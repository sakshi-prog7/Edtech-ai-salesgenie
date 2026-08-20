import http from 'node:http'

const getJson = (url) =>
  new Promise((resolve, reject) => {
    http.get(url, (res) => {
      let d = ''
      res.on('data', (c) => (d += c))
      res.on('end', () => { try { resolve(JSON.parse(d)) } catch (e) { reject(e) } })
    }).on('error', reject)
  })

const targets = await getJson('http://localhost:9222/json/list')
const page = targets.find((t) => t.type === 'page')
const ws = new WebSocket(page.webSocketDebuggerUrl)
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej })
let msgId = 0
const pending = new Map()
ws.onmessage = (ev) => {
  const msg = JSON.parse(ev.data)
  if (msg.id) {
    const p = pending.get(msg.id)
    if (p) { pending.delete(msg.id); msg.error ? p.reject(new Error(JSON.stringify(msg.error))) : p.resolve(msg.result) }
  }
}
const send = (method, params = {}) =>
  new Promise((resolve, reject) => {
    const id = ++msgId
    pending.set(id, { resolve, reject })
    ws.send(JSON.stringify({ id, method, params }))
  })
const evaluate = async (expression) => {
  const r = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true })
  if (r.exceptionDetails) return `EVAL-ERROR: ${r.exceptionDetails.text}`
  return r.result.value
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

await send('Page.enable')
await send('Runtime.enable')
await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 1, mobile: true })

await send('Page.navigate', { url: 'http://localhost:4173/dashboard' })
await sleep(4000)
await evaluate(`document.querySelector('button[aria-label="Toggle navigation"]').click()`)
await sleep(1500)

console.log('inert elements:')
console.log(await evaluate(`[...document.querySelectorAll('[inert]')].map(el => el.tagName + '.' + (el.className || '').toString().slice(0, 80)).join('\\n')`))
console.log('inert count:', await evaluate(`document.querySelectorAll('[inert]').length`))
console.log('inert VALUE of first:', await evaluate(`document.querySelector('[inert]')?.getAttribute('inert')`))
ws.close()
process.exit(0)
