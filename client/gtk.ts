export type ElementParams = {
  cls?: string
  text?: string
  css?: string
  [index: string]: any
}

export type ElementChildren = (HTMLElement | Widget)[]

export function newElement(
  tagName: string,
  params: ElementParams = {},
  ...children: ElementChildren
): any {
  const element = document.createElement(tagName)
  if (params.cls) element.classList.add(...params.cls.split(" "))
  if (params.text) element.innerText = params.text
  if (params.css) element.style.cssText = params.css
  for (const [name, value] of Object.entries(params)) {
    if (["cls", "text", "css"].includes(name)) continue
    /* @ts-ignore */
    element[name] = value
  }
  for (const child of children) {
    if (child instanceof Widget) {
      element.append(child.div)
      child.onrender(element)
    } else {
      element.append(child)
    }
  }
  return element
}

export function newDiv(
  params: ElementParams = {},
  ...children: ElementChildren
): HTMLDivElement {
  return newElement("div", params, ...children)
}

export function newRow(params: ElementParams = {}, ...children: ElementChildren) {
  const div = newDiv(params, ...children)
  div.classList.add("row")
  return div
}

export function newColumn(params: ElementParams = {}, ...children: ElementChildren) {
  const div = newDiv(params, ...children)
  div.classList.add("column")
  return div
}

export function newSpan(
  text: string,
  params: ElementParams = {},
  ...children: ElementChildren
): HTMLSpanElement {
  params.text = text
  const span: HTMLSpanElement = newElement("span", params, ...children)
  return span
}

export function newButton(
  text: string,
  params: ElementParams = {},
  ...children: ElementChildren
) {
  params.text = text
  const button: HTMLButtonElement = newElement("button", params, ...children)
  return button
}

export function newFlexDivider() {
  return newDiv({ cls: "mar-right-auto" })
}

export class Widget {
  div: HTMLDivElement

  constructor(params: ElementParams = {}, ...children: ElementChildren) {
    this.div = newDiv(params, ...children)
    if (params.then) params.then(this)
  }

  append(...children: ElementChildren) {
    for (const child of children) {
      if (child instanceof Widget) {
        this.div.append(child.div)
        this.onrender(this)
      } else {
        this.div.append(child)
      }
    }
  }

  replace(...children: ElementChildren) {
    this.div.replaceChildren()
    this.append(...children)
  }

  onrender(parent: HTMLElement | Widget) {}
}
