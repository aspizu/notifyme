import * as gtk from "../gtk.js"

export class Popover extends gtk.Widget {
  x: number
  y: number
  constructor(x: number, y: number, child: HTMLElement | gtk.Widget) {
    super({ cls: "popover" }, child)
    this.x = x
    this.y = y
  }

  onrender(parent: HTMLElement | gtk.Widget) {
    const childRect = this.div.getBoundingClientRect()
    let x = this.x - childRect.width / 2
    if (x + childRect.width >= window.innerWidth) {
      x = window.innerWidth - childRect.width
    }
    if (x < 0) {
      x = 0
    }
    this.div.style.left = x + "px"
    this.div.style.top = this.y + "px"
  }
}
