import { chromium } from 'playwright-core'

const browser = await chromium.launch({
  executablePath: '/usr/bin/chromium',
  args: ['--no-sandbox', '--disable-setuid-sandbox'],
})
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 })
await page.goto('https://agentaudit-gamma.vercel.app/', { waitUntil: 'networkidle', timeout: 45000 })
await page.waitForTimeout(2500)
await page.screenshot({ path: '/home/killer13b/Projects/Cascade/agentaudit/demo/assets/live.png' })
console.log('saved live.png')
await browser.close()
