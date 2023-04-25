import * as gtk from "./gtk.js"
import { Popover } from "./widgets/popover.js"
import { Dialog } from "./widgets/dialog.js"
import { getCookie, setCookie } from "./cookie.js"
import { User, getUser } from "./api.js"

export class App extends gtk.Widget {
  activePopover: Popover | undefined
  activeDialogs: Dialog[] = []
  username: string
  user!: User

  constructor() {
    super({ cls: "column vert-expand" })
    this.username = ""
    window.addEventListener("mousedown", (event) => {
      if (this.activePopover) {
        const popoverRect = this.activePopover.div.getBoundingClientRect()
        const isInsidePopover =
          event.clientX >= popoverRect.left &&
          event.clientX <= popoverRect.right &&
          event.clientY >= popoverRect.top &&
          event.clientY <= popoverRect.bottom
        if (!isInsidePopover) {
          app.removePopover()
        }
      }
    })
  }

  popover(popover: Popover) {
    if (this.activePopover) {
      app.removePopover()
    }
    this.activePopover = popover
    document.body.append(popover.div)
    popover.onrender(document.body)
  }

  removePopover() {
    if (this.activePopover) {
      this.activePopover.remove(() => {
        this.activePopover = undefined
      })
    }
  }

  save() {
    setCookie("username", this.username)
  }

  async load() {
    this.username = getCookie("username")
    try {
      if (this.username != "") this.user = await getUser(this.username)
    } catch (err) {}
  }
}

export const app = new App()
document.body.append(app.div)
