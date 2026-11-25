import puppeteer from '../tools/diagrams/node_modules/puppeteer/lib/puppeteer/puppeteer.js'
import { join, resolve } from 'node:path'

const [url, folder, chrome] = process.argv.slice(2)
for (const lang of ['en', 'hi']) {
  const browser = await puppeteer.launch({ executablePath: chrome, headless: true,
    args: ['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream',
      '--use-file-for-fake-audio-capture=' + resolve(join(folder, lang + '-input.wav')) + '%noloop'] })
  try {
    const page = await browser.newPage()
    await page.goto(url)
    const result = await page.evaluate(language => new Promise(async resolve => {
      const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition
      if (!Recognition) return resolve({ error: 'unavailable' })
      const recognition = new Recognition()
      recognition.lang = language + '-IN'
      recognition.interimResults = true
      const started = performance.now()
      let interim
      const timer = setTimeout(() => { recognition.abort(); resolve({ error: 'timeout' }) }, 14000)
      const finish = fields => { clearTimeout(timer); resolve({ ...fields, interim }) }
      recognition.onerror = event => finish({ error: event.error })
      recognition.onend = () => finish({ error: 'ended without final result' })
      recognition.onresult = event => {
        for (const result of event.results) {
          if (result.isFinal) finish({ text: result[0].transcript, finalMs: Math.round(performance.now() - started) })
          else interim ??= Math.round(performance.now() - started)
        }
      }
      try { recognition.start() } catch (error) { finish({ error: error.name }) }
    }), lang)
    console.log(lang, JSON.stringify(result))
  } finally { await browser.close() }
}
