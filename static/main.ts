type ElementParams = {
  cls?: string
  text?: string
  css?: string
  [index: string]: any
}

function newElement(
  tagName: string,
  params: ElementParams = {},
  ...children: (HTMLElement | Widget)[]
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

function newDiv(
  params: ElementParams = {},
  ...children: HTMLElement[]
): HTMLDivElement {
  return newElement('div', params, ...children)
}

function newSpan(
  params: ElementParams = {},
  ...children: HTMLElement[]
): HTMLSpanElement {
  return newElement('span', params, ...children)
}

class Widget {
  div: HTMLDivElement

  constructor(params: ElementParams = {}, ...children: HTMLElement[]) {
    this.div = newDiv(params, ...children)
  }
}

document.body.append(
  newDiv(
    {},
    newSpan({ text: 'Username' }),
    newElement('input', { type: 'text' })
  )
)
