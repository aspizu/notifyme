export function setCookie(name: string, val: string) {
  const date = new Date()
  const value = val
  date.setTime(date.getTime() + 7 * 24 * 60 * 60 * 1000) /* 7 Days */
  document.cookie =
    name +
    '=' +
    value +
    '; expires=' +
    date.toUTCString() +
    '; path=/; SameSite=Strict;'
}

export function getCookie(name: string) {
  const parts = ('; ' + document.cookie).split('; ' + name + '=')
  if (parts.length == 2) {
    // @ts-ignore
    return parts.pop().split(';').shift()
  }
}

export function deleteCookie(name: string) {
  const date = new Date()
  // Set it expire in -1 days
  date.setTime(date.getTime() + -1 * 24 * 60 * 60 * 1000)
  document.cookie = name + '=; expires=' + date.toUTCString() + '; path=/'
}
