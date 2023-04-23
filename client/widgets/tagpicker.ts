import * as gtk from "../gtk.js"
import { app } from "../app.js"
import { Popover } from "./popover.js"
import { Input } from "./input.js"

export class TagPicker extends gtk.Widget {
  validatorFunction: (value: string) => string | undefined
  tags: string[]
  constructor(
    tags: string[],
    validatorFunction: (value: string) => string | undefined,
  ) {
    super({ cls: "TagPicker row gap-1" })
    this.validatorFunction = validatorFunction
    this.tags = tags
    this.render()
  }

  render() {
    this.div.replaceChildren(
      ...this.tags.map((tag) =>
        gtk.newDiv(
          { cls: "TagPicker__tag vert-center row gap-0 pad-0" },
          gtk.newSpan(tag),
          gtk.newButton("❌", {
            cls: "button-clear",
            onclick: () => {
              this.removeTag(tag)
            },
          }),
        ),
      ),
      gtk.newButton(gtk.icon("add"), {
        cls: "button",
        onclick: (event: MouseEvent) => {
          this.addTag(event)
        },
      }),
    )
  }

  addTag(event: MouseEvent) {
    const input = new Input(this.validatorFunction)
    app.popover(
      new Popover(
        event.clientX,
        event.clientY,
        gtk.newDiv(
          { cls: "column surface pad-1 gap-1" },
          input,
          gtk.newRow(
            { cls: "gap-1" },
            gtk.newButton("Add", {
              cls: "button-primary",
              onclick: () => {
                this.tags.push(input.input.value)
                this.render()
                app.removePopover()
              },
            }),
            gtk.newButton("Cancel", {
              cls: "button",
              onclick: () => {
                app.removePopover()
              },
            }),
          ),
        ),
      ),
    )
  }

  removeTag(tag: string) {
    this.tags.splice(this.tags.indexOf(tag), 1)
    this.render()
  }
}
