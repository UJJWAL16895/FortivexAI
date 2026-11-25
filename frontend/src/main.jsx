import React, { useEffect, useRef, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { createPlayback, toWav, transcribe } from './voice.js'
import './styles.css'

const prompts = ['How do I manage multiple stores?', 'How much does it cost?', 'Can I see a demo?']
const initialMessage = {
  role: 'agent',
  text: 'Hi, I’m the ShelfPilot demo agent. What would you like to know about managing inventory across your stores?',
}

function App() {
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
  const [voiceInfo, setVoiceInfo] = useState(null)
  const [voiceError, setVoiceError] = useState('')
  const [connection, setConnection] = useState(0)
  const socket = useRef(null)
  const transcript = useRef(null)
  const input = useRef(null)
  const recording = useRef(null)
  const context = useRef(null)
  const playback = useRef(null)
  const replyMode = useRef('mock')

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
        return
      }
      if (event.type === 'provider') {
        if (event.status !== 'trying') {
          setTrace(items => [...items, `${event.provider} ${event.status}${event.code ? ` (${event.code})` : ''}${event.quota ? ` · ${event.quota}` : ''}`])
        }
        if (event.status === 'active') {
          setProvider(event.model)
          replyMode.current = event.provider === 'mock' ? 'mock' : 'live'
          setMode(replyMode.current)
        }
        return
      }
      if (event.type === 'delta') {
        setPartial(text => text + event.text)
        return
      }
      if (event.type === 'sentence') {
        playback.current?.enqueue(event.text, replyMode.current)
        return
      }
      if (event.type !== 'reply' && event.type !== 'error') return
      setMessages(items => [...items, {
        role: event.type === 'error' ? 'notice' : 'agent',
        text: event.text,
        mode: event.mode,
      }])
      setPartial('')
      if (event.type === 'reply') setLatency(event.latency_ms)
      setPending(false)
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
      const recorder = new MediaRecorder(stream)
      const parts = []
      recording.current = recorder
      recorder.ondataavailable = event => { if (event.data.size) parts.push(event.data) }
      recorder.onstop = async () => {
        const stoppedAt = performance.now()
        clearTimeout(timer)
        stream.getTracks().forEach(track => track.stop())
        recording.current = null
        setMic('transcribing')
        try {
          const bytes = await toWav(parts, recorder.mimeType, context.current)
          const transcript = await transcribe(bytes)
          setVoiceInfo({ stt: transcript.provider, sttMs: transcript.latency_ms })
          const voicePlayback = createPlayback(context.current, source => setVoiceInfo(info => ({
            ...info, tts: source, audioMs: info.audioMs ?? Math.round(performance.now() - stoppedAt),
          })), setVoiceError)
          if (!send(transcript.text, false, voicePlayback)) setVoiceError('Reconnect and record again.')
        } catch (error) {
          setVoiceError(error.message || 'Recording failed. Try typing your message.')
        } finally {
          setMic('idle')
        }
      }
      recorder.start()
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
              {messages.map(({ role, text, mode: replyMode }, index) => (
                <div className={`message ${role}`} key={index}>
                  <span>{role === 'buyer' ? 'You' : role === 'notice' ? 'Session' : 'ShelfPilot'}{replyMode && ` · ${replyMode.toUpperCase()}`}</span>
                  <p>{text}</p>
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
            <p className="voice-note">{configuredMode === 'live' ? 'Mic audio is sent to Gemini for transcription.' : 'Mock voice uses a scripted transcript.'}</p>
            {voiceError && <p role="alert" className="voice-error">{voiceError}</p>}
          </section>
          <aside className="panel sidebar">
            <section aria-labelledby="session-title">
              <h2 id="session-title">Session</h2>
              <dl>
                <div><dt>Provider</dt><dd>{provider || '—'}</dd></div>
                <div><dt>First text</dt><dd>{latency === null ? '—' : `${latency.toFixed(2)} ms`}</dd></div>
                {voiceInfo && <div><dt>Transcription</dt><dd>{voiceInfo.stt} · {voiceInfo.sttMs.toFixed(0)} ms</dd></div>}
                {voiceInfo?.tts && <div><dt>Stop to playback</dt><dd>{voiceInfo.audioMs} ms · {voiceInfo.tts}</dd></div>}
              </dl>
              {trace.length > 0 && <ul className="trace" aria-label="Provider trace">{trace.map(item => <li key={item}>{item}</li>)}</ul>}
              {allowFallback && <button className="suggestion" disabled={pending || mic !== 'idle' || status !== 'Connected'} onClick={() => send(prompts[0], true)}>Simulate Gemini failures</button>}
              {status === 'Disconnected' && <button className="suggestion" onClick={() => { setStatus('Connecting'); setConnection(value => value + 1) }}>Reconnect</button>}
            </section>
            <section aria-labelledby="prompts-title" className="prompts">
              <h2 id="prompts-title">Try asking</h2>
              {prompts.map(prompt => <button className="suggestion" key={prompt} disabled={pending || mic !== 'idle' || status !== 'Connected'} onClick={() => send(prompt)}>{prompt}<span aria-hidden="true">↗</span></button>)}
            </section>
          </aside>
        </div>
      </main>
    </>
  )
}

createRoot(document.getElementById('root')).render(<App />)
