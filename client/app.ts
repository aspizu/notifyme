import * as gtk from "./gtk.js"
import * as api from "./api.js"
import { Popover } from "./widgets/popover.js"
import { Dialog } from "./widgets/dialog.js"
import { Input, PasswordInput } from "./widgets/input.js"

function isUsernameValid(username: string) {
  if (username.length < 4) {
    return "Username is too short."
  }
  if (username.length > 32) {
    return "Username is too long."
  }
  if (!/^[a-zA-Z0-9]+$/.test(username)) {
    return "Username can only contain letters and numbers"
  }
}

function isPasswordValid(password: string) {
  if (password.length < 8) {
    return "Password is too short."
  }
}

export class App extends gtk.Widget {
  activePopover: Popover | undefined
  activeDialogs: Dialog[] = []

  constructor() {
    super({ cls: "column vert-expand" })
    window.addEventListener("mousedown", (event) => {
      if (this.activePopover) {
        const popoverRect = this.activePopover.div.getBoundingClientRect()
        const isInsidePopover =
          event.clientX >= popoverRect.left &&
          event.clientX <= popoverRect.right &&
          event.clientY >= popoverRect.top &&
          event.clientY <= popoverRect.bottom
        if (!isInsidePopover) {
          this.activePopover.div.remove()
          this.activePopover = undefined
        }
      }
    })
  }

  popover(popover: Popover) {
    if (this.activePopover) {
      this.activePopover.div.remove()
    }
    this.activePopover = popover
    document.body.append(popover.div)
    popover.onrender(document.body)
  }

  main() {
    document.title = "notifyme"
    function onInvalid() {
      if (usernameInput.isValid() && passwordInput.isValid()) {
        button.classList.remove("disabled")
      } else {
        button.classList.add("disabled")
      }
    }
    const usernameInput = new Input(isUsernameValid, onInvalid)
    const passwordInput = new PasswordInput(isPasswordValid, onInvalid)
    const button = gtk.newButton("Login", {
      cls: "button-primary disabled",
      onclick: async () => {
        if (!(usernameInput.isValid() || passwordInput.isValid)) {
          return
        }
      },
    })
    this.replace(
      gtk.newColumn(
        { cls: "vert-center horiz-center vert-expand" },
        gtk.newColumn(
          { cls: "surface gap-1 pad-1", css: "min-width: 90%" },
          gtk.newSpan("Username"),
          usernameInput,
          gtk.newSpan("Password"),
          passwordInput,
          button,
        ),
      ),
    )
  }
}

export const app = new App()
document.body.append(app.div)
