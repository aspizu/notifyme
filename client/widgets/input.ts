import * as gtk from "../gtk.js"

export class Input extends gtk.Widget {
  input: HTMLInputElement
  tooltip: HTMLDivElement
  validatorFunction: (value: string) => string | undefined
  onInvalid: (isValid: boolean) => void

  constructor(
    validatorFunction: (value: string) => string | undefined,
    onInvalid: (isValid: boolean) => void = (isValid: boolean) => undefined,
    params: gtk.ElementParams = {},
  ) {
    super({ cls: "tooltip-container" })
    this.input = gtk.newElement("input", { cls: "input", type: "text", ...params })
    this.tooltip = gtk.newDiv({ cls: "tooltip-destructive hidden" })
    this.validatorFunction = validatorFunction
    this.onInvalid = onInvalid
    this.input.addEventListener("input", () => {
      this.isValid()
    })
    this.div.append(this.input, this.tooltip)
  }

  isValid() {
    const error = this.validatorFunction(this.input.value)
    if (error) {
      this.setError(error)
      this.onInvalid(false)
      return false
    } else {
      this.tooltip.classList.add("hidden")
      this.input.classList.remove("error")
      this.onInvalid(true)
      return true
    }
  }

  setError(message: string) {
    this.tooltip.classList.remove("hidden")
    this.tooltip.textContent = message
    this.input.classList.add("error")
  }
}

export class PasswordInput extends gtk.Widget {
  container: HTMLDivElement
  input: HTMLInputElement
  tooltip: HTMLDivElement
  visibilityButton: HTMLButtonElement
  validatorFunction: (value: string) => string | undefined

  constructor(
    validatorFunction: (value: string) => string | undefined,
    onInvalid: (isValid: boolean) => void = (isValid: boolean) => undefined,
  ) {
    super({ cls: "tooltip-container" })
    this.input = gtk.newElement("input", { type: "password" })
    this.tooltip = gtk.newDiv({ cls: "tooltip-destructive hidden" })
    this.visibilityButton = gtk.newElement("button", {
      cls: "button-clear",
      text: "SHOW",
      onclick: () => {
        if (this.input.type == "text") {
          this.input.type = "password"
          this.visibilityButton.textContent = "SHOW"
        } else {
          this.input.type = "text"
          this.visibilityButton.textContent = "HIDE"
        }
      },
    })
    this.container = gtk.newRow({ cls: "input" }, this.input, this.visibilityButton)
    this.validatorFunction = validatorFunction
    this.input.addEventListener("input", () => {
      onInvalid(this.isValid())
    })
    this.div.append(this.container, this.tooltip)
  }

  isValid() {
    const error = this.validatorFunction(this.input.value)
    if (error) {
      this.setError(error)
      return false
    } else {
      this.tooltip.classList.add("hidden")
      this.container.classList.remove("error")
      return true
    }
  }

  setError(message: string) {
    this.tooltip.classList.remove("hidden")
    this.tooltip.textContent = message
    this.container.classList.add("error")
  }
}
