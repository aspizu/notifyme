import * as gtk from "../gtk.js"

export class Dialog extends gtk.Widget {
  dialog: HTMLDivElement

  constructor(params: gtk.ElementParams = {}, ...children: gtk.ElementChildren) {
    super()
    this.div.classList.add("dialog-container")
    this.dialog = gtk.newColumn(params, ...children)
    this.div.append(this.dialog)
  }
}
