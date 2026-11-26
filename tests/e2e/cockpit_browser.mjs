import assert from 'node:assert/strict'
import { mkdir } from 'node:fs/promises'
import { join, resolve } from 'node:path'
import puppeteer from '../../tools/diagrams/node_modules/puppeteer/lib/puppeteer/puppeteer.js'

const [url, chrome, screenshots, micFixture] = process.argv.slice(2)
const args = micFixture ? ['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream',
  '--use-file-for-fake-audio-capture=' + resolve(micFixture)] : []
const browser = await puppeteer.launch({ executablePath: chrome, headless: true, args })
const origin = new URL(url).origin
try {
  if (screenshots) await mkdir(screenshots, { recursive: true })
  for (const width of [1440, 768, 390]) {
    const page = await browser.newPage()
    const errors = []
    page.on('pageerror', error => errors.push(error.message))
    page.on('console', message => {
      if (message.type() === 'error') errors.push(message.text() + ' ' + (message.location().url || ''))
    })
    await page.setRequestInterception(true)
    page.on('request', request => request.url().startsWith(origin) ? request.continue() : request.abort())
    await page.emulateMediaFeatures([{ name: 'prefers-reduced-motion', value: 'reduce' }])
    await page.setViewport({ width, height: width === 390 ? 910 : 1100 })
    await page.goto(new URL('/console', url).href)
    await page.waitForSelector('.connected')
    await page.waitForSelector('.mock-ribbon')
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth))
    const gridColumns = await page.$eval('.cockpit-grid', element => getComputedStyle(element).gridTemplateColumns.split(' ').length)
    assert.equal(gridColumns, width === 1440 ? 3 : width === 768 ? 2 : 1)
    await page.keyboard.press('Tab')
    assert.equal(await page.evaluate(() => document.activeElement.textContent), 'Skip to console')
    await page.$eval('.cockpit-skip', element => element.blur())
    const screenshot = async stage => {
      if (!screenshots) return
      await page.evaluate(() => window.scrollTo(0, 0))
      await page.screenshot({ path: join(screenshots, 'cockpit-' + (width === 390 ? 'mobile' : 'desktop') + '-' + stage + '.png'), fullPage: stage !== 'insights' })
    }
    if (width === 768) {
      assert.deepEqual(errors, [])
      await page.close()
      console.log('768 px: two columns, connected, keyboard skip link, zero errors and overflow')
      continue
    }
    await screenshot('empty')
    const mobile = width === 390
    const show = async tab => { if (mobile) await page.click('#cockpit-tab-' + tab) }
    if (mobile) {
      await page.focus('#cockpit-tab-conversation')
      await page.keyboard.press('ArrowRight')
      assert.equal(await page.$eval('#cockpit-tab-call', element => element.getAttribute('aria-selected')), 'true')
      await page.waitForSelector('.call-scenarios', { visible: true })
    }
    await page.locator('::-p-aria(Run the hero journey)').click()
    assert.equal(await page.$$eval('.message.buyer', messages => messages.length), 0)
    await page.locator('.guide-next').click()
    await page.waitForSelector('.citation-chip', { visible: true })
    await page.click('.citation-chip')
    await page.waitForFunction(() => document.querySelector('dialog[open] blockquote')?.textContent.includes('2,499'))
    await page.keyboard.press('Escape')
    await page.waitForSelector('dialog[open]', { hidden: true })

    const type = async (text, expected) => {
      await show('conversation')
      await page.type('#message', text)
      await page.keyboard.press('Enter')
      await page.waitForFunction(phrase => [...document.querySelectorAll('.message.agent:not(.streaming) p')].at(-1)?.textContent.includes(phrase), {}, expected)
    }
    await type('Can I get 40% off?', 'specialist follow up')
    await page.waitForSelector('.event-note')
    await screenshot('conversation')
    await page.type('#message', 'My name is Asha.')
    await page.keyboard.press('Enter')
    await page.waitForFunction(() => document.querySelector('[aria-label="Lead profile"]')?.textContent.includes('Asha'))
    await page.type('#message', 'I am the owner. We need inventory tools this month. Our budget is fixed, but I am frustrated.')
    await page.keyboard.press('Enter')
    await page.waitForFunction(() => document.querySelector('[aria-label="Lead profile"]')?.textContent.includes('inventory tools'))
    const contact = 'cockpit-' + width + '-' + Date.now() + '@example.test'
    await type('My email is ' + contact, 'saved the demo contact')
    await type('Book a demo', 'UTC+05:30')
    await type('Confirm booking', 'Demo booked')
    await page.waitForSelector('[aria-label="Booking receipt"]', { visible: true })
    await screenshot('receipt')
    await show('intelligence')
    if (mobile) await page.waitForSelector('#intelligence-panel', { visible: true })
    await page.locator('::-p-aria(View demo CRM)').click()
    await page.waitForFunction(contact => document.querySelector('dialog[open] [aria-label="Demo CRM"]')?.textContent.includes(contact), {}, contact)
    await page.keyboard.press('Escape')
    await page.waitForSelector('dialog[open]', { hidden: true })
    await show('conversation')
    await page.locator('::-p-aria(End conversation)').click()
    await page.waitForFunction(() => [...document.querySelectorAll('.message.agent p')].at(-1)?.textContent.includes('Conversation ended'))
    await show('intelligence')
    await page.waitForFunction(() => document.querySelector('[aria-label="Sentiment"] .intel-value') &&
      document.querySelector('[aria-label="Lead score"] .intel-value')?.textContent.includes('Hot 100'))
    await page.locator('::-p-aria(View insights)').click()
    await page.waitForFunction(() => document.querySelector('dialog[open] [aria-label="Call insights"]')?.textContent.includes('Follow-up draft'))
    await screenshot('insights')
    await page.keyboard.press('Escape')
    await page.waitForSelector('dialog[open]', { hidden: true })
    await page.evaluate(() => window.scrollTo(0, 0))
    await page.locator('::-p-aria(Reset call)').click()
    await page.waitForSelector('.connected').catch(async error => {
      console.error(await page.$eval('.connection-status', node => node.textContent), errors)
      throw error
    })
    await page.waitForSelector('.cockpit-empty', { visible: true })
    await show('intelligence')
    await page.locator('::-p-aria(Simulate Gemini failures)').click()
    await page.waitForFunction(() => {
      const trace = document.querySelector('.trace')?.textContent || ''
      return ['Gemini A', 'Gemini B', 'mock active'].every(label => trace.includes(label))
    })
    await page.evaluate(() => window.scrollTo(0, 0))
    await page.locator('::-p-aria(Presenter mode)').click()
    await page.waitForSelector('.cockpit[data-presenter=true]')
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth))
    assert.deepEqual(errors, [])
    console.log(width + ' px: connected, guide, source drawer, abstention, booking, CRM, saved analysis, reset, fallback, presenter and keyboard passed; zero errors and overflow')
    await page.close()
  }
  if (micFixture) {
    const page = await browser.newPage()
    const errors = []
    page.on('pageerror', error => errors.push(error.message))
    await page.goto(new URL('/console', url).href)
    await page.waitForSelector('.connected')
    await page.click('button.mic')
    await page.waitForFunction(() => {
      const station = document.querySelector('.call-station[data-state=listening]')
      return station && parseFloat(station.style.getPropertyValue('--mic-scale')) > 1.02
    })
    await new Promise(resolve => setTimeout(resolve, 1900))
    await page.click('button.mic')
    await page.waitForSelector('.call-station[data-state=speaking]')
    await page.waitForFunction(() => [...document.querySelectorAll('dt')]
      .some(label => label.textContent === 'Stop to playback' && /\d+ ms/.test(label.nextElementSibling.textContent)))
    assert.deepEqual(errors, [])
    console.log('Synthetic mic: input changed the orb scale, playback signaled Speaking, and real browser timing populated')
  }
} finally {
  await browser.close()
}
