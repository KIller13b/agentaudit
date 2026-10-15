import { chromium } from 'playwright-core'
import fs from 'node:fs'
import path from 'node:path'

const CHROMIUM = process.env.CHROMIUM_PATH || '/usr/bin/chromium'
const ROOT = path.resolve(new URL('.', import.meta.url).pathname, '..')
const OUT_DIR = path.join(ROOT, 'demo', 'raw')

fs.mkdirSync(OUT_DIR, { recursive: true })

const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

const browser = await chromium.launch({
  executablePath: CHROMIUM,
  args: ['--no-sandbox', '--disable-setuid-sandbox'],
})

const context = await browser.newContext({
  viewport: { width: 1280, height: 800 },
  deviceScaleFactor: 1,
  recordVideo: { dir: OUT_DIR, size: { width: 1280, height: 800 } },
})

const page = await context.newPage()
await page.goto('http://localhost:5173', { waitUntil: 'networkidle' })
await sleep(1400)

await page.getByRole('button', { name: /Load Demo Contract/i }).click()
await sleep(1200)

await page.getByRole('button', { name: /Audit Contract/i }).click()

await page.waitForSelector('text=/Analyzed \\d+ file/', { timeout: 60000 })
await sleep(1800)

await page.mouse.wheel(0, 500)
await sleep(1200)
await page.mouse.wheel(0, 600)
await sleep(1400)
await page.mouse.wheel(0, 700)
await sleep(1600)
await page.mouse.wheel(0, -400)
await sleep(1200)

await page.screenshot({ path: path.join(ROOT, 'demo', 'raw', 'preview.png') })
await context.close()
await browser.close()

const video = await page.video().path()
console.log('VIDEO_PATH=' + video)
