import { getCookie, setCookie } from "./cookie.js"

export type User = {
  id: number
  username: string
  display_name: string
  avatar_url: string | null
  tags: string[]
  permission: number
  created_time: number
}

export type Post = {
  id: number
  author: User
  content: string
  tags: string[]
  recipients: string[]
  created_time: number
  reactions: { [index: number]: [number, boolean] }
}

export async function post(url: string, body: any = {}) {
  const response = await (
    await fetch(url, { method: "POST", body: JSON.stringify(body) })
  ).json()
  if (!response.success) {
    throw new Error(response.error)
  }
  return response
}

export async function get(url: string, body: any = {}) {
  const response = await (
    await fetch(url + "?" + new URLSearchParams(body), { method: "GET" })
  ).json()
  if (!response.success) {
    throw new Error(response.error)
  }
  return response
}

export async function login(username: string, password: string) {
  const token: string = (
    await post("/api/login", { username: username, password: password })
  ).token
  setCookie("username", username)
  setCookie("token", token)
}

export async function register(
  username: string,
  displayName: string,
  password: string,
): Promise<number> {
  return (
    await post("/api/register", {
      username: username,
      display_name: displayName,
      password: password,
    })
  ).id
}

export async function changePassword(oldPassword: string, newPassword: string) {
  await post("/api/change_password", {
    username: getCookie("username"),
    old_password: oldPassword,
    new_password: newPassword,
  })
}

type editProfileOptions = {
  displayName?: string
  avatarUrl?: string
  tags?: string[]
}

export async function editProfile({
  displayName,
  avatarUrl,
  tags,
}: editProfileOptions = {}) {
  await post("/api/edit_profile", {
    display_name: displayName ? displayName != undefined : null,
    avatar_url: avatarUrl ? avatarUrl != undefined : null,
    tags: tags ? tags != undefined : null,
  })
}

export async function checkSession() {
  await get("/api/check_session")
}

export async function isLoggedIn() {
  try {
    await checkSession()
    return true
  } catch {
    return false
  }
}

export async function getUser(username: string): Promise<User> {
  return await get("/api/get_user", { username: username })
}

export async function deleteUser(password: string) {
  await post("/api/delete_user", {
    username: getCookie("username"),
    password: password,
  })
}

export async function getPost(id: number): Promise<Post> {
  return await get("/api/get_post", { id: id })
}

export async function getPosts(): Promise<Post[]> {
  return (await get("/api/get_posts")).posts
}

export async function newPost(
  content: string,
  tags: string[],
  recipients: string[],
): Promise<number> {
  return (
    await post("/api/new_post", {
      content: content,
      tags: tags,
      recipients: recipients,
    })
  ).id
}

type editPostOptions = {
  content?: string
  tags?: string[]
  recipients?: string[]
}

export async function editPost(
  id: number,
  { content, tags, recipients }: editPostOptions = {},
) {
  await post("/api/edit_post", {
    id: id,
    content: content ? content != undefined : null,
    tags: tags ? tags != undefined : null,
    recipients: recipients ? recipients != undefined : null,
  })
}

export async function deletePost(id: number) {
  await post("/api/delete_post", { id: id })
}

export async function addReaction(postId: number, emoji: number) {
  await post("/api/add_reaction", { post_id: postId, emoji: emoji })
}

export async function removeReaction(postId: number, emoji: number) {
  await post("/api/remove_reaction", { post_id: postId, emoji: emoji })
}
