import React from 'react'
import { bant, bookingTime, formatClock, hero, receivedLanguage, scenarios } from './cockpitData.js'
import { Icon } from './cockpitIcons.jsx'

export function CallPanel({ mic, stage, micLevel, recordingMs, busy, toggleMic, endCall, guide, setGuide, choose }) {
  const next = hero[guide]
  const recording = mic === 'recording'
  return <section id="call-panel" className="cockpit-card call-panel" aria-labelledby="call-title">
    <div className="cockpit-card-head"><Icon name="mic"/><h2 id="call-title">Call controls</h2></div>
    <div className="call-station" data-state={stage.toLowerCase()} style={{ '--mic-scale': 1 + micLevel * .42 }}>
      <div className="call-orb" aria-hidden="true">
        <div className="orb-core"/>
        <div className="orb-wave">
          {[.22,.54,.8,1,.8,.54,.22].map((weight, index) =>
            <i key={index} style={{ transform: 'scaleY(' + (recording ? .17 + micLevel * weight * 1.35 : .26 + weight * .58) + ')' }}/>)}
        </div>
      </div>
      <div className="call-station-controls">
        <p className="call-state" role="status">{stage}{recording && ' · ' + formatClock(recordingMs)}</p>
        <button className="mic" disabled={busy && !recording} type="button" onClick={toggleMic}>
          <Icon name={recording ? 'stop' : 'mic'} size={24}/><span>{({idle: 'Record', starting: 'Opening…', recording: 'Stop', transcribing: 'Transcribing…'})[mic]}</span>
        </button>
        <button className="cockpit-button end-button" disabled={busy} type="button" onClick={endCall}>End conversation</button>
      </div>
    </div>
    <div className="call-scenarios">
      <h3>Quick scenarios</h3>
      {Object.entries(scenarios).map(([group, prompts]) => <div className="scenario" key={group}>
        <span>{group}</span>
        <div>{prompts.map(prompt => <button type="button" className="scenario-chip" key={prompt}
          disabled={busy} onClick={() => choose(prompt)}>{prompt}</button>)}</div>
      </div>)}
      <div className="hero-guide">
        <button type="button" className="cockpit-button" onClick={() => setGuide(guide === null ? 0 : null)}
          aria-expanded={guide !== null}>Run the hero journey</button>
        {guide !== null && (next ? <div className="guide-step">
          <span className="cockpit-muted">Step {guide + 1} of {hero.length} · {next[0]}</span>
          <button type="button" className="scenario-chip guide-next" disabled={busy} onClick={() => {
            if (choose(next[1])) setGuide(guide + 1)
          }}>{next[1]}</button>
        </div> : <p>End the call, then open Insights to review the saved report.</p>)}
      </div>
    </div>
  </section>
}

function ChatMessage({ entry, openSource }) {
  const { role, text, mode, citation, time, language, guarded } = entry
  const slot = bookingTime(mode, text)
  const languageTag = receivedLanguage(text) || language
  return <div className={'message ' + role}>
    <div className="message-meta">
      <b className="message-avatar" aria-hidden="true">{role === 'buyer' ? 'Y' : role === 'notice' ? '!' : 'S'}</b>
      <span>{role === 'buyer' ? 'You' : role === 'notice' ? 'Session' : 'ShelfPilot'}{mode && ' · ' + mode.toUpperCase()}</span>
      {time && <time dateTime={new Date(time).toISOString()}>{new Date(time).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}</time>}
      {languageTag && <span>{languageTag}</span>}
    </div>
    <p>{text}</p>
    {citation && <small><button className="citation-chip" type="button" onClick={() => openSource({ citation, text })}>
      <Icon name="doc" size={15}/>{citation.title}
    </button><span className="sr-only">Source · {citation.source}#{citation.id}</span></small>}
    {!citation && mode === 'knowledge' && <small className="event-note">No source: abstained</small>}
    {(guarded || mode === 'policy') && <small className="event-note">Guardrail · reviewed follow-up used</small>}
    {slot && <article className="booking-receipt" aria-label="Booking receipt">
      <strong><Icon name="ticket"/> Appointment confirmed</strong>
      <div>{slot}</div>
      <small>Receipt ID unavailable in this console</small>
    </article>}
  </div>
}

export function Conversation({ messages, mode, partial, pending, transcript, openSource, composer, voiceNote, voiceError }) {
  return <section id="conversation-panel" className="cockpit-card conversation-panel" aria-labelledby="transcript-title">
    <div className="cockpit-card-head"><Icon name="chat"/><h2 id="transcript-title">Conversation</h2></div>
    <div className="transcript cockpit-log" role="log" aria-live="polite" aria-relevant="additions" aria-label="Transcript messages" ref={transcript}>
      {messages.length === 1 && <div className="cockpit-empty">
        <div className="empty-illustration" aria-hidden="true"><Icon name="chat" size={32}/><i/><i/><i/></div>
        <strong>Say hello or pick a scenario</strong>
        <p>Try a product question to see a source, or book a demo.</p>
      </div>}
      {messages.map((entry, index) => <ChatMessage entry={entry} key={index} openSource={openSource}/>)}
      {partial && <div className="message agent streaming" aria-hidden="true"><span>ShelfPilot · {mode.toUpperCase()}</span><p>{partial}</p></div>}
      {pending && !partial && <div className="typing-indicator" role="status"><i/><i/><i/> ShelfPilot is replying…</div>}
    </div>
    {composer}
    <p className="voice-note">{voiceNote}</p>
    {voiceError && <p role="alert" className="voice-error">{voiceError}</p>}
  </section>
}

function IntelligenceGroup({ title, children, className = '' }) {
  return <section className={'intel-card ' + className} aria-label={title}><h3>{title}</h3>{children}</section>
}

function Sentiment({ report, analyzing }) {
  return <IntelligenceGroup title="Sentiment">
    {report?.sentiment?.length ? <>
      <div className="sentiment-trend" aria-label={'Sentiment by turn: ' + report.sentiment.join(', ')}>
        {report.sentiment.map((label, index) => <span key={index} data-tone={label.toLowerCase()} title={label}/>)}
      </div>
      <p className="intel-value">{report.sentiment.at(-1)}</p>
      <p className="cockpit-muted">Latest saved call</p>
    </> : <AnalysisPending analyzing={analyzing}/>}
  </IntelligenceGroup>
}

function AnalysisPending({ analyzing }) {
  return <div className="analysis-pending" aria-busy={analyzing}>
    <span className={analyzing ? 'analysis-skeleton' : 'analysis-track'} aria-hidden="true"/>
    <p>{analyzing ? 'Analyzing…' : 'Available after the call ends.'}</p>
  </div>
}

function LeadScore({ report, analyzing }) {
  return <IntelligenceGroup title="Lead score">
    {report ? <>
      <p className="intel-value"><span className="rating" data-rating={report.rating}>{report.rating}</span> {report.score}<small>/100</small></p>
      <p className="cockpit-muted">Latest saved call</p>
      <div className="score-track" aria-hidden="true"><i style={{ transform: 'scaleX(' + report.score / 100 + ')' }}/></div>
      <div className="bant-list">{bant.map(([label, reason]) => {
        const captured = report.reasons.includes(reason)
        return <div key={label}><span>{label}</span><span className="bant-bar" aria-hidden="true"><i data-captured={captured}/></span>
          <span className="sr-only">{captured ? 'Signal recorded' : 'No signal recorded'}</span></div>
      })}</div>
      <details><summary>Scoring reasons</summary>{report.reasons.length
        ? <ul>{report.reasons.map(reason => <li key={reason}>{reason}</li>)}</ul>
        : <p>No explicit BANT signal was recorded.</p>}</details>
    </> : <AnalysisPending analyzing={analyzing}/>}
  </IntelligenceGroup>
}

function LeadProfile({ lead, needsConfirmation, confirmed }) {
  const rows = [['Name', lead?.name], ['Company', lead?.company], ['Stores', lead?.store_count, 'store_count'],
    ['Need', lead?.need], ['Objection', lead?.objection], ['Language', ({ en: 'EN', hi: 'HI' })[lead?.language]],
    ['Target date', lead?.target_date, 'target_date']]
  return <IntelligenceGroup title="Lead profile">
    <dl>{rows.map(([label, value, field]) => <div key={label}>
      <dt>{label}</dt><dd key={value || 'empty'} className={value != null ? 'filled-field' : ''}>{value ?? '—'}
      {value != null && confirmed.includes(field) && <span className="confirmed-tick" title="Readback confirmed" aria-label="Readback confirmed"><Icon name="check" size={14}/></span>}</dd>
    </div>)}</dl>
    {needsConfirmation && <p className="pending">Waiting for your confirmation</p>}
  </IntelligenceGroup>
}

function Latency({ latency, voiceInfo }) {
  const rows = [
    ['Transcription', voiceInfo?.sttMs, voiceInfo?.stt],
    ['First text', latency],
    ['TTS first byte', voiceInfo?.ttsFirstByteMs],
    [voiceInfo?.audioMs == null ? 'Playback' : 'Stop to playback', voiceInfo?.audioMs, voiceInfo?.tts],
  ]
  const max = Math.max(1, ...rows.map(row => row[1] ?? 0))
  return <IntelligenceGroup title="Turn latency" className="technical-card">
    <dl>{rows.map(([label, value, source]) => <div className="latency-row" key={label}>
      <dt>{label}</dt><dd>{value == null ? '—' : value.toFixed(label === 'First text' ? 2 : 0) + ' ms'}{source && ' · ' + source}</dd>
      <span className="latency-track" aria-hidden="true"><i style={{transform: 'scaleX(' + ((value ?? 0) / max) + ')'}}/></span>
    </div>)}</dl>
    {voiceInfo && <details><summary>Additional timings</summary><dl>
      <div><dt>Endpoint tail · encode</dt><dd>{voiceInfo.endpointMs.toFixed(0)} · {voiceInfo.encodeMs.toFixed(0)} ms</dd></div>
      <div><dt>Transfer overhead</dt><dd>{voiceInfo.transferMs.toFixed(0)} ms</dd></div>
      {voiceInfo.sentenceMs != null && <div><dt>First approved sentence</dt><dd>{voiceInfo.sentenceMs.toFixed(0)} ms</dd></div>}
      {voiceInfo.audioMs != null && <div><dt>Estimated end to playback</dt><dd>{Math.round(voiceInfo.endpointMs + voiceInfo.audioMs)} ms</dd></div>}
    </dl></details>}
  </IntelligenceGroup>
}

export function Intelligence({ report, analyzing, lead, needsConfirmation, confirmed, latency, voiceInfo, provider, trace, allowFallback, busy, simulate, openRecords, reconnect, status }) {
  return <aside id="intelligence-panel" className="cockpit-card intelligence-panel" aria-labelledby="intelligence-title">
    <div className="cockpit-card-head"><Icon name="pulse"/><h2 id="intelligence-title">Live intelligence</h2></div>
    <div className="intel-stack">
      <div className="record-actions" aria-label="Workspace records">
        {[['crm', 'View demo CRM'], ['bookings', 'Bookings'], ['summary', 'Call summary'], ['insights', 'View insights']].map(([view, label]) =>
          <button type="button" className="cockpit-button" key={view} onClick={() => openRecords(view)}>{label}</button>)}
      </div>
      <Sentiment report={report} analyzing={analyzing}/>
      <LeadScore report={report} analyzing={analyzing}/>
      <LeadProfile lead={lead} needsConfirmation={needsConfirmation} confirmed={confirmed}/>
      <Latency latency={latency} voiceInfo={voiceInfo}/>
      <IntelligenceGroup title="Provider trace" className="technical-card">
        <dl><div><dt>Provider</dt><dd>{provider || '—'}</dd></div></dl>
        {trace.length > 0 && <ol className="trace" aria-label="Provider trace">{trace.map((item, index) => <li key={index}>{item}</li>)}</ol>}
        {allowFallback && <button type="button" className="cockpit-button" disabled={busy} onClick={simulate}>Simulate Gemini failures</button>}
        {status === 'Disconnected' && <button type="button" className="cockpit-button" onClick={reconnect}>Reconnect</button>}
      </IntelligenceGroup>
    </div>
  </aside>
}
