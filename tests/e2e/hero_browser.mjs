import puppeteer from '../../tools/diagrams/node_modules/puppeteer/lib/puppeteer/puppeteer.js'
import { readFile } from 'node:fs/promises'
import { join } from 'node:path'

const [url, chrome, voiceFolder] = process.argv.slice(2)
const browser = await puppeteer.launch({
  executablePath: chrome,
  headless: true,
  args: ['--autoplay-policy=no-user-gesture-required'],
})
try {
  const page = await browser.newPage()
  const errors = []
  page.on('pageerror', error => errors.push(error.message))
  const contact = (voiceFolder ? 'voice' : 'text') + '-hero@example.test'
  if (voiceFolder) {
    const files = await Promise.all(['price', 'book', 'confirm'].map(async name =>
      (await readFile(join(voiceFolder, name + '.wav'))).toString('base64')))
    await page.evaluateOnNewDocument(clips => {
      let index = 0
      // A synthetic microphone. The app's MediaRecorder, PCM upload, STT and playback are unchanged.
      navigator.mediaDevices.getUserMedia = async () => {
        const context = new AudioContext()
        await context.resume()
        const data = Uint8Array.from(atob(clips[index++]), letter => letter.charCodeAt(0))
        const source = context.createBufferSource()
        const output = context.createMediaStreamDestination()
        source.buffer = await context.decodeAudioData(data.buffer)
        source.connect(output)
        source.onended = () => setTimeout(() => context.close(), 1500)
        source.start(context.currentTime + .25)
        return output.stream
      }
    }, files)
  }
  await page.goto(url)
  await page.waitForSelector('.connected')
  const lastReply = text => page.waitForFunction(value =>
    [...document.querySelectorAll('.message.agent p')].at(-1)?.textContent.includes(value),
  { timeout: 30000 }, text)
  const typed = async (text, expected) => {
    await page.type('#message', text)
    await page.keyboard.press('Enter')
    await lastReply(expected)
  }
  const spoken = async expected => {
    await page.click('button.mic')
    await page.waitForFunction(() => document.querySelector('button.mic').textContent === 'Stop')
    await new Promise(resolve => setTimeout(resolve, 4300))
    await page.click('button.mic')
    await lastReply(expected)
    await page.waitForFunction(() => [...document.querySelectorAll('dt')]
      .some(el => el.textContent === 'Stop to playback'), { timeout: 15000 })
  }
  if (voiceFolder) await spoken('2,499')
  else await typed('How much does Growth cost?', '2,499')
  await page.waitForFunction(() => [...document.querySelectorAll('.message small')]
    .some(el => el.textContent.includes('plans-and-prices.json#growth')))
  const replies = await page.$$eval('.message.agent p', items => items.length)
  await page.type('#message', 'My name is Asha.')
  await page.keyboard.press('Enter')
  await page.waitForFunction(count => document.querySelectorAll('.message.agent p').length > count &&
    document.querySelector('[aria-label="Lead profile"]')?.textContent.includes('Asha'), {}, replies)
  await typed('My email is ' + contact, 'saved the demo contact')
  if (voiceFolder) {
    await spoken('UTC+05:30')
    await spoken('Demo booked')
  } else {
    await typed('Book a demo', 'UTC+05:30')
    await typed('Confirm booking', 'Demo booked')
    await typed('Confirm booking', 'Demo booked')
  }
  await page.evaluate(() => [...document.querySelectorAll('button')]
    .find(el => el.textContent === 'View demo CRM').click())
  await page.waitForFunction(value => document.querySelector('[aria-label="Demo CRM"]')
    ?.textContent.includes(value), {}, contact)
  const crm = await page.evaluate(async () => (await fetch('/api/crm')).json())
  if (crm.leads.filter(row => row.contact === contact).length !== 1 ||
      crm.bookings.filter(row => row.contact === contact).length !== 1 || errors.length) {
    throw Error('Expected one persisted demo lead and booking, with no browser exceptions')
  }
  await page.reload()
  await page.waitForSelector('.connected')
  await typed(contact, 'Welcome back, Asha')
  console.log((voiceFolder ? 'Voice' : 'Text') + ' hero: citation, timezone, one booking, one CRM lead, returning caller verified.')
  if (process.env.CHECK_HERO_INSIGHTS === '1') {
    await page.evaluate(() => [...document.querySelectorAll('button')]
      .find(el => el.textContent === 'End conversation').click())
    await lastReply('Conversation ended')
    await page.waitForFunction(async () => (await (await fetch('/api/insights')).json()).calls.some(call => call.booked))
    await page.evaluate(() => [...document.querySelectorAll('button')]
      .find(el => el.textContent === 'View insights').click())
    await page.waitForFunction(() => document.querySelector('[aria-label="Call insights"]')
      ?.textContent.includes('Follow-up draft'))
    if (errors.length) throw Error('Unexpected browser exception in the insights flow')
    console.log('Insights panel: completed booking count, report and follow-up draft verified.')
  }
} finally {
  await browser.close()
}
