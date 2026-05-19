export const clamp = (val, min, max) => Math.min(Math.max(val, min), max)

export const debounce = (fn, delay) => {
  let timer
  return (...args) => {
    clearTimeout(timer)
    timer = setTimeout(() => fn(...args), delay)
  }
}
