import assert from 'node:assert/strict'
import { mkdir } from 'node:fs/promises'
import { join, resolve } from 'node:path'
import puppeteer from '../../tools/diagrams/node_modules/puppeteer/lib/puppeteer/puppeteer.js'

const [url, chrome, target, profile, wav] = process.argv.slice(2)
const real = profile === 'real'
const args = real ? ['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream',
  '--use-file-for-fake-audio-capture=' + resolve(wav), '--autoplay-policy=no-user-gesture-required'] : []
const browser = await puppeteer.launch({ executablePath: chrome, headless: true, args })
const page = await browser.newPage()
const requestErrors = []
page.on('pageerror', error => requestErrors.push(error.message))
const selector = mode => '.live-toggle button[data-choice=' + mode + ']'
const phase = state => page.waitForSelector('.mode-ribbon[data-state=' + state + ']')
const ribbon = () => page.$eval('.mode-ribbon', element => element.textContent.trim())
const shot = async name => {
  if (target) await page.screenshot({path: join(target, 'live-toggle-' + name + '.png'), fullPage: false})
}
try {
  if (target) await mkdir(target, {recursive: true})
  await page.setViewport({width: 1440, height: 900})
  await page.goto(new URL('/console', url).href)
  await page.waitForSelector('.connected')
  await phase('mock')
  await shot('mock')
  await page.click(selector('live'))
  await phase('checking')
  await shot('checking')
  const outcome = await page.waitForFunction(() => {
    const state = document.querySelector('.mode-ribbon').dataset.state
    return state !== 'checking' ? state : null
  })
  if (await outcome.jsonValue() === 'mock') throw Error(await page.$eval('.cockpit-toast', element => element.textContent))
  if (!real) {
    await phase('warming')
    assert(await page.$eval('button.mic', element => element.disabled))
    await shot('warming')
  }
  await phase('live')
  assert.equal(await page.$eval(selector('live'), button => button.getAttribute('aria-pressed')), 'true')
  await page.waitForSelector('.mode-divider')
  assert.match(await ribbon(), /LIVE.+Readiness.+ms/)
  await shot('live')
  console.log('Live activation:', await ribbon())
  if (real) {
    await page.type('#message', 'I would like to talk about inventory tracking.')
    await page.keyboard.press('Enter')
    await page.waitForFunction(() => document.querySelectorAll('.message.agent:not(.streaming)').length > 1)
    const text = await page.$$eval('.message.agent:not(.streaming)', items => items.at(-1).textContent)
    console.log('Real text:', text, '|', await ribbon())
    await page.click('button.mic')
    await page.waitForFunction(() => document.querySelector('button.mic').textContent === 'Stop')
    await new Promise(resolve => setTimeout(resolve, 2600))
    await page.click('button.mic')
    await page.waitForFunction(() => [...document.querySelectorAll('dt')].some(el => el.textContent === 'Stop to playback') ||
      document.querySelector('.voice-error'), {timeout: 35000})
    assert.equal(await page.$('.voice-error'), null)
    const data = await page.evaluate(() => Object.fromEntries([...document.querySelectorAll('.latency-row')].map(row =>
      [row.querySelector('dt').textContent, row.querySelector('dd').textContent])))
    console.log('Real voice:', JSON.stringify(data), '|', await ribbon())
  }
  await page.click(selector('mock'))
  await phase('mock')
  await page.waitForFunction(() => [...document.querySelectorAll('.mode-divider')].some(el => el.textContent.includes('Switched to MOCK')))
  await page.waitForFunction(() => document.querySelector('.cockpit-toast')?.textContent.includes('Mock mode enabled'))
  if (!real) {
    await page.click(selector('live'))
    await page.waitForFunction(() => document.querySelector('.cockpit-toast')?.textContent.includes('rejected the API key'))
    await shot('failure')
    assert.equal(await page.$eval(selector('mock'), button => button.getAttribute('aria-pressed')), 'true')
    await page.setViewport({width: 390, height: 900})
    await page.evaluate(() => scrollTo(0, 0))
    await page.locator('::-p-aria(Presenter mode)').click()
    assert(await page.evaluate(() => {
      const control = document.querySelector('.live-toggle').getBoundingClientRect()
      return control.right <= innerWidth && document.documentElement.scrollWidth <= innerWidth
    }))
    await shot('mobile')
  }
  assert.deepEqual(requestErrors, [])
  console.log('Chrome: mode dividers, selected badges, toast and return to mock verified')
} finally {
  await browser.close()
}
