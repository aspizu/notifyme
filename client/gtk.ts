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
  child: HTMLElement | string | Promise<HTMLElement>,
  params: ElementParams = {},
  ...children: ElementChildren
) {
  const button: HTMLButtonElement = newElement("button", params, ...children)
  if (child instanceof Promise)
    child.then((value) => {
      button.append(value)
    })
  else button.append(child)
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

  replaceChildren(...children: ElementChildren) {
    this.div.replaceChildren()
    this.append(...children)
  }

  onrender(parent: HTMLElement | Widget) {}
}

export async function svg(url: string) {
  const response = await fetch(url)
  const svgData = await response.text()
  const parser = new DOMParser()
  const svgDoc = parser.parseFromString(svgData, "image/svg+xml")
  return svgDoc.documentElement
}

export async function icon(name: string) {
  const element = await svg(`/static/icons/${name}.svg`)
  element.classList.add("icon")
  return element
}
