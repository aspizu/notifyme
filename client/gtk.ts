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
  if (params.cls) element.classList.add(...params.cls.split(' '))
  if (params.text) element.innerText = params.text
  if (params.css) element.style.cssText = params.css
  for (const [name, value] of Object.entries(params)) {
    if (['cls', 'text', 'css'].includes(name)) continue
    /* @ts-ignore */
    element[name] = value
  }
  element.append(
    ...children.map((child) => (child instanceof Widget ? child.div : child))
  )
  return element
}

export function newDiv(
  params: ElementParams = {},
  ...children: ElementChildren
): HTMLDivElement {
  return newElement('div', params, ...children)
}

export function newSpan(
  params: ElementParams = {},
  ...children: ElementChildren
): HTMLSpanElement {
  return newElement('span', params, ...children)
}

export class Widget {
  div: HTMLDivElement

  constructor(params: ElementParams = {}, ...children: ElementChildren) {
    this.div = newDiv(params, ...children)
  }
}
