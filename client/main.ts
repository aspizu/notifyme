import { app } from "./app.js"
import * as gtk from "./gtk.js"
import * as api from "./api.js"
import { Input, PasswordInput } from "./widgets/input.js"
import { TagPicker } from "./widgets/tagpicker.js"
import { Popover } from "./widgets/popover.js"
import { Dialog } from "./widgets/dialog.js"
import { relativeToNow } from "./time.js"

const emojis: { [index: string]: string } = {
  0: "❤️",
  1: "😍",
}

function getAvatar(avatar_url: string | null, username: string) {
  return avatar_url ? avatar_url : `https://ui-avatars.com/api?name=${username}`
}

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

function isDisplayNameValid(displayName: string) {
  if (displayName.length <= 0) {
    return "Display name cannot be empty."
  }
  if (displayName.length > 256) {
    return "Display name too long."
  }
}

async function login() {
  document.title = "notifyme - Log in"
  function onInvalid(isValid: boolean) {
    if (isValid && passwordInput.isValid()) {
      button.disabled = false
    } else {
      button.disabled = true
    }
  }
  const usernameInput = new Input(isUsernameValid, onInvalid)
  const passwordInput = new PasswordInput(isPasswordValid, onInvalid)
  const button = gtk.newButton("Login", {
    cls: "button-primary",
    onclick: async () => {
      if (!usernameInput.isValid()) {
        usernameInput.input.focus()
        return
      }
      if (!passwordInput.isValid()) {
        passwordInput.input.focus()
        return
      }
      try {
        await api.login(usernameInput.input.value, passwordInput.input.value)
      } catch (err: any) {
        passwordInput.setError(err.message)
        passwordInput.input.focus()
      }
      app.username = usernameInput.input.value
      app.save()
      window.location.href = "/"
    },
  })
  app.replaceChildren(
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

function logout() {
  const dialog = new Dialog(
    { cls: "dialog pad-1 gap-1" },
    gtk.newSpan("Are you sure you want to log out?"),
    gtk.newRow(
      { cls: "gap-1" },
      gtk.newButton("Log out", {
        cls: "button-destructive",
        onclick: async () => {
          await api.logout()
          window.location.href = "/"
        },
      }),
      gtk.newButton("Cancel", {
        cls: "button",
        onclick: () => {
          dialog.div.remove()
        },
      }),
    ),
  )
  document.body.append(dialog.div)
}

function headerBar() {
  return gtk.newRow(
    { cls: "header-bar vert-center pad-0 gap-0" },
    gtk.newButton(gtk.icon("home"), {
      cls: "clear-icon-button",
      onclick: () => {
        window.location.href = "/"
      },
    }),
    gtk.newSpan("notifyme", { cls: "mar-left-auto mar-right-auto large bold" }),
    gtk.newButton(gtk.icon("options"), {
      cls: "clear-icon-button",
      onclick: (event: MouseEvent) => {
        app.popover(
          new Popover(
            event.clientX,
            event.clientY,
            gtk.newColumn(
              { cls: "menu" },
              ...(app.user.permission > 0
                ? [
                    gtk.newButton("Create new post", {
                      cls: "menu-button",
                      onclick: () => {
                        const submitBtn = gtk.newButton("Create", {
                          cls: "button-primary",
                          disabled: true,
                          onclick: async () => {
                            await api.newPost(
                              contentInput.input.value,
                              tagPicker.tags,
                              recipientsPicker.tags,
                            )
                            dialog.div.remove()
                          },
                        })
                        const contentInput = new Input(
                          (content: string) => {
                            if (content.length < 1) {
                              return "Content shouldn't be empty."
                            }
                          },
                          (valid) => {
                            submitBtn.disabled = !valid
                          },
                        )
                        const tagPicker = new TagPicker([], (tag) => {
                          if (tag.length < 0) {
                            return "Tag shouldn't be empty."
                          }
                        })
                        const recipientsPicker = new TagPicker([], (recpient) => {
                          if (recpient.length < 0) {
                            return "Username shouldn't be empty."
                          }
                        })
                        const dialog = new Dialog(
                          { cls: "dialog pad-1 gap-1" },
                          gtk.newSpan("Create new post", { cls: "large" }),
                          gtk.newSpan("Tags:"),
                          tagPicker,
                          gtk.newSpan("Recipients:"),
                          recipientsPicker,
                          contentInput,
                          gtk.newRow(
                            { cls: "gap-1" },
                            submitBtn,
                            gtk.newButton("Cancel", {
                              cls: "button",
                              onclick: () => {
                                dialog.div.remove()
                              },
                            }),
                          ),
                        )
                        document.body.append(dialog.div)
                        app.removePopover()
                      },
                    }),
                  ]
                : []),
              gtk.newButton("View profile", {
                cls: "menu-button",
                onclick: () => {
                  window.location.href = "/user/" + app.username
                  app.removePopover()
                },
              }),
              gtk.newButton("Account settings", {
                cls: "menu-button",
                onclick: () => {
                  window.location.href = "/accountSettings"
                  app.removePopover()
                },
              }),
              gtk.newButton("Log out", {
                cls: "menu-button",
                onclick: () => {
                  logout()
                  app.removePopover()
                },
              }),
            ),
          ),
        )
      },
    }),
  )
}

async function userProfile(username: string) {
  document.title = "notifyme - " + username
  const user = await api.getUser(username)
  return gtk.newColumn(
    { cls: "pad-1 gap-1" },
    gtk.newRow(
      { cls: "vert-center gap-1" },
      gtk.newElement("img", {
        cls: "round",
        width: 32,
        src: getAvatar(user.avatar_url, user.username),
      }),
      gtk.newColumn(
        {},
        gtk.newSpan("@" + user.username),
        gtk.newSpan(user.display_name, { cls: "large bold" }),
      ),
    ),
    gtk.newRow(
      { cls: "gap-1" },
      ...user.tags.map((tag) => gtk.newSpan(tag, { cls: "TagPicker__tag pad-0" })),
    ),
  )
}

async function accountSettings() {
  document.title = "notifyme - Account Settings"
  const user = await api.getUser(app.username)

  const displayNameInput = new Input(isDisplayNameValid, undefined, {
    value: user.display_name,
  })
  displayNameInput.div.classList.add("grow")
  const avatarInput = new Input(
    () => undefined,
    () => {
      avatarImg.src = getAvatar(
        avatarInput.input.value == "" ? null : avatarInput.input.value,
        user.username,
      )
    },
    {
      value: user.avatar_url ? user.avatar_url : "",
      placeholder: "Enter avatar URL",
    },
  )
  avatarInput.div.classList.add("grow")
  const avatarImg = gtk.newElement("img", {
    src: getAvatar(user.avatar_url, user.username),
    width: 80,
    height: 80,
  })
  const avatarInputBox = gtk.newRow(
    { cls: "gap-1" },
    avatarImg,
    gtk.newColumn(
      { cls: "grow" },
      gtk.newRow(
        { cls: "grow gap-1" },
        avatarInput,
        gtk.newButton("Undo", {
          cls: "button-primary",
          onclick: () => {
            avatarInput.input.value = user.avatar_url ? user.avatar_url : ""
            avatarInput.isValid()
          },
        }),
      ),
    ),
  )

  const tagsPicker = new TagPicker(user.tags, () => undefined)

  const updateButton = gtk.newButton("Update", {
    cls: "button-primary",
    onclick: async () => {
      try {
        await api.editProfile({
          displayName: displayNameInput.input.value,
          avatarUrl: avatarInput.input.value,
          tags: tagsPicker.tags,
        })
        alert("Profile updated successfully")
      } catch (error) {
        console.error(error)
        alert("An error occurred while updating your profile")
      }
    },
  })

  app.replaceChildren(
    headerBar(),
    gtk.newColumn(
      { cls: "pad-1 gap-1" },
      gtk.newSpan("Account Settings", { cls: "large" }),
      gtk.newColumn(
        { cls: "surface pad-1 gap-1" },
        gtk.newSpan("Display Name: ", { cls: "bold" }),
        gtk.newRow(
          { cls: "gap-1" },
          displayNameInput,
          gtk.newButton("Undo", {
            cls: "button-primary",
            onclick: () => {
              displayNameInput.input.value = user.display_name
            },
          }),
        ),
        gtk.newSpan("Avatar: ", { cls: "bold" }),
        avatarInputBox,
        gtk.newSpan("Tags: ", { cls: "bold" }),
        tagsPicker,
        gtk.newRow({ cls: "gap-1" }, updateButton),
      ),
    ),
  )
}

function newPost(post: api.Post) {
  const avatar: HTMLImageElement = gtk.newElement("img", {
    cls: "round",
    src: getAvatar(post.author.avatar_url, post.author.username),
    width: 32,
    height: 32,
  })
  const username = gtk.newElement("a", {
    cls: "small",
    css: "padding-bottom: 4px",
    text: "@" + post.author.username,
    href: `/user/${post.author.username}`,
  })
  const displayName = gtk.newSpan(post.author.display_name, { cls: "bold" })
  const content = gtk.newSpan(post.content)
  const reactions = gtk.newRow(
    { cls: "gap-1" },
    ...Object.entries(post.reactions).map(([emoji_idx, [count, isReacted]]) =>
      gtk.newButton(
        emojis[emoji_idx],
        { cls: isReacted ? "button" : "clear-icon-button" },
        gtk.newSpan(count.toString()),
      ),
    ),
  )
  const container = gtk.newColumn(
    { cls: "surface pad-1 gap-1" },
    gtk.newRow(
      { cls: "vert-center gap-1" },
      avatar,
      gtk.newColumn({}, username, displayName),
      ...(post.recipients.includes(post.author.username)
        ? [gtk.newSpan("For you", { cls: "ForYou pad-0" })]
        : []),
      gtk.newFlexDivider(),
      gtk.newSpan(relativeToNow(post.created_time), { cls: "small" }),
      ...(post.author.username == app.username
        ? [
            gtk.newButton(gtk.icon("options"), {
              cls: "clear-icon-button",
              onclick: (event: MouseEvent) => {
                app.popover(
                  new Popover(
                    event.clientX,
                    event.clientY,
                    gtk.newColumn(
                      { cls: "menu" },
                      gtk.newButton("Edit", {
                        cls: "menu-button",
                        onclick: () => {
                          const submitBtn = gtk.newButton("Edit", {
                            cls: "button-primary",
                            onclick: async () => {
                              await api.editPost(post.id, {
                                content: contentInput.input.value,
                                tags: tagPicker.tags,
                                recipients: recipientsPicker.tags,
                              })
                              content.textContent = contentInput.input.value
                              dialog.div.remove()
                            },
                          })
                          const contentInput = new Input(
                            (content: string) => {
                              if (content.length < 1) {
                                return "Content shouldn't be empty."
                              }
                            },
                            (valid) => {
                              submitBtn.disabled = !valid
                            },
                            { value: post.content },
                          )
                          const tagPicker = new TagPicker(post.tags, (tag) => {
                            if (tag.length < 0) {
                              return "Tag shouldn't be empty."
                            }
                          })
                          const recipientsPicker = new TagPicker(
                            post.recipients,
                            (recpient) => {
                              if (recpient.length < 0) {
                                return "Username shouldn't be empty."
                              }
                            },
                          )
                          const dialog = new Dialog(
                            { cls: "dialog pad-1 gap-1" },
                            gtk.newSpan("Edit post", { cls: "large" }),
                            gtk.newSpan("Tags:"),
                            tagPicker,
                            gtk.newSpan("Recipients:"),
                            recipientsPicker,
                            contentInput,
                            gtk.newRow(
                              { cls: "gap-1" },
                              submitBtn,
                              gtk.newButton("Cancel", {
                                cls: "button",
                                onclick: () => {
                                  dialog.div.remove()
                                },
                              }),
                            ),
                          )
                          document.body.append(dialog.div)
                          app.removePopover()
                        },
                      }),
                      gtk.newButton("Delete", {
                        cls: "menu-button",
                        onclick: () => {
                          const dialog = new Dialog(
                            {},
                            gtk.newColumn(
                              { cls: "dialog gap-1 pad-1" },
                              gtk.newSpan("Are you sure you want to delete this post?"),
                              gtk.newColumn(
                                { cls: "surface pad-1 gap-1" },
                                gtk.newSpan(post.content),
                              ),
                              gtk.newRow(
                                { cls: "gap-1" },
                                gtk.newButton("Delete", {
                                  cls: "button-destructive",
                                  onclick: () => {
                                    api.deletePost(post.id)
                                    dialog.div.remove()
                                    container.remove()
                                  },
                                }),
                                gtk.newButton("Cancel", {
                                  cls: "button",
                                  onclick: () => {
                                    dialog.div.remove()
                                  },
                                }),
                              ),
                            ),
                          )
                          document.body.append(dialog.div)
                          app.removePopover()
                        },
                      }),
                    ),
                  ),
                )
              },
            }),
          ]
        : []),
    ),
    ...(post.tags.length != 0
      ? [
          gtk.newRow(
            { cls: "gap-1" },
            ...post.tags.map((tag) =>
              gtk.newSpan(tag, { cls: "TagPicker__tag pad-0" }),
            ),
          ),
        ]
      : []),
    content,
    reactions,
  )
  return container
}

async function homepage() {
  document.title = "notifyme - Home"
  const posts = await api.getPosts()
  app.replaceChildren(
    headerBar(),
    gtk.newColumn({ cls: "pad-1 gap-1" }, ...posts.map(newPost)),
  )
}

async function loadView() {
  const path = window.location.pathname.split("/")
  if (path.length == 2 && path[1] == "login") {
    if (await api.isLoggedIn()) {
      window.location.href = "/"
      return
    }
    await login()
    return
  } else if (!(await api.isLoggedIn())) {
    window.location.href = "/login"
    return
  }
  if (path.length == 2 && path[1] == "accountSettings") {
    await accountSettings()
    return
  }
  if (path.length == 3 && path[1] == "user") {
    app.replaceChildren(headerBar(), await userProfile(path[2]))
    return
  }
  await homepage()
  return
}

await app.load()
await loadView()
