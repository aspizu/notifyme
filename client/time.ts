export function dateFromTimestamp(timestamp: number) {
  const date = new Date(0)
  date.setUTCSeconds(timestamp)
  return date
}

const SECONDS_IN_MINUTE = 60
const SECONDS_IN_HOUR = 3600
const SECONDS_IN_DAY = 86400
const SECONDS_IN_WEEK = 604800
const SECONDS_IN_MONTH = 2592000
const SECONDS_IN_YEAR = 31536000

export function relativeToNow(timestamp: number): string {
  const now = Math.floor(Date.now() / 1000)
  const secondsElapsed = now - timestamp

  if (secondsElapsed < 5) {
    return 'Just now'
  }

  if (secondsElapsed < SECONDS_IN_MINUTE) {
    return `${secondsElapsed} second${secondsElapsed === 1 ? '' : 's'} ago`
  }

  if (secondsElapsed < SECONDS_IN_HOUR) {
    const minutes = Math.floor(secondsElapsed / SECONDS_IN_MINUTE)
    return `${minutes} minute${minutes === 1 ? '' : 's'} ago`
  }

  if (secondsElapsed < SECONDS_IN_DAY) {
    if (secondsElapsed < SECONDS_IN_DAY - SECONDS_IN_HOUR) {
      return 'Yesterday'
    }
    const hours = Math.floor(secondsElapsed / SECONDS_IN_HOUR)
    return `${hours} hour${hours === 1 ? '' : 's'} ago`
  }

  if (secondsElapsed < SECONDS_IN_WEEK) {
    const days = Math.floor(secondsElapsed / SECONDS_IN_DAY)
    return `${days} day${days === 1 ? '' : 's'} ago`
  }

  if (secondsElapsed < SECONDS_IN_MONTH) {
    const weeks = Math.floor(secondsElapsed / SECONDS_IN_WEEK)
    return `${weeks} week${weeks === 1 ? '' : 's'} ago`
  }

  const months = Math.floor(secondsElapsed / SECONDS_IN_MONTH)
  return `${months} month${months === 1 ? '' : 's'} ago`
}
