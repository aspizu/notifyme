import ast
import sys
from typing import IO, Any, Callable


class BaseWriter:
    extension: str
    """The file extension used for the output files (For example: ".md")"""

    class WithIndent:
        def __init__(
            self,
            writer: "BaseWriter",
            enter_callback: Callable[[], None],
            leave_callback: Callable[[], None],
        ):
            """
            Args:
              enter_callback: Function to be called before indenting.
              leave_callback: Function to be called after dedenting.
            """
            self.enter_callback = enter_callback
            """Function to be called before indenting."""
            self.leave_callback = leave_callback
            """Function to be called after dedenting."""
            self.writer = writer

        def __enter__(self):
            self.enter_callback()
            self.writer.indent_level += 1

        def __exit__(self, *args: Any):
            self.writer.indent_level -= 1
            self.leave_callback()

    def __init__(self, node: ast.Module, file: IO[str], indent_width: int = 4):
        self.file = file
        """Output file the documentation is rendered into."""
        self.indent_level = 0
        """Current level of indentation."""
        self.indent_width = indent_width
        """The number of spaces to use for each level of indentation."""
        self.module(node)

    def write(self, string: str) -> None:
        """
        Write a string into the output file. The current indentation level will be
        inserted after each newline character in the string.
        """
        indentation = self.indent_level * self.indent_width * " "
        string = string.replace("\n", "\n" + indentation)
        self.file.write(string)

    def writeln(self, string: str) -> None:
        """
        Write a line into the output file. The current indentation level will be
        inserted before the line and after each newline character. A newline character
        will be appended to the end of the line.
        """
        indentation = self.indent_level * self.indent_width * " "
        string = string.replace("\n", "\n" + indentation)
        self.file.write(indentation + string + "\n")

    def indent(
        self,
        enter_callback: Callable[[], None] = (lambda: None),
        leave_callback: Callable[[], None] = (lambda: None),
    ):
        """Returns a `BaseWriter.WithIndent` object to be used in a `with` statement.

        Args:
          enter_callback: Function to be called before indenting.
          leave_callback: Function to be called after dedenting.
        """
        return BaseWriter.WithIndent(self, enter_callback, leave_callback)

    def module(self, module: ast.Module) -> None:
        ...


class Writer(BaseWriter):
    def post_endpoint(self, name: str, path: str, parameters: list[str]):
        body = (
            "{ "
            + ", ".join(f"{parameter}: {parameter}" for parameter in parameters)
            + " }"
        )
        self.writeln(f"async function {name}({', '.join(parameters)}) {{")
        with self.indent():
            self.writeln(f"return await (await fetch({path!r}, {{")
            with self.indent():
                self.writeln('method: "POST",')
                self.writeln(f"body: JSON.stringify({body}),")
            self.writeln("})).json();")
        self.writeln("}\n")

    def module(self, module: ast.Module) -> None:
        for node in ast.walk(module):
            if isinstance(node, ast.FunctionDef):
                self.function(node)

    def function(self, function: ast.FunctionDef) -> None:
        name = function.name
        if not len(function.decorator_list) == 1:
            return
        decorator = function.decorator_list[0]
        if not isinstance(decorator, ast.Call):
            return
        attribute = decorator.func
        if not isinstance(attribute, ast.Attribute):
            return
        if not attribute.attr == "POST":
            return
        path_arg: ast.Constant = decorator.args[0]  # type: ignore
        path: str = path_arg.value
        parameters: list[str] = [
            arg.arg
            for arg in function.args.args
            if arg.arg not in ("request", "session")
        ]
        self.post_endpoint(name, path, parameters)


Writer(ast.parse(open("notifyme/user.py").read()), sys.stderr, 2)
