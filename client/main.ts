import * as gtk from "./gtk.js"
import * as api from "./api.js"
import * as time from "./time.js"
import { deleteCookie, getCookie, setCookie } from "./cookie.js"

const REACTION_EMOJIS: { [index: string]: string } = {
  1: "❤️",
}

class Main {
  view: HTMLDivElement | undefined
  user!: api.User

  constructor() {
    this.login().then(async () => {
      this.showDialog(loginDialog())
      /* this.setView(await mainView()) */
    })
  }

  async login() {
    if (!(await api.isLoggedIn())) {
      await api.login("aspizu", "br000tal")
      setCookie("username", "aspizu")
      await this.login()
      return
    } else {
      const username = getCookie("username")
      if (!username) {
        deleteCookie("token")
        await this.login()
        return
      }
      this.user = await api.getUser(username)
    }
  }

  setView(view: HTMLDivElement) {
    if (this.view) {
      this.view.remove()
    }
    this.view = view
    document.body.append(view)
  }

  showDialog(dialog: HTMLDivElement) {
    document.body.append(gtk.newDiv({ cls: "dialog-container" }, dialog))
  }
}

const main = new Main()

function newPost({ author, content, created_time, reactions }: api.Post) {
  return gtk.newDiv(
    { cls: "post" },
    gtk.newDiv(
      { cls: "post-author" },
      gtk.newElement("img", {
        cls: "post-author-avatar",
        src:
          author.avatar_url != null
            ? author.avatar_url
            : `https://ui-avatars.com/api?size=32&name=${main.user.username}`,
      }),
      gtk.newSpan({
        cls: "post-author-username",
        text: author.username,
      }),
      gtk.newSpan({
        cls: "post-created_time",
        text: time.relativeToNow(created_time),
      }),
    ),
    gtk.newSpan({ cls: "post-content", text: content }),
    gtk.newDiv(
      { cls: "reactions" },
      ...Object.entries(reactions).map(([emoji, count]) =>
        gtk.newDiv(
          { cls: "reaction" },
          gtk.newSpan({ cls: "reaction-emoji", text: REACTION_EMOJIS[emoji] }),
          gtk.newSpan({ cls: "reaction-count", text: count.toString() }),
        ),
      ),
    ),
  )
}

async function mainView() {
  const posts = gtk.newDiv(
    { cls: "posts" },
    ...(await api.getPosts()).map((post) => newPost(post)),
  )
  const header = gtk.newDiv(
    { cls: "header" },
    gtk.newDiv(
      { cls: "user-profile" },
      gtk.newElement("img", {
        cls: "user-profile-avatar",
        src:
          main.user.avatar_url != null
            ? main.user.avatar_url
            : `https://ui-avatars.com/api?size=32&name=${main.user.username}`,
      }),
      gtk.newSpan({ text: main.user.username }),
    ),
    gtk.newDiv(
      { cls: "user-options" },
      gtk.newElement("button", { text: "New post" }),
      gtk.newElement("button", { text: "Account settings" }),
      gtk.newElement("button", { text: "Log out" }),
    ),
  )
  return gtk.newDiv({ cls: "column" }, header, posts)
}

async function loginDialog() {
  return gtk.newDiv({ cls: "dialog" })
}
