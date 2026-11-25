import puppeteer from '../../tools/diagrams/node_modules/puppeteer/lib/puppeteer/puppeteer.js'
import assert from 'node:assert/strict'
import { mkdir } from 'node:fs/promises'
const [url, chrome] = process.argv.slice(2)
const browser = await puppeteer.launch({executablePath:chrome})
try {
  const page = await browser.newPage()
  const errors = []
  const context = new URL(url).origin
  await page.setRequestInterception(true)
  page.on('request', request => request.url().startsWith(context) ? request.continue() : request.abort())
  page.on('pageerror', error => errors.push(error.message))
  await page.emulateMediaFeatures([{name:'prefers-reduced-motion', value:'reduce'}])
  await mkdir('docs/diagrams/ui', {recursive:true})
  for (const width of [390,768,1440]) {
    await page.setViewport({width,height:900})
    await page.goto(url, {waitUntil:'networkidle0'})
    await page.waitForSelector('.show-hero')
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth))
    assert(await page.evaluate(()=>[...document.querySelectorAll('.show-nav nav a')].every(a=>document.querySelector(a.hash))))
    if (width!==768) await page.screenshot({path:'docs/diagrams/ui/'+(width===390?'mobile':'desktop')+'.png'})
    console.log(width+' px: anchors valid, no overflow')
  }
  await page.keyboard.press('Tab')
  assert.equal(await page.evaluate(()=>document.activeElement.className), 'skip')
  await page.keyboard.press('Enter')
  assert.equal(new URL(page.url()).hash, '#features')
  await page.click('a[href="#sample"]')
  assert.equal(new URL(page.url()).hash,'#sample')
  await page.click('.sample-controls button')
  await page.waitForSelector('.sample-outcome')
  assert.equal(await page.$eval('.sample-outcome strong', el=>el.textContent),'Booking confirmed · CRM saved')
  await page.click('.system-buttons button:last-child')
  assert.equal(await page.$eval('.system-card h3', el=>el.textContent), 'SQLite')
  await page.goto(new URL('/console',url).href)
  await page.waitForSelector('.connected')
  assert.deepEqual(errors,[])
  console.log('Offline blocked-external showcase, scripted player and console connection passed')
} finally { await browser.close() }
