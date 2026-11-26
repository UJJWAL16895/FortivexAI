export function reportMarkdown(call) {
  return [
    '# ShelfPilot call report', '',
    `Lead rating: ${call.rating} (${call.score}/100)`,
    `Booking: ${call.booked ? 'Confirmed' : 'No booking'}`,
    `Sentiment by turn: ${call.sentiment_turns?.length ? call.sentiment_turns.map(item =>
      item.status === 'mock' ? 'Mock (rule-based): ' + item.sentiment : item.sentiment || 'Not analyzed').join(', ')
      : call.sentiment.length ? 'Legacy (source unavailable): ' + call.sentiment.join(', ') : 'Not analyzed'}`, '',
    '## Evidence', ...call.reasons.map(item => '- ' + item), '',
    '## Summary', call.summary, '',
    '## Next action', call.next_action, '',
    '## Follow-up draft', call.follow_up_draft, '',
  ].join('\n')
}

export function downloadReport(call) {
  const url = URL.createObjectURL(new Blob([reportMarkdown(call)], {type: 'text/markdown;charset=utf-8'}))
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = 'shelfpilot-call-report.md'
  anchor.click()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}
