import React from 'react'
import { downloadReport } from './reportExport.js'
import { Icon } from './cockpitIcons.jsx'

export default function CockpitRecords({ view, crm, insights }) {
  if (view === 'crm' || view === 'bookings') {
    if (!crm) return <p className="cockpit-muted">Loading workspace records…</p>
    return <section aria-label={view === 'crm' ? 'Demo CRM' : 'Bookings'} className="records-content">
      <h3>{view === 'crm' ? 'Demo CRM' : 'Bookings'}</h3>
      <p className="cockpit-muted">{crm.leads.length} leads · {crm.bookings.length} bookings</p>
      {view === 'crm' && crm.leads.map(item => <article className="record" key={item.contact}>
        <strong>{item.name || item.contact}</strong>
        {item.name && <p>{item.contact}</p>}
        {item.company && <p>{item.company}</p>}
      </article>)}
      {crm.bookings.map(item => <article className="record" key={item.slot}>
        <strong><Icon name="ticket"/> {item.label}</strong><p>{item.contact}</p>
      </article>)}
      {((view === 'crm' && !crm.leads.length) || (view === 'bookings' && !crm.bookings.length)) &&
        <p className="cockpit-muted">No saved {view === 'crm' ? 'contacts' : 'bookings'} yet.</p>}
    </section>
  }
  if (!insights) return <p className="cockpit-muted">Loading saved analysis…</p>
  const calls = view === 'summary' ? insights.calls.slice(0, 1) : insights.calls
  return <section aria-label={view === 'summary' ? 'Call summary' : 'Call insights'} className="records-content">
    <h3>{view === 'summary' ? 'Latest saved call' : 'Call insights'}</h3>
    {view === 'insights' && <div className="insight-totals">
      <div><b>{insights.totals.calls}</b><span>Analyzed calls</span></div>
      <div><b>{insights.totals.booked_calls}</b><span>Booked</span></div>
      <div><b>{insights.totals.calls ? (insights.totals.booking_rate * 100).toFixed(0) + '%' : '—'}</b><span>Booking rate</span></div>
    </div>}
    {insights.dropped_jobs > 0 && <p>{insights.dropped_jobs} analysis jobs skipped at capacity</p>}
    {!calls.length && <p className="cockpit-muted">End a conversation to generate a report.</p>}
    {calls.map((call, index) => <article className="record" key={index}>
      <h4>{call.rating} · {call.score}/100</h4>
      <p>{call.summary}</p>
      <p>Sentiment by turn · {call.sentiment_turns?.length ? call.sentiment_turns.map(item =>
        item.status === 'mock' ? 'Mock (rule-based): ' + item.sentiment : item.sentiment || 'Not analyzed').join(' → ')
        : call.sentiment.length ? 'Legacy (source unavailable): ' + call.sentiment.join(' → ') : 'Not analyzed'}</p>
      <p><strong>Next action</strong> · {call.next_action}</p>
      <p><strong>Follow-up draft</strong> · {call.follow_up_draft}</p>
      <button type="button" className="cockpit-button" onClick={() => downloadReport(call)}>Export call report</button>
    </article>)}
  </section>
}
