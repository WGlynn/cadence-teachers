// Headless visual check: screenshots of the built site at several viewports (npm run shots).
// Serve dist first (npx vite preview --port 4173), then run. Writes PNGs to the system temp dir and
// reports console errors. Uses the local Chrome via puppeteer-core; WebGL via SwiftShader.
import puppeteer from 'puppeteer-core'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { mkdirSync } from 'node:fs'

const URL = process.env.URL || 'http://localhost:4173/'
const CHROME = process.env.CHROME || 'C:/Program Files/Google/Chrome/Application/chrome.exe'
const OUT = join(tmpdir(), 'atlas-shots'); mkdirSync(OUT, { recursive: true })
const VIEWS = [['desktop', 1440, 900], ['laptop', 1424, 749], ['phone', 390, 844]]
const SECTIONS = (process.env.SECTIONS || 'top').split(',')

const browser = await puppeteer.launch({ executablePath: CHROME, headless: 'new',
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--hide-scrollbars'] })
const errors = []
for (const [name, w, h] of VIEWS) {
  const page = await browser.newPage()
  page.on('pageerror', (e) => errors.push(`${name}: ${e.message}`))
  page.on('console', (m) => { if (m.type() === 'error') errors.push(`${name}: ${m.text()}`) })
  await page.setViewport({ width: w, height: h, deviceScaleFactor: 1 })
  await page.goto(URL, { waitUntil: 'networkidle0', timeout: 60000 })
  for (const s of SECTIONS) {
    if (s !== 'top') await page.evaluate((id) => document.getElementById(id)?.scrollIntoView({ behavior: 'instant' }), s)
    await new Promise((r) => setTimeout(r, 3500))
    const file = join(OUT, `${name}-${s}.png`)
    await page.screenshot({ path: file })
    // layout check: hero copy must not run under the fixed nav
    if (s === 'top') {
      const r = await page.evaluate(() => {
        const nav = document.querySelector('.nav')?.getBoundingClientRect()
        const copy = document.querySelector('.hero-copy')?.getBoundingClientRect()
        return { navBottom: nav?.bottom ?? 0, copyTop: copy?.top ?? 0, copyBottom: copy?.bottom ?? 0, vh: innerHeight }
      })
      console.log(`${name} ${w}x${h}: hero copy ${Math.round(r.copyTop)}..${Math.round(r.copyBottom)} (nav ends ${Math.round(r.navBottom)}, viewport ${r.vh})${r.copyTop < r.navBottom ? '  <-- OVERLAPS NAV' : ''}`)
    }
    console.log('  ' + file)
  }
  await page.close()
}
await browser.close()
console.log(errors.length ? 'console errors:\n' + errors.join('\n') : 'no console errors')
