import React, { lazy, Suspense, useEffect, useRef, useState } from 'react'
import { createPlayback, toWav, transcribe } from './voice.js'
import { CallPanel, Conversation, Intelligence } from './CockpitPanels.jsx'
import { bookingTime, formatClock, navigation, scenarios } from './cockpitData.js'
import { Icon } from './cockpitIcons.jsx'
import './cockpit.css'

const Records = lazy(() => import('./CockpitRecords.jsx'))
const MODE_PREFERENCE = 'shelfpilot:preferred-mode'
const initialMessage = {
  role: 'agent',
  text: 'Hi, I’m the ShelfPilot demo agent. What would you like to know about managing inventory across your stores?',
}

export default function App() {
  const [messages, setMessages] = useState([initialMessage])
  const [draft, setDraft] = useState('')
  const [status, setStatus] = useState('Connecting')
  const [publicMode, setPublicMode] = useState(null)
  const [accessCode, setAccessCode] = useState('')
  const [accessError, setAccessError] = useState('')
  const [pending, setPending] = useState(false)
  const [latency, setLatency] = useState(null)
  const [mode, setMode] = useState('')
  const [configuredMode, setConfiguredMode] = useState('')
  const [modePhase, setModePhase] = useState('')
  const [liveAllowed, setLiveAllowed] = useState(false)
  const [liveModel, setLiveModel] = useState('')
  const [liveFirstText, setLiveFirstText] = useState(null)
  const [probeMs, setProbeMs] = useState(null)
  const [quota, setQuota] = useState(null)
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
  const [presenter, setPresenter] = useState(false)
  const [tab, setTab] = useState('conversation')
  const [guide, setGuide] = useState(null)
  const [drawer, setDrawer] = useState(null)
  const [toast, setToast] = useState('')
  const [confirmed, setConfirmed] = useState([])
  const [speaking, setSpeaking] = useState(false)
  const [elapsed, setElapsed] = useState(0)
  const [recordingMs, setRecordingMs] = useState(0)
  const [analyzing, setAnalyzing] = useState(false)
  const [report, setReport] = useState(null)
  const [liveAnalysis, setLiveAnalysis] = useState(null)
  const nextTurn = useRef(0)
  const socket = useRef(null)
  const transcript = useRef(null)
  const input = useRef(null)
  const recording = useRef(null)
  const context = useRef(null)
  const playback = useRef(null)
  const replyMode = useRef('mock')
  const voiceSentAt = useRef(null)
  const dialog = useRef(null)
  const callStarted = useRef(null)
  const recordingStarted = useRef(null)
  const confirmationKeys = useRef([])
  const profileSnapshot = useRef('')
  const callVersion = useRef(0)
  const ending = useRef(false)
  const policyUsed = useRef(false)
  const voiceSession = useRef(null)
  const activeMode = useRef('')

  useEffect(() => {
    const tick = () => {
      if (callStarted.current !== null) setElapsed(performance.now() - callStarted.current)
      if (recordingStarted.current !== null) setRecordingMs(performance.now() - recordingStarted.current)
    }
    const timer = setInterval(tick, 250)
    return () => clearInterval(timer)
  }, [])

  useEffect(() => {
    if (drawer && !dialog.current.open) dialog.current.showModal()
  }, [drawer])

  useEffect(() => {
    if (!toast) return
    const timer = setTimeout(() => setToast(''), 3200)
    return () => clearTimeout(timer)
  }, [toast])

  useEffect(() => {
    fetch('/api/public-status').then(response => response.json()).then(setPublicMode).catch(() => {})
  }, [])

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
        activeMode.current = event.mode
        voiceSession.current = event.voice_session
        setLiveAllowed(Boolean(event.live_allowed))
        setLiveModel(event.model || '')
        setLiveFirstText(null)
        setProbeMs(null)
        setQuota(event.quota ?? null)
        setProvider(event.mode === 'mock' ? 'Deterministic mock' : 'Gemini')
        setAllowFallback(event.allow_fallback_demo)
        setLead(null)
        setLiveAnalysis(null)
        setNeedsConfirmation(false)
        try {
          const choice = localStorage.getItem(MODE_PREFERENCE)
          if (event.live_allowed && (choice === 'live' || (choice === 'mock' && choice !== event.mode))) {
            setModePhase(choice === 'live' ? 'checking' : 'switching')
            client.send(JSON.stringify({ mode: choice }))
          }
        } catch {
          // Storage can be disabled. The server default still works.
        }
        return
      }
      if (event.type === 'quota') {
        setQuota(event.quota)
        return
      }
      if (event.type === 'mode_status') {
        setQuota(event.quota)
        if (event.probe_ms != null) setProbeMs(event.probe_ms)
        if (['checking', 'warming'].includes(event.phase)) {
          setModePhase(event.phase)
          if (event.model) setLiveModel(event.model)
          return
        }
        setModePhase('')
        if (activeMode.current !== event.mode) {
          const time = Date.now()
          const label = new Date(time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          setMessages(items => [...items, { role: 'divider', text: 'Switched to ' + event.mode.toUpperCase() + ' at ' + label }])
          setLiveFirstText(null)
          setProvider(event.model || 'Deterministic mock')
        }
        activeMode.current = event.mode
        setConfiguredMode(event.mode)
        setMode(event.mode)
        if (event.model || event.phase !== 'failed') setLiveModel(event.model || '')
        if (['ready', 'quota', 'unavailable'].includes(event.phase)) {
          try {
            localStorage.setItem(MODE_PREFERENCE, event.mode)
          } catch {
            // The mode remains confirmed for this connection.
          }
        }
        if (event.message) setToast(event.message)
        return
      }
      if (event.type === 'profile') {
        setLead(event.profile)
        setNeedsConfirmation(Boolean(event.pending))
        const snapshot = JSON.stringify(event.profile)
        if (profileSnapshot.current && snapshot !== profileSnapshot.current) setToast('Lead profile updated.')
        profileSnapshot.current = snapshot
        if (event.pending) confirmationKeys.current = Object.keys(event.pending).filter(key => event.pending[key] != null)
        return
      }
      if (event.type === 'analysis') {
        setMessages(items => items.map(item => item.turnId === event.turn_id
          ? { ...item, analysis: event } : item))
        if (['analyzed', 'mock'].includes(event.status)) setLiveAnalysis({ score: event.score, rating: event.rating, reasons: event.reasons, status: event.status })
        return
      }
      if (event.type === 'provider') {
        if (event.provider === 'policy' && event.status === 'active') policyUsed.current = true
        if (event.status !== 'trying') {
          setTrace(items => [...items, `${event.provider} ${event.status}${event.code ? ` (${event.code})` : ''}${event.quota ? ` · ${event.quota}` : ''}`])
        }
        if (event.status === 'failed' || event.status === 'fallback') setToast(event.provider + ' failed. Checking the fallback.')
        if (event.status === 'active') {
          setProvider(event.model)
          if (event.provider === 'Gemini A' || event.provider === 'Gemini B') {
            setLiveModel(event.model)
            replyMode.current = 'live'
          } else if (event.provider === 'mock') {
            replyMode.current = 'mock'
          }
        }
        return
      }
      if (event.type === 'delta') {
        setPartial(text => text + event.text)
        return
      }
      if (event.type === 'first_text') {
        setLatency(event.latency_ms)
        if (replyMode.current === 'live') setLiveFirstText(event.latency_ms)
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
      if (event.type === 'error') {
        setMessages(items => items.map(item => item.turnId === nextTurn.current && !item.analysis
          ? { ...item, analysis: { status: 'not_analyzed' } } : item))
      }
      const guarded = policyUsed.current
      setMessages(items => [...items, {
        role: event.type === 'error' ? 'notice' : 'agent',
        text: event.text,
        mode: event.mode,
        citation: event.citation,
        source: event.origin === 'gemini' || event.mode === 'live' ? 'Gemini ' + event.provider
          : event.origin === 'approved' ? 'Scripted/approved phrase'
          : event.citation ? 'Knowledge card' : event.mode === 'mock' ? 'Mock' : 'Scripted/approved phrase',
        passage: event.passage,
        booking: event.booking,
        approvedFollowUp: event.approved_follow_up,
        time: Date.now(),
        guarded,
        execution: event.mode === 'mock' || event.mode === 'live' ? event.mode : activeMode.current,
      }])
      setPartial('')
      if (event.type === 'reply') setLatency(event.latency_ms)
      setPending(false)
      if (event.mode === 'booking') {
        setCRM(null)
        if (bookingTime(event.mode, event.text)) setToast('Appointment confirmed.')
      }
      if (/^(Thanks, I’ve confirmed|धन्यवाद, मैंने ये बातें)/u.test(event.text)) {
        const fields = confirmationKeys.current
        setConfirmed(current => [...new Set([...current, ...fields])])
      }
    }
    client.onclose = () => {
      playback.current?.stop()
      playback.current = null
      setStatus('Disconnected')
      setModePhase('')
      voiceSession.current = null
      setPending(false)
      setPartial('')
      setSpeaking(false)
      if (callStarted.current !== null) setElapsed(performance.now() - callStarted.current)
      callStarted.current = null
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
    if (messages.length > 1) transcript.current.scrollTop = transcript.current.scrollHeight
  }, [messages, pending, partial, tab])

  function send(text, simulateFailure = false, voicePlayback = null) {
    const message = text.trim()
    if (!message || pending || socket.current?.readyState !== WebSocket.OPEN) return false
    playback.current?.stop()
    setSpeaking(false)
    playback.current = voicePlayback
    if (!voicePlayback) {
      setVoiceInfo(null)
      setVoiceError('')
    }
    voiceSentAt.current = voicePlayback ? performance.now() : null
    policyUsed.current = false
    replyMode.current = activeMode.current || 'mock'
    callStarted.current ??= performance.now()
    const turnId = simulateFailure ? undefined : ++nextTurn.current
    socket.current.send(JSON.stringify({ text: message, simulate_failure: simulateFailure, turn_id: turnId }))
    setTrace([])
    setLatency(null)
    setMessages(items => [...items, { role: 'buyer', text: message, time: Date.now(), turnId,
      language: voicePlayback ? voiceLanguage.toUpperCase() + ' · mic' : null }])
    setDraft('')
    setPending(true)
    setTab('conversation')
    if (input.current.getClientRects().length) input.current.focus()
    else requestAnimationFrame(() => input.current?.focus())
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
    setSpeaking(false)
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
        recordingStarted.current = null
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
          const transcript = await transcribe(bytes, voiceLanguage, voiceSession.current)
          setVoiceInfo({ stt: transcript.provider, sttMs: transcript.latency_ms,
            endpointMs, encodeMs: encodedAt - stoppedAt, transferMs: transcript.transferMs })
          const voicePlayback = createPlayback(context.current, (source, ttsFirstByteMs) => setVoiceInfo(info => ({
            ...info, tts: info.tts ?? source,
            ttsFirstByteMs: info.ttsFirstByteMs ?? ttsFirstByteMs,
            audioMs: info.audioMs ?? Math.round(performance.now() - stoppedAt),
          })), setVoiceError, setSpeaking, voiceSession.current)
          if (!send(transcript.text, false, voicePlayback)) setVoiceError('Reconnect and record again.')
        } catch (error) {
          setVoiceError(error.message || 'Recording failed. Try typing your message.')
        } finally {
          setMic('idle')
        }
      }
      recorder.start()
      callStarted.current ??= performance.now()
      recordingStarted.current = performance.now()
      setRecordingMs(0)
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


  function reconnect() {
    setStatus('Connecting')
    setConnection(value => value + 1)
  }

  function chooseMode(target) {
    if (target === configuredMode || modePhase || pending || mic !== 'idle' ||
        socket.current?.readyState !== WebSocket.OPEN || (target === 'live' && !liveAllowed)) return
    playback.current?.stop()
    setSpeaking(false)
    setModePhase(target === 'live' ? 'checking' : 'switching')
    setProbeMs(null)
    socket.current.send(JSON.stringify({ mode: target }))
  }

  function resetCall() {
    callVersion.current += 1
    ending.current = false
    callStarted.current = null
    voiceSentAt.current = null
    policyUsed.current = false
    confirmationKeys.current = []
    profileSnapshot.current = ''
    playback.current?.stop()
    playback.current = null
    setMessages([initialMessage])
    setElapsed(0)
    setDraft('')
    setPartial('')
    setPending(false)
    setVoiceInfo(null)
    setVoiceError('')
    setSpeaking(false)
    setLatency(null)
    setTrace([])
    setLead(null)
    setNeedsConfirmation(false)
    setConfirmed([])
    setCRM(null)
    setInsights(null)
    setCRMError('')
    setInsightsError('')
    setAnalyzing(false)
    setReport(null)
    setLiveAnalysis(null)
    setToast('')
    setGuide(null)
    setTab('conversation')
    reconnect()
  }

  async function endCall() {
    if (ending.current) return
    const client = socket.current
    const version = callVersion.current
    ending.current = true
    setAnalyzing(true)
    let before
    try {
      const snapshot = await fetchWorkspace('insights', AbortSignal.timeout(1600))
      before = snapshot.totals.calls
    } catch {
      // The existing end command still works if the analytics read is unavailable.
    }
    if (version !== callVersion.current) return
    if (client?.readyState === WebSocket.OPEN) client.send(JSON.stringify({ text: 'End conversation', end_call: true }))
    try {
      if (before == null) return
      for (const pause of [180, 300, 450, 700, 1000]) {
        await new Promise(resolve => setTimeout(resolve, pause))
        if (version !== callVersion.current) return
        const result = await fetchWorkspace('insights', AbortSignal.timeout(1500))
        if (result.totals.calls > before) {
          if (version !== callVersion.current) return
          setInsights(result)
          setReport(result.calls[0] ?? null)
          setToast('A saved call report is available.')
          return
        }
      }
    } catch {
      // The operator can reopen Insights if the bounded refresh did not complete.
    } finally {
      if (version === callVersion.current) {
        ending.current = false
        setAnalyzing(false)
      }
    }
  }

  async function fetchWorkspace(endpoint, signal) {
    const response = await fetch('/api/' + endpoint, { signal })
    if (!response.ok) throw Error((endpoint === 'crm' ? 'CRM' : 'Insights') + ' unavailable.')
    return response.json()
  }

  async function openRecords(view) {
    setDrawer({ view })
    const wantsCRM = ['crm', 'bookings'].includes(view)
    const setError = wantsCRM ? setCRMError : setInsightsError
    setError('')
    const version = callVersion.current
    try {
      const data = await fetchWorkspace(wantsCRM ? 'crm' : 'insights')
      if (version === callVersion.current) (wantsCRM ? setCRM : setInsights)(data)
    } catch (error) {
      if (version === callVersion.current) setError(error.message)
    }
  }

  async function unlock(event) {
    event.preventDefault()
    setAccessError('')
    try {
      const response = await fetch('/api/unlock', { method: 'POST', body: accessCode })
      if (!response.ok) throw Error(response.status === 429 ? 'Demo request limit reached.' : 'Access code rejected.')
      setAccessCode('')
      reconnect()
    } catch (error) {
      setAccessError(error.message || 'Unable to unlock.')
    }
  }

  const stage = mic === 'recording' ? 'Listening'
    : mic === 'transcribing' ? 'Transcribing'
    : mic === 'starting' ? 'Opening microphone'
    : speaking ? 'Speaking'
    : voiceError ? 'Error'
    : pending ? 'Thinking' : 'Idle'
  const busy = pending || mic !== 'idle' || status !== 'Connected' || analyzing || Boolean(modePhase)
  const composer = <form className="cockpit-composer" onSubmit={event => {
    event.preventDefault()
    if (!busy) send(draft)
  }}>
    <label className="sr-only" htmlFor="message">Message</label>
    <input id="message" ref={input} placeholder="Ask about inventory…" maxLength={500} value={draft} onChange={event => setDraft(event.target.value)}/>
    <button className="send" disabled={!draft.trim() || busy} type="submit">Send <Icon name="send" size={16}/></button>
  </form>

  function moveTab(event, index) {
    const order = ['conversation', 'call', 'intelligence']
    const offset = { ArrowLeft: -1, ArrowRight: 1 }[event.key]
    const next = offset ? (index + offset + order.length) % order.length
      : event.key === 'Home' ? 0 : event.key === 'End' ? order.length - 1 : null
    if (next === null) return
    event.preventDefault()
    setTab(order[next])
    document.getElementById('cockpit-tab-' + order[next]).focus()
  }

  return <div className="cockpit" data-tab={tab} data-presenter={presenter}>
    <a className="cockpit-skip" href="#cockpit-main">Skip to console</a>
    <header className="cockpit-header">
      <a className="cockpit-brand" href="/"><span aria-hidden="true"><Icon name="pulse" size={23}/></span>ShelfPilot</a>
      <nav aria-label="ShelfPilot">{navigation.map(([id, label]) =>
        <a href={'/#' + id} key={id} aria-current={id === 'live' ? 'location' : undefined}>{label}</a>)}</nav>
      <div className="cockpit-status">
        <span className="connection-status" role="status"><i className={status === 'Connected' ? 'connected' : ''}/>{status}</span>
        <div className="live-toggle" role="group" aria-label="Provider mode"
          title="LIVE uses real Gemini replies (free tier, rate limited). MOCK is deterministic.">
          {['mock', 'live'].map(target => <button key={target} type="button" data-choice={target}
            aria-pressed={configuredMode === target} disabled={busy || (target === 'live' && !liveAllowed)}
            onClick={() => chooseMode(target)}>{target.toUpperCase()}</button>)}
        </div>
        <span className="mode sr-only" data-mode={mode}>{mode ? mode.toUpperCase() : 'CONNECTING'}</span>
        <label className="language-picker"><span className="sr-only">Microphone language</span>
          <select id="voice-language" value={voiceLanguage} onChange={e => setVoiceLanguage(e.target.value)} disabled={mic !== 'idle'}>
            <option value="en">EN · English</option><option value="hi">हिं · Hindi</option>
          </select>
        </label>
        <span className="call-clock" aria-label={'Call duration ' + formatClock(elapsed)}>{formatClock(elapsed)}</span>
      </div>
    </header>
    <div className="mock-ribbon mode-ribbon" data-state={modePhase || configuredMode} role="status">
      {modePhase === 'checking' ? <><b>CHECKING</b> Checking Gemini…</>
        : modePhase === 'warming' ? <><b>WARMING</b> Warming up voice…</>
        : modePhase === 'switching' ? 'Switching to mock…'
        : configuredMode === 'live' ? <><b>LIVE</b> {liveModel} · Latest Gemini first text {liveFirstText == null ? '—' : liveFirstText.toFixed(2) + ' ms'}</>
        : configuredMode === 'mock' ? 'Mock mode: deterministic replies. Free conversation requires LIVE.' : 'Connecting to ShelfPilot…'}
      {probeMs != null && <span>Readiness · {liveModel} · {probeMs.toFixed(2)} ms</span>}
      {quota && <span title="Local process counter for provider requests over the last 24 hours">Live calls used today: {quota.used} / {quota.cap}</span>}
      {publicMode?.public && !liveAllowed && <span>{publicMode.locked && status !== 'Connected' ? 'Enter the evaluator access code to connect.' : 'Public live switching is disabled.'}</span>}
    </div>
    {publicMode?.public && <aside className="public-mode">
      <strong>Public preview · {publicMode.mode.toUpperCase()}</strong> Use fictional data.
      {publicMode.locked && status !== 'Connected' && <form onSubmit={unlock}>
        <label htmlFor="public-code">Evaluator access code</label>
        <input id="public-code" type="password" value={accessCode} maxLength={256} onChange={e => setAccessCode(e.target.value)} required/>
        <button className="cockpit-button">Unlock</button>
        {accessError && <p role="alert">{accessError}</p>}
      </form>}
    </aside>}
    <main id="cockpit-main" className="cockpit-main">
      <div className="cockpit-title">
        <div><p className="cockpit-kicker">SHELFPILOT SALES CONSOLE</p><h1>Live Call Cockpit</h1></div>
        <div className="cockpit-tools">
          <button type="button" className="cockpit-button" aria-pressed={presenter} onClick={() => setPresenter(value => !value)}>
            <Icon name="screen"/> Presenter mode
          </button>
          <button type="button" className="cockpit-button" disabled={mic !== 'idle'} onClick={resetCall}>
            <Icon name="refresh"/> Reset call
          </button>
        </div>
      </div>
      <div className="cockpit-tabs" role="tablist" aria-label="Cockpit panels">
        {[['conversation', 'Conversation'], ['call', 'Call'], ['intelligence', 'Intelligence']].map(([id, label], index) =>
          <button type="button" role="tab" id={'cockpit-tab-' + id} aria-controls={id + '-panel'} key={id}
            aria-selected={tab === id} tabIndex={tab === id ? 0 : -1} onClick={() => setTab(id)}
            onKeyDown={event => moveTab(event, index)}>{label}</button>)}
      </div>
      <div className="cockpit-grid">
        <CallPanel mic={mic} stage={stage} micLevel={micLevel} recordingMs={recordingMs} busy={busy}
          toggleMic={toggleMic} endCall={endCall} guide={guide} setGuide={setGuide} choose={send}/>
        <Conversation messages={messages} mode={mode} partial={partial} pending={pending}
          transcript={transcript} openSource={setDrawer} composer={composer}
          voiceNote={configuredMode === 'live' ? 'Microphone audio may be sent to Gemini for transcription.' : 'Mock voice uses a scripted transcript.'}
          voiceError={voiceError}/>
        <Intelligence report={liveAnalysis || report} live={Boolean(liveAnalysis)}
          sentiment={messages.filter(item => item.turnId && item.analysis?.sentiment).map(item => item.analysis)}
          analyzing={messages.some(item => item.turnId && !item.analysis) && status === 'Connected'} lead={lead}
          needsConfirmation={needsConfirmation} confirmed={confirmed} latency={latency} voiceInfo={voiceInfo}
          provider={provider} trace={trace} allowFallback={allowFallback} busy={busy}
          simulate={() => send(scenarios.Ask[1], true)} openRecords={openRecords} reconnect={reconnect} status={status}/>
      </div>
    </main>
    <div className="toast-region" aria-live="polite">{toast && <div className="cockpit-toast" key={toast}>{toast}</div>}</div>
    <dialog className="cockpit-drawer" ref={dialog} onClose={() => setDrawer(null)} aria-labelledby="drawer-title">
      {drawer && <>
        <header className="drawer-header">
          <h2 id="drawer-title">{drawer.citation ? 'Reviewed source' : 'Workspace records'}</h2>
          <button type="button" className="cockpit-button" onClick={() => dialog.current.close()} aria-label="Close panel"><Icon name="close"/></button>
        </header>
        {drawer.citation ? <section className="drawer-source">
          <h3>{drawer.citation.title}</h3><p>{drawer.citation.source}#{drawer.citation.id}</p>
          <blockquote>{drawer.text}</blockquote>
        </section> : (['crm', 'bookings'].includes(drawer.view) ? crmError : insightsError)
          ? <p className="drawer-source" role="alert">{['crm', 'bookings'].includes(drawer.view) ? crmError : insightsError}</p>
          : <Suspense fallback={<p className="drawer-source">Loading panel…</p>}>
              <Records view={drawer.view} crm={crm} insights={insights}/>
            </Suspense>}
      </>}
    </dialog>
  </div>
}
