// Navigation QA: drives headless Chrome over CDP (Node 22+ global WebSocket).
import http from 'node:http'

const CDP_PORT = 9222
const BASE = `http://localhost:${CDP_PORT}`
const APP = 'http://localhost:4173'

const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

function getJson(url) {
  return new Promise((resolve, reject) => {
    http
      .get(url, (res) => {
        let data = ''
        res.on('data', (c) => (data += c))
        res.on('end', () => {
          try { resolve(JSON.parse(data)) } catch (e) { reject(e) }
        })
      })
      .on('error', reject)
  })
}

const targets = await getJson(`${BASE}/json/list`)
const page = targets.find((t) => t.type === 'page')
if (!page) throw new Error('No page target found')

const ws = new WebSocket(page.webSocketDebuggerUrl)
await new Promise((resolve, reject) => { ws.onopen = resolve; ws.onerror = reject })

let msgId = 0
const pending = new Map()
const runtimeErrors = []

ws.onmessage = (ev) => {
  const msg = JSON.parse(ev.data)
  if (msg.id) {
    const p = pending.get(msg.id)
    if (p) {
      pending.delete(msg.id)
      msg.error ? p.reject(new Error(JSON.stringify(msg.error))) : p.resolve(msg.result)
    }
    return
  }
  if (msg.method === 'Runtime.exceptionThrown') {
    runtimeErrors.push(msg.params.exceptionDetails?.text ?? 'exception')
  }
  if (msg.method === 'Runtime.consoleAPICalled' && msg.params.type === 'error') {
    runtimeErrors.push(msg.params.args.map((a) => a.value ?? a.description ?? '').join(' '))
  }
  if (msg.method === 'Log.entryAdded' && msg.params.entry.level === 'error') {
    runtimeErrors.push(msg.params.entry.text)
  }
}

function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = ++msgId
    pending.set(id, { resolve, reject })
    ws.send(JSON.stringify({ id, method, params }))
  })
}

async function evaluate(expression) {
  const r = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true })
  if (r.exceptionDetails) throw new Error(`eval failed: ${r.exceptionDetails.text} :: ${expression}`)
  return r.result.value
}

async function waitFor(fn, timeout = 15000, label = 'condition') {
  const start = Date.now()
  while (Date.now() - start < timeout) {
    try { if (await fn()) return } catch { /* retry */ }
    await sleep(150)
  }
  throw new Error(`timeout waiting for ${label}`)
}

const results = []
function report(name, ok, detail = '') {
  results.push({ name, ok, detail })
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${name}${detail ? `  [${detail}]` : ''}`)
}

await send('Page.enable')
await send('Runtime.enable')
await send('Log.enable')

async function goto(url) {
  await send('Page.navigate', { url })
  await waitFor(
    () => evaluate(`location.pathname === ${JSON.stringify(new URL(url).pathname)}`),
    15000,
    `navigate to ${url}`,
  )
}

async function waitPath(path) {
  await waitFor(() => evaluate(`location.pathname === ${JSON.stringify(path)}`), 15000, `path ${path}`)
}

async function activeHref() {
  return evaluate(`document.querySelector('nav[aria-label="Primary"] a[aria-current="page"]')?.getAttribute('href') ?? null`)
}

// ---------- 1. Dashboard: content, active state, Back to Home present ----------
await goto(`${APP}/dashboard`)
await waitFor(() => evaluate(`document.body.innerText.includes('Executive Command Center')`), 15000, 'dashboard content')
report('1. /dashboard renders', true)
report('1. active nav = /dashboard', (await activeHref()) === '/dashboard', `got ${await activeHref()}`)
report('1. Back to Home present in sidebar', await evaluate(`document.body.innerText.includes('Back to Home')`))

// ---------- 2. SPA navigation Dashboard -> Leads -> Analytics -> Settings ----------
await evaluate(`window.__marker = 'spa-alive'`)
await evaluate(`document.querySelector('a[href="/leads"]').click()`)
await waitPath('/leads')
await waitFor(() => evaluate(`document.getElementById('main-content')?.innerText.toLowerCase().includes('ai-powered lead intelligence')`), 15000, 'leads content')
report('2. click Leads -> /leads', true)
report('2. no full page reload (SPA)', (await evaluate(`window.__marker`)) === 'spa-alive')
report('2. active nav = /leads', (await activeHref()) === '/leads', `got ${await activeHref()}`)

await evaluate(`document.querySelector('a[href="/analytics/sales"]').click()`)
await waitPath('/analytics/sales')
await waitFor(() => evaluate(`document.body.innerText.toLowerCase().includes('sales analytics')`), 15000, 'analytics content')
report('2. click Sales Analytics -> /analytics/sales', true)
report('2. active nav = /analytics/sales', (await activeHref()) === '/analytics/sales', `got ${await activeHref()}`)

await evaluate(`document.querySelector('a[href="/settings"]').click()`)
await waitPath('/settings')
await waitFor(() => evaluate(`document.getElementById('main-content')?.innerText.toLowerCase().includes('system settings')`), 15000, 'settings content')
report('2. click Settings -> /settings', true)
report('2. active nav = /settings', (await activeHref()) === '/settings', `got ${await activeHref()}`)

// ---------- 3. Back to Home leaves the dashboard shell ----------
await evaluate(`document.querySelector('a[href="/"]').click()`)
await waitPath('/')
await waitFor(() => evaluate(`document.body.innerText.includes('Powerful Tools for Education Sales')`), 15000, 'homepage content')
report('3. Back to Home -> / (homepage)', true)
report('3. no full page reload (SPA)', (await evaluate(`window.__marker`)) === 'spa-alive')
report('3. dashboard sidebar absent on homepage', !(await evaluate(`document.body.innerText.includes('Back to Home')`)))

// ---------- 4. Browser back / forward ----------
await evaluate(`history.back()`)
await waitPath('/settings')
report('4. browser back -> /settings', true)
report('4. active nav = /settings after back', (await activeHref()) === '/settings', `got ${await activeHref()}`)

await evaluate(`history.back()`)
await waitPath('/analytics/sales')
report('4. browser back x2 -> /analytics/sales', true)

await evaluate(`history.forward()`)
await waitPath('/settings')
report('4. browser forward -> /settings', true)

// ---------- 5. Direct URL access + active state after refresh ----------
await goto(`${APP}/call-intelligence`)
await waitFor(() => evaluate(`(document.getElementById('main-content')?.innerText.length ?? 0) > 100`), 15000, 'call intelligence content')
report('5. direct URL /call-intelligence renders', true)
report('5. active nav after direct load = /call-intelligence', (await activeHref()) === '/call-intelligence', `got ${await activeHref()}`)

await goto(`${APP}/ai/lead-scoring`)
await waitFor(() => evaluate(`(document.getElementById('main-content')?.innerText.length ?? 0) > 100`), 15000, 'lead scoring content')
report('5. direct URL /ai/lead-scoring renders', true)
report('5. active nav after direct load = /ai/lead-scoring', (await activeHref()) === '/ai/lead-scoring', `got ${await activeHref()}`)

// ---------- 6. Mobile (390x844 then 430x932): drawer nav works, no overflow ----------
for (const [w, h] of [
  [390, 844],
  [430, 932],
]) {
  await send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 1, mobile: true })
  await goto(`${APP}/dashboard`)
  await waitFor(() => evaluate(`document.body.innerText.includes('Executive Command Center')`), 15000, 'mobile dashboard content')
  await waitFor(() => evaluate(`!!document.querySelector('button[aria-label="Toggle navigation"]')`), 10000, 'menu button')
  await evaluate(`document.querySelector('button[aria-label="Toggle navigation"]').click()`)
  await waitFor(() => evaluate(`!document.querySelector('[inert]')`), 10000, 'drawer opens')
  const drawerHasNav = await evaluate(
    `document.body.innerText.includes('Back to Home') && document.body.innerText.includes('Leads') && document.body.innerText.includes('Settings')`,
  )
  report(`6. ${w}x${h} drawer shows nav + Back to Home`, drawerHasNav)
  await evaluate(`document.querySelector('a[href="/leads"]').click()`)
  await waitPath('/leads')
  const drawerClosed = await evaluate(
    `document.querySelector('div[inert]') !== null || document.querySelector('aside [inert]') !== null`,
  )
  report(`6. ${w}x${h} click Leads in drawer -> /leads`, true)
  const overflow = await evaluate(`document.documentElement.scrollWidth > window.innerWidth + 1`)
  report(`6. ${w}x${h} no horizontal overflow`, !overflow, overflow ? `scrollWidth=${'x'} > innerWidth` : 'ok')
  await send('Emulation.clearDeviceMetricsOverride')
}

// ---------- 7. Console errors ----------
report('7. no console errors / exceptions', runtimeErrors.length === 0, runtimeErrors.slice(0, 3).join(' | '))

ws.close()
const failed = results.filter((r) => !r.ok)
console.log(`\n${results.length - failed.length}/${results.length} checks passed`)
process.exit(failed.length === 0 ? 0 : 1)
