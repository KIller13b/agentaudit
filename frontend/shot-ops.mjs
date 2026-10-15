import { chromium } from 'playwright-core'
import path from 'node:path'

const CHROMIUM = process.env.CHROMIUM_PATH || '/usr/bin/chromium'
const ROOT = path.resolve(new URL('.', import.meta.url).pathname, '..')

const browser = await chromium.launch({
  executablePath: CHROMIUM,
  args: ['--no-sandbox', '--disable-setuid-sandbox'],
})
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } })
await page.goto('http://localhost:8000/ops', { waitUntil: 'networkidle' })
await page.waitForTimeout(3500)
await page.screenshot({ path: path.join(ROOT, 'demo', 'assets', 'ops.png'), fullPage: true })
await browser.close()
console.log('screenshot saved: demo/assets/ops.png')
