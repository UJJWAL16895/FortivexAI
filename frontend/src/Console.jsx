import React, { useEffect, useRef, useState } from 'react'
import { createPlayback, toWav, transcribe } from './voice.js'
import './styles.css'
import { downloadReport } from './reportExport.js'


const prompts = ['How does the multi-store dashboard work?', 'How much does Growth cost?', 'Can I see a demo?']
const initialMessage = {
  role: 'agent',
  text: 'Hi, I’m the ShelfPilot demo agent. What would you like to know about managing inventory across your stores?',
}

export default function App() {
  const [messages, setMessages] = useState([initialMessage])
  const [draft, setDraft] = useState('')
  const [status, setStatus] = useState('Connecting')
  const [pending, setPending] = useState(false)
  const [latency, setLatency] = useState(null)
  const [mode, setMode] = useState('')
  const [configuredMode, setConfiguredMode] = useState('')
  const [provider, setProvider] = useState('')
  const [trace, setTrace] = useState([])
  const [partial, setPartial] = useState('')
  const [allowFallback, setAllowFallback] = useState(false)
  const [mic, setMic] = useState('idle')
  const [micLevel, setMicLevel] = useState(0)
  const [voiceInfo, setVoiceInfo] = useState(null)
  const [voiceError, setVoiceError] = useState('')
  const [voiceLanguage, setVoiceLanguage] = useState('en')
  const [lead, setLead] = useState(null)
  const [crm, setCRM] = useState(null)
  const [crmError, setCRMError] = useState('')
  const [insights, setInsights] = useState(null)
  const [insightsError, setInsightsError] = useState('')
  const [needsConfirmation, setNeedsConfirmation] = useState(false)
  const [connection, setConnection] = useState(0)
  const socket = useRef(null)
  const transcript = useRef(null)
  const input = useRef(null)
  const recording = useRef(null)
  const context = useRef(null)
  const playback = useRef(null)
  const replyMode = useRef('mock')
  const voiceSentAt = useRef(null)

  useEffect(() => {
    const url = new URL('/ws/text', window.location.href)
    url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:'
    const client = new WebSocket(url)
    socket.current = client
    client.onmessage = ({ data }) => {
      const event = JSON.parse(data)
      if (event.type === 'ready') {
        setStatus('Connected')
        setMode(event.mode)
        setConfiguredMode(event.mode)
        setProvider(event.mode === 'mock' ? 'Deterministic mock' : 'Gemini')
        setAllowFallback(event.allow_fallback_demo)
        setLead(null)
        setNeedsConfirmation(false)
        return
      }
      if (event.type === 'profile') {
        setLead(event.profile)
        setNeedsConfirmation(Boolean(event.pending))
        return
      }
      if (event.type === 'provider') {
        if (event.status !== 'trying') {
          setTrace(items => [...items, `${event.provider} ${event.status}${event.code ? ` (${event.code})` : ''}${event.quota ? ` · ${event.quota}` : ''}`])
        }
        if (event.status === 'active') {
          setProvider(event.model)
          replyMode.current = event.provider === 'mock' ? 'mock' : 'live'
          if (!['policy', 'session', 'knowledge', 'booking'].includes(event.provider)) setMode(replyMode.current)
        }
        return
      }
      if (event.type === 'delta') {
        setPartial(text => text + event.text)
        return
      }
      if (event.type === 'first_text') {
        setLatency(event.latency_ms)
        return
      }
      if (event.type === 'sentence') {
        if (voiceSentAt.current != null) {
          const sentenceMs = performance.now() - voiceSentAt.current
          voiceSentAt.current = null
          setVoiceInfo(info => info ? { ...info, sentenceMs } : info)
        }
        playback.current?.enqueue(event.text, replyMode.current)
        return
      }
      if (event.type !== 'reply' && event.type !== 'error') return
      setMessages(items => [...items, {
        role: event.type === 'error' ? 'notice' : 'agent',
        text: event.text,
        mode: event.mode,
        citation: event.citation,
      }])
      setPartial('')
      if (event.type === 'reply') setLatency(event.latency_ms)
      setPending(false)
      if (event.mode === 'booking') setCRM(null)
    }
    client.onclose = () => {
      playback.current?.stop()
      playback.current = null
      setStatus('Disconnected')
      setPending(false)
      setPartial('')
    }
    return () => {
      client.onclose = null
      client.onmessage = null
      client.close()
    }
  }, [connection])

  useEffect(() => () => {
    recording.current?.stream.getTracks().forEach(track => track.stop())
    playback.current?.stop()
    context.current?.close()
  }, [])

  useEffect(() => {
    transcript.current.scrollTop = transcript.current.scrollHeight
  }, [messages, pending, partial])

  function send(text, simulateFailure = false, voicePlayback = null) {
    const message = text.trim()
    if (!message || pending || socket.current?.readyState !== WebSocket.OPEN) return false
    playback.current?.stop()
    playback.current = voicePlayback
    voiceSentAt.current = voicePlayback ? performance.now() : null
    socket.current.send(JSON.stringify({ text: message, simulate_failure: simulateFailure }))
    setTrace([])
    setLatency(null)
    setMessages(items => [...items, { role: 'buyer', text: message }])
    setDraft('')
    setPending(true)
    input.current.focus()
    return true
  }

  async function toggleMic() {
    if (recording.current?.state === 'recording') {
      recording.current.stop()
      return
    }
    if (mic !== 'idle') return
    setMic('starting')
    setVoiceError('')
    setVoiceInfo(null)
    playback.current?.stop()
    let stream
    try {
      if (!window.MediaRecorder || !navigator.mediaDevices?.getUserMedia) throw Error()
      context.current ??= new AudioContext()
      await context.current.resume()
      stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const meterSource = context.current.createMediaStreamSource(stream)
      const analyser = context.current.createAnalyser()
      meterSource.connect(analyser)
      const samples = new Uint8Array(analyser.fftSize)
      let levelFrame
      const drawLevel = () => {
        analyser.getByteTimeDomainData(samples)
        const level = Math.max(...samples.map(sample => Math.abs(sample - 128))) / 128
        setMicLevel(level)
        levelFrame = requestAnimationFrame(drawLevel)
      }
      const recorder = new MediaRecorder(stream)
      const parts = []
      recording.current = recorder
      recorder.ondataavailable = event => { if (event.data.size) parts.push(event.data) }
      recorder.onstop = async () => {
        cancelAnimationFrame(levelFrame)
        meterSource.disconnect()
        setMicLevel(0)
        const stoppedAt = performance.now()
        clearTimeout(timer)
        stream.getTracks().forEach(track => track.stop())
        recording.current = null
        setMic('transcribing')
        try {
          const { bytes, endpointMs } = await toWav(parts, recorder.mimeType, context.current)
          const encodedAt = performance.now()
          const transcript = await transcribe(bytes, voiceLanguage)
          setVoiceInfo({ stt: transcript.provider, sttMs: transcript.latency_ms,
            endpointMs, encodeMs: encodedAt - stoppedAt, transferMs: transcript.transferMs })
          const voicePlayback = createPlayback(context.current, (source, ttsFirstByteMs) => setVoiceInfo(info => ({
            ...info, tts: info.tts ?? source,
            ttsFirstByteMs: info.ttsFirstByteMs ?? ttsFirstByteMs,
            audioMs: info.audioMs ?? Math.round(performance.now() - stoppedAt),
          })), setVoiceError)
          if (!send(transcript.text, false, voicePlayback)) setVoiceError('Reconnect and record again.')
        } catch (error) {
          setVoiceError(error.message || 'Recording failed. Try typing your message.')
        } finally {
          setMic('idle')
        }
      }
      recorder.start()
      drawLevel()
      const timer = setTimeout(() => {
        if (recorder.state === 'recording') recorder.stop()
      }, 12000)
      setMic('recording')
    } catch {
      stream?.getTracks().forEach(track => track.stop())
      recording.current = null
      setVoiceError('Microphone unavailable. Check browser permission or type your message.')
      setMic('idle')
    }
  }

  return (
    <>
      <header className="header">
        <div className="brand"><span className="brand-mark" aria-hidden="true">▥</span><span>ShelfPilot<small>SALES CONSOLE</small></span></div>
        <span className="mode"><span aria-hidden="true" /> {mode ? mode.toUpperCase() : 'CONNECTING'}</span>
      </header>
      <main>
        <section className="intro">
          <p className="eyebrow">WORKSPACE / SALES DEMO</p>
          <h1>Sales conversation</h1>
          <p>Try an inbound inventory inquiry as a retail buyer.</p>
        </section>
        <div className="workspace">
          <section className="panel chat" aria-labelledby="transcript-title">
            <div className="panel-header"><h2 id="transcript-title">Transcript</h2><span className={status === 'Connected' ? 'connected' : ''} role="status">{status}</span></div>
            <div className="transcript" role="log" aria-label="Transcript messages" ref={transcript}>
              {messages.map(({ role, text, mode: replyMode, citation }, index) => (
                <div className={`message ${role}`} key={index}>
                  <span>{role === 'buyer' ? 'You' : role === 'notice' ? 'Session' : 'ShelfPilot'}{replyMode && ` · ${replyMode.toUpperCase()}`}</span>
                  <p>{text}</p>
                  {citation && <small>Source · {citation.title} · {citation.source}#{citation.id}</small>}
                </div>
              ))}
              {partial && <div className="message agent"><span>ShelfPilot · {mode.toUpperCase()}</span><p>{partial}</p></div>}
              {pending && !partial && <p role="status" className="pending">ShelfPilot is replying…</p>}
            </div>
            <form onSubmit={event => { event.preventDefault(); if (mic === 'idle') send(draft) }}>
              <label className="sr-only" htmlFor="message">Message</label>
              <input id="message" ref={input} placeholder="Ask about inventory…" maxLength={500} value={draft} onChange={event => setDraft(event.target.value)} />
              <button className="send" disabled={!draft.trim() || pending || mic !== 'idle' || status !== 'Connected'} type="submit">Send <span aria-hidden="true">↑</span></button>
              <button className="mic" disabled={pending || status !== 'Connected' || !['idle', 'recording'].includes(mic)} type="button" onClick={toggleMic}>{({idle: 'Record', starting: 'Opening…', recording: 'Stop', transcribing: 'Transcribing…'})[mic]}</button>
            </form>
            {mic === 'recording' && <div className="mic-waveform" aria-hidden="true">
              {[.4,.65,.85,1,.85,.65,.4].map((factor, index) =>
                <i key={index} style={{transform: 'scaleY(' + (.12 + factor * micLevel * .88) + ')'}} />)}
            </div>}
            <p className="voice-note">{configuredMode === 'live' ? 'Microphone audio may be sent to Gemini for transcription.' : 'Mock voice uses a scripted transcript.'}</p>
            {voiceError && <p role="alert" className="voice-error">{voiceError}</p>}
          </section>
          <aside className="panel sidebar">
            <section aria-labelledby="session-title">
              <h2 id="session-title">Session</h2>
              <dl>
                <div><dt>Provider</dt><dd>{provider || '—'}</dd></div>
                <div><dt>First text</dt><dd>{latency === null ? '—' : `${latency.toFixed(2)} ms`}</dd></div>
                {voiceInfo && <div><dt>Transcription</dt><dd>{voiceInfo.stt} · {voiceInfo.sttMs.toFixed(0)} ms</dd></div>}
                {voiceInfo && <div><dt>Endpoint tail · encode</dt><dd>{voiceInfo.endpointMs.toFixed(0)} · {voiceInfo.encodeMs.toFixed(0)} ms</dd></div>}
                {voiceInfo && <div><dt>Transfer overhead</dt><dd>{voiceInfo.transferMs.toFixed(0)} ms</dd></div>}
                {voiceInfo?.sentenceMs != null && <div><dt>First approved sentence</dt><dd>{voiceInfo.sentenceMs.toFixed(0)} ms</dd></div>}
                {voiceInfo?.ttsFirstByteMs != null && <div><dt>TTS first byte</dt><dd>{voiceInfo.ttsFirstByteMs.toFixed(0)} ms</dd></div>}
                {voiceInfo?.tts && <div><dt>Stop to playback</dt><dd>{voiceInfo.audioMs} ms · {voiceInfo.tts}</dd></div>}
                {voiceInfo?.tts && <div><dt>Estimated end to playback</dt><dd>{Math.round(voiceInfo.endpointMs + voiceInfo.audioMs)} ms</dd></div>}
              </dl>
              <label htmlFor="voice-language">Microphone language </label>
              <select id="voice-language" value={voiceLanguage} onChange={e => setVoiceLanguage(e.target.value)} disabled={mic !== 'idle'}>
                <option value="en">English</option><option value="hi">Hindi</option>
              </select>
              {trace.length > 0 && <ul className="trace" aria-label="Provider trace">{trace.map(item => <li key={item}>{item}</li>)}</ul>}
              {allowFallback && <button className="suggestion" disabled={pending || mic !== 'idle' || status !== 'Connected'} onClick={() => send(prompts[0], true)}>Simulate Gemini failures</button>}
              {status === 'Disconnected' && <button className="suggestion" onClick={() => { setStatus('Connecting'); setConnection(value => value + 1) }}>Reconnect</button>}
            </section>
            {lead && (needsConfirmation || lead.name || lead.company || lead.need || lead.store_count || lead.target_date) &&
              <section className="prompts" aria-label="Lead profile">
                <h2>Lead profile</h2>
                <dl>
                  {lead.name && <div><dt>Name</dt><dd>{lead.name}</dd></div>}
                  {lead.company && <div><dt>Company</dt><dd>{lead.company}</dd></div>}
                  {lead.need && <div><dt>Need</dt><dd>{lead.need}</dd></div>}
                  {lead.store_count && <div><dt>Stores</dt><dd>{lead.store_count}</dd></div>}
                  {lead.target_date && <div><dt>Target date</dt><dd>{lead.target_date}</dd></div>}
                </dl>
                {needsConfirmation && <p className="pending">Waiting for your confirmation</p>}
              </section>}
            <section aria-labelledby="prompts-title" className="prompts">
              <h2 id="prompts-title">Try asking</h2>
              {prompts.map(prompt => <button className="suggestion" key={prompt} disabled={pending || mic !== 'idle' || status !== 'Connected'} onClick={() => send(prompt)}>{prompt}<span aria-hidden="true">↗</span></button>)}
              <button className="suggestion" disabled={pending || mic !== 'idle' || status !== 'Connected'} onClick={() => send('Book a demo')}>Book a demo</button>
              <button className="suggestion" onClick={async () => {
                setCRMError('')
                try {
                  const response = await fetch('/api/crm')
                  if (!response.ok) throw Error('CRM unavailable.')
                  setCRM(await response.json())
                } catch { setCRMError('CRM unavailable.') }
              }}>View demo CRM</button>
              <button className="suggestion" disabled={pending || mic !== 'idle' || status !== 'Connected'}
                onClick={() => socket.current.send(JSON.stringify({ text: 'End conversation', end_call: true }))}>End conversation</button>
              <button className="suggestion" onClick={async () => {
                setInsightsError('')
                try {
                  const response = await fetch('/api/insights')
                  if (!response.ok) throw Error('Insights unavailable.')
                  setInsights(await response.json())
                } catch { setInsightsError('Insights unavailable.') }
              }}>View insights</button>
              {crmError && <p role="alert">{crmError}</p>}
              {insightsError && <p role="alert">{insightsError}</p>}
              {crm && <section aria-label="Demo CRM">
                <h3>Demo CRM</h3>
                <p>{crm.leads.length} leads · {crm.bookings.length} bookings</p>
                <ul>{crm.leads.map(item => <li key={item.contact}>{item.name || item.contact}{item.company ? ' · ' + item.company : ''}</li>)}</ul>
                <ul>{crm.bookings.map(item => <li key={item.slot}>{item.contact} · {item.label}</li>)}</ul>
              </section>}
              {insights && <section aria-label="Call insights">
                <h3>Call insights</h3>
                <p>{insights.totals.booked_calls} of {insights.totals.calls} analyzed calls booked · {(insights.totals.booking_rate * 100).toFixed(0)}%</p>
                {insights.dropped_jobs > 0 && <p>{insights.dropped_jobs} analysis jobs skipped at capacity</p>}
                {insights.calls.map((call, index) => <article key={index}>
                  <h4>{call.rating} · {call.score}/100</h4>
                  <p>{call.summary}</p>
                  {call.reasons.length > 0 && <ul>{call.reasons.map(reason => <li key={reason}>{reason}</li>)}</ul>}
                  <small>Sentiment by turn · {call.sentiment.join(' → ')}</small>
                  <p>Next action · {call.next_action}</p>
                  <p>Follow-up draft · {call.follow_up_draft}</p>
                  <button className="suggestion" onClick={() => downloadReport(call)}>Export call report</button>
                </article>)}
              </section>}
            </section>
          </aside>
        </div>
      </main>
    </>
  )
}
