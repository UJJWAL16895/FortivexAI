import React, { useEffect, useRef, useState } from 'react'
import { createRoot } from 'react-dom/client'
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
  const [connection, setConnection] = useState(0)
  const socket = useRef(null)
  const transcript = useRef(null)
  const input = useRef(null)

  useEffect(() => {
    const url = new URL('/ws/text', window.location.href)
    url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:'
    const client = new WebSocket(url)
    socket.current = client
    client.onmessage = ({ data }) => {
      const event = JSON.parse(data)
      if (event.type === 'ready') {
        setStatus('Connected')
        return
      }
      setMessages(items => [...items, { role: event.type === 'error' ? 'notice' : 'agent', text: event.text }])
      if (event.type === 'reply') setLatency(event.latency_ms)
      setPending(false)
    }
    client.onclose = () => {
      setStatus('Disconnected')
      setPending(false)
    }
    return () => {
      client.onclose = null
      client.onmessage = null
      client.close()
    }
  }, [connection])

  useEffect(() => {
    transcript.current.scrollTop = transcript.current.scrollHeight
  }, [messages, pending])

  function send(text) {
    const message = text.trim()
    if (!message || pending || socket.current?.readyState !== WebSocket.OPEN) return
    socket.current.send(JSON.stringify({ text: message }))
    setMessages(items => [...items, { role: 'buyer', text: message }])
    setDraft('')
    setPending(true)
    input.current.focus()
  }

  return (
    <>
      <header className="header">
        <div className="brand"><span className="brand-mark" aria-hidden="true">▥</span><span>ShelfPilot<small>SALES CONSOLE</small></span></div>
        <span className="mode"><span aria-hidden="true" /> Mock provider</span>
      </header>
      <main>
        <section className="intro">
          <p className="eyebrow">WORKSPACE / TEXT DEMO</p>
          <h1>Sales conversation</h1>
          <p>Try an inbound inventory inquiry as a retail buyer.</p>
        </section>
        <div className="workspace">
          <section className="panel chat" aria-labelledby="transcript-title">
            <div className="panel-header"><h2 id="transcript-title">Transcript</h2><span className={status === 'Connected' ? 'connected' : ''} role="status">{status}</span></div>
            <div className="transcript" role="log" aria-label="Transcript messages" ref={transcript}>
              {messages.map(({ role, text }, index) => (
                <div className={`message ${role}`} key={index}>
                  <span>{role === 'buyer' ? 'You' : role === 'notice' ? 'Session' : 'ShelfPilot'}</span>
                  <p>{text}</p>
                </div>
              ))}
              {pending && <p role="status" className="pending">ShelfPilot is replying…</p>}
            </div>
            <form onSubmit={event => { event.preventDefault(); send(draft) }}>
              <label className="sr-only" htmlFor="message">Message</label>
              <input id="message" ref={input} placeholder="Ask about inventory…" maxLength={500} value={draft} onChange={event => setDraft(event.target.value)} />
              <button className="send" disabled={!draft.trim() || pending || status !== 'Connected'} type="submit">Send <span aria-hidden="true">↑</span></button>
            </form>
          </section>
          <aside className="panel sidebar">
            <section aria-labelledby="session-title">
              <h2 id="session-title">Session</h2>
              <dl>
                <div><dt>Provider</dt><dd>Deterministic mock</dd></div>
                <div><dt>Reply compute</dt><dd>{latency === null ? '—' : `${latency.toFixed(3)} ms`}</dd></div>
              </dl>
              {status === 'Disconnected' && <button className="suggestion" onClick={() => { setStatus('Connecting'); setConnection(value => value + 1) }}>Reconnect</button>}
            </section>
            <section aria-labelledby="prompts-title" className="prompts">
              <h2 id="prompts-title">Try asking</h2>
              {prompts.map(prompt => <button className="suggestion" key={prompt} disabled={pending || status !== 'Connected'} onClick={() => send(prompt)}>{prompt}<span aria-hidden="true">↗</span></button>)}
            </section>
          </aside>
        </div>
      </main>
    </>
  )
}

createRoot(document.getElementById('root')).render(<App />)
