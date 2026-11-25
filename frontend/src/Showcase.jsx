import React, { useEffect, useRef, useState } from 'react'
import './showcase.css'

const features = [
  ['Voice', 'Record a browser turn and hear an approved sentence.'],
  ['Memory', 'Keep four recent turns and confirm counts and dates.'],
  ['Languages', 'Use English, Hindi and tested Hinglish phrases.'],
  ['Cited knowledge', 'Quote reviewed product cards and abstain on weak evidence.'],
  ['Booking', 'Reserve a labelled IST time after explicit confirmation.'],
  ['CRM', 'Recognize a returning fictional phone or email.'],
  ['Sentiment', 'Review a label for each completed buyer turn.'],
  ['Lead score', 'Read the BANT evidence behind the score.'],
  ['Summary', 'Review a next action and follow-up draft.'],
  ['Insights', 'See saved call and booking counts after restart.'],
]
const pipeline = ['Microphone', 'Transcription', 'Gemini or reviewed card', 'Claims check', 'Synthesis', 'Playback']
const systems = [
  ['Browser', 'Captures speech and plays approved clips.', 'A blocked microphone leaves text available.', 'Keep a socket attached to its gateway.'],
  ['FastAPI', 'Validates frames, routes calls and serves the console.', 'Disconnect cancels the active reply.', 'Move reconnectable state to Redis.'],
  ['Speech', 'Whisper, Gemini and bundled audio cover demo voice.', 'A failed recognizer can use its backup.', 'Use warm GPU or managed streaming STT.'],
  ['Knowledge', 'Retrieves reviewed passages with citations.', 'Weak evidence gets an abstention.', 'Use tenant-filtered managed indexing.'],
  ['SQLite', 'Stores bookings, CRM and call reports.', 'One unique slot can be claimed.', 'Use a Postgres writer and read replicas.'],
]
const sample = [
  ['Buyer', 'How much does Growth cost?', 'Neutral', 0],
  ['ShelfPilot', 'Growth costs ₹2,499 per month for up to five stores, before GST.', 'Neutral', 0, 'Plans and prices · growth'],
  ['Buyer', 'I own three stores and need inventory help this month. My budget is ₹3,000.', 'Positive', 100],
  ['ShelfPilot', 'I can offer a demo on Friday at 11:00 IST. Say confirm booking to reserve it.', 'Positive', 100],
  ['Buyer', 'Confirm booking.', 'Positive', 100],
  ['ShelfPilot', 'Demo booked. The CRM saved the fictional lead and the confirmed appointment.', 'Positive', 100],
]
const costs = [['1,000', 7.66], ['10,000', 76.60], ['100,000', 766]]
const nav = [['home','Home'],['features','Features'],['flow','How it works'],['live','Live console'],['architecture','Architecture'],['scale','Scale & Cost'],['about','About']]

function Wave() {
  return <div className="wave" aria-hidden="true">{Array.from({length: 33}, (_, i) =>
    <i key={i} style={{'--height': Math.round(12 + 88 * Math.abs(Math.sin(i * .72) * Math.sin((i + 1) / 11))) + '%', '--delay': (i * -55) + 'ms'}} />)}</div>
}

function Sample() {
  const [step,setStep] = useState(0)
  const [playing,setPlaying] = useState(false)
  const [typed,setTyped] = useState('')
  const active = sample[Math.max(0,step-1)]
  useEffect(() => {
    if (!playing) return
    const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches
    const timer = setTimeout(() => {
      if (step >= sample.length) setPlaying(false)
      else setStep(step + 1)
    }, reduced ? 900 : 2700)
    return () => clearTimeout(timer)
  }, [step,playing])
  useEffect(() => {
    if (!step) return
    const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches
    const text = sample[step-1][1]
    if (reduced) { setTyped(text); return }
    let count=0
    const timer=setInterval(()=> {
      count+=3
      setTyped(text.slice(0,count))
      if (count>=text.length) clearInterval(timer)
    },22)
    return () => clearInterval(timer)
  }, [step])
  return <section id="sample" className="show-section">
    <div className="section-head"><span>LOCAL FIXTURE</span><h2>Watch a sample call</h2><p>Scripted demo · runs without network or quota.</p></div>
    <article className="sample-shell">
      <div className="sample-controls">
        <button onClick={()=>{ if (!step || step===sample.length) {setTyped('');setStep(1)} setPlaying(!playing) }}>{playing?'Pause':step&&step<sample.length?'Resume':'Play sample'}</button>
        <button onClick={()=>{setPlaying(false);setStep(0);setTyped('')}}>Reset</button>
      </div>
      <div className="sample-grid">
        <div className="sample-chat" aria-label="Scripted conversation">
          {step ? sample.slice(0,step).map(([role,text],i)=>
            <p className="sample-line" key={i}><strong>{role}</strong> {i===step-1?typed:text}</p>) : <p>Play the example to see a cited reply become a booking.</p>}
          {step>=2 && <small className="citation">{sample[1][4]}</small>}
        </div>
        <aside aria-live="polite">
          <p>Sentiment · {step ? active[2] : 'Waiting'}</p>
          <label>Lead score · {step?active[3]:0}/100 <meter value={step?active[3]:0} min="0" max="100" /></label>
          {step===sample.length && <div className="sample-outcome"><strong>Booking confirmed · CRM saved</strong><p>Summary · Three-store buyer, confirmed mock demo. Next action · Review the follow-up draft.</p></div>}
        </aside>
      </div>
    </article>
  </section>
}

export default function Showcase() {
  const [active,setActive]=useState(0)
  const [component,setComponent]=useState(0)
  const [progress,setProgress]=useState(0)
  const [countsVisible,setCountsVisible]=useState(false)
  const [counter,setCounter]=useState(0)
  const root=useRef(null)
  useEffect(()=>{
    const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches
    const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{
      if (!entry.isIntersecting) return
      entry.target.classList.add('seen')
      if(entry.target.dataset.flow) setActive(Number(entry.target.dataset.flow)-1)
      if(entry.target.id==='scale') setCountsVisible(true)
    }),{threshold:.28})
    root.current.querySelectorAll('.reveal,[data-flow],#scale').forEach(el=>observer.observe(el))
    const scroll=()=>{
      const max=document.documentElement.scrollHeight-innerHeight
      setProgress(max?scrollY/max:0)
      if (!reduced) root.current.style.setProperty('--hero-shift', Math.min(24,scrollY/18)+'px')
    }
    addEventListener('scroll',scroll,{passive:true})
    if(reduced) scroll()
    return ()=>{observer.disconnect();removeEventListener('scroll',scroll)}
  },[])
  useEffect(()=>{
    if(!countsVisible)return
    if(matchMedia('(prefers-reduced-motion: reduce)').matches){setCounter(125);return}
    let frame
    const started=performance.now()
    const tick=now=>{const fraction=Math.min(1,(now-started)/650);setCounter(Math.round(125*fraction));if(fraction<1)frame=requestAnimationFrame(tick)}
    frame=requestAnimationFrame(tick)
    return ()=>cancelAnimationFrame(frame)
  },[countsVisible])
  const system=systems[component]
  return <div className="showcase" ref={root}>
    <a className="skip" href="#features">Skip to content</a>
    <header className="show-nav"><a className="show-brand" href="#home">ShelfPilot<span>.</span></a>
      <nav aria-label="Showcase">{nav.map(([id,label])=><a href={'#'+id} key={id}>{label}</a>)}</nav>
      <div className="scroll-progress" style={{transform:'scaleX('+Math.min(1,progress)+')'}} />
    </header>
    <main className="show-main">
      <section className="show-hero" id="home">
        <div><p className="show-kicker">FORTIVEX ROUND 3</p><h1>Make the first <em>sales call</em> count.</h1><p>Ask in your language, hear a sourced answer and confirm a demo in the same conversation.</p><div className="show-actions"><a className="primary" href="#sample">Watch a sample call</a><a href="#live">Open live console</a></div></div>
        <figure className="wave-card"><figcaption>VOICE SIGNAL · ILLUSTRATION</figcaption><Wave/><p>Listen. Check the source. Confirm.</p></figure>
      </section>
      <section className="show-section reveal"><div className="section-head"><span>[ASSUMED] PILOT SCENARIO</span><h2>Give reps time for the conversations that need them.</h2><p>At 1,000 inbound calls per month, six minutes of human handling per call is 100 hours. Two minutes of review per call would be about 33 hours. Pilot outcomes remain unmeasured.</p></div></section>
      <section className="show-section reveal" id="features"><div className="section-head"><span>THE PRODUCT</span><h2>One journey, from hello to follow-up.</h2></div><div className="feature-grid">{features.map(([name,detail],i)=><article key={name} style={{'--stagger':i*36+'ms'}}><h3>{name}</h3><p>{detail}</p></article>)}</div></section>
      <section className="show-section" id="flow"><div className="section-head"><span>THE PIPELINE</span><h2>Follow a turn.</h2></div><ol className="pipeline">{pipeline.map((name,i)=><li key={name} data-flow={i+1} className={active===i?'active':''}>{name}</li>)}</ol></section>
      <Sample/>
      <section className="show-section reveal" id="live"><div className="section-head"><span>WORKING PRODUCT</span><h2>Live console</h2><p>Use text or microphone, inspect the provider trace, then review your booking and call report.</p></div><a className="primary" href="/console">Launch the Sales Console</a></section>
      <section className="show-section reveal" id="architecture"><div className="section-head"><span>SYSTEM DESIGN</span><h2>Explore the architecture.</h2></div><div className="system-buttons" aria-label="Architecture components">{systems.map(([name],i)=><button aria-pressed={component===i} key={name} onClick={()=>setComponent(i)}>{name}</button>)}</div><article className="system-card"><h3>{system[0]}</h3><dl><div><dt>Responsibility</dt><dd>{system[1]}</dd></div><div><dt>Failure mode</dt><dd>{system[2]}</dd></div><div><dt>[ASSUMED] Scaling</dt><dd>{system[3]}</dd></div></dl></article></section>
      <section className="show-section" id="scale"><div className="section-head"><span>[ASSUMED] CAPACITY AND COST SCENARIO</span><h2>Separate registrations from active calls.</h2><p><strong className="counter" aria-label="125 estimated peak sockets">{counter || 125}</strong> peak sockets in the 100,000-registration planning scenario.</p></div><div className="chart" aria-label="Assumed daily paid costs by registrations">{costs.map(([label,cost])=><div key={label}><span>{label}</span><i style={{'--bar':cost/766}}/><b>${cost.toFixed(2)}/day</b></div>)}</div><p>Measured local mock p95 was 66.4 ms at 125 concurrent clients on 26 November 2026. Fleet voice capacity remains unmeasured.</p></section>
      <section className="show-section reveal" id="about"><div className="section-head"><span>LIMITATIONS</span><h2>A prototype with clear boundaries.</h2><p>Use fictional contacts. The published evaluation uses a small authored corpus, synthetic voice and rule-based scoring. Broader speech validation, streaming STT and verified customer identity are production work.</p></div></section>
    </main>
    <footer className="show-footer"><strong>ShelfPilot</strong><a href="https://github.com/UJJWAL16895/FortivexAI">Repository and project contact</a></footer>
  </div>
}
