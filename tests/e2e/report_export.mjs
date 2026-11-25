import assert from 'node:assert/strict'
import { reportMarkdown } from '../../frontend/src/reportExport.js'
const report = reportMarkdown({
  rating:'Warm', score:50, booked:true, sentiment:['Neutral','Positive'],
  reasons:['Buyer stated a need.'], summary:'Booked.', next_action:'Review.',
  follow_up_draft:'Thank you for calling.',
})
assert.match(report, /Warm \(50\/100\)/)
assert.match(report, /Booking: Confirmed/)
assert.match(report, /Neutral, Positive/)
assert.match(report, /## Follow-up draft\nThank you for calling\./)
console.log('Derived Markdown export passed')
