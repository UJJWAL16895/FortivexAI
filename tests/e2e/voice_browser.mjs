// Exercise a real browser microphone API with a synthetic WAV as its capture device.
import { resolve } from 'node:path'
import puppeteer from '../../tools/diagrams/node_modules/puppeteer/lib/puppeteer/puppeteer.js'

const [url, wav, chrome, mode = 'mock', language = 'en', duration = '2500'] = process.argv.slice(2)
if (!url || !wav || !chrome || !['mock', 'live'].includes(mode)) {
  throw Error('Usage: node tests/e2e/voice_browser.mjs URL CAPTURE.wav CHROME_PATH [mock|live]')
}
const browser = await puppeteer.launch({
  executablePath: chrome,
  headless: true,
  args: ['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream',
    '--use-file-for-fake-audio-capture=' + resolve(wav)],
})
try {
  const page = await browser.newPage()
  const errors = []
  page.on('pageerror', error => errors.push(error.message))
  await page.setViewport({ width: 390, height: 844 })
  await page.goto(url)
  await page.waitForSelector('.connected')
  if (language !== 'en') await page.select('#voice-language', language)
  await page.click('button.mic')
  await page.waitForFunction(() => document.querySelector('button.mic').textContent === 'Stop')
  await new Promise(resolve => setTimeout(resolve, Number(duration)))
  await page.click('button.mic')
  await page.waitForFunction(() => document.querySelector('.voice-error') ||
    [...document.querySelectorAll('dt')].some(el => el.textContent === 'Stop to playback'), { timeout: 45000 })
  const evidence = await page.evaluate(() => ({
    transcript: document.querySelector('.message.buyer p')?.textContent,
    error: document.querySelector('.voice-error')?.textContent,
    data: Object.fromEntries([...document.querySelectorAll('dl div')].map(
      row => [row.querySelector('dt').textContent, row.querySelector('dd').textContent]
    )),
    mode: document.querySelector('.mode').textContent.trim(),
    overflow: document.documentElement.scrollWidth > innerWidth,
  }))
  console.log(JSON.stringify({ ...evidence, pageErrors: errors.length }))
  if (evidence.error || !evidence.transcript || !evidence.data['Stop to playback'] ||
      evidence.mode !== mode.toUpperCase() || evidence.overflow || errors.length) {
    throw Error('Voice flow failed')
  }
} finally {
  await browser.close()
}
