import locationsAudio from './mock-speech/locations.mp3'
import checkAudio from './mock-speech/check.mp3'
import followUpAudio from './mock-speech/follow-up.mp3'
import demoAudio from './mock-speech/demo.mp3'
import storesConfirmationAudio from './mock-speech/stores-confirmation.mp3'

const approvedAudio = new Map([
  ['How many locations do you manage today?', locationsAudio],
  ['I’ll check that with our team.', checkAudio],
  ['Would you like a human follow-up?', followUpAudio],
  ['What would you like to see in a demo?', demoAudio],
  ['I heard 3 stores. Is that correct?', storesConfirmationAudio],
])

export async function toWav(parts, mimeType, context) {
  const audio = await context.decodeAudioData(await new Blob(parts, { type: mimeType }).arrayBuffer())
  const duration = Math.min(audio.duration, 12.5)
  const offline = new OfflineAudioContext(1, Math.max(1, Math.floor(duration * 16000)), 16000)
  const source = offline.createBufferSource()
  source.buffer = audio
  source.connect(offline.destination)
  source.start()
  const samples = (await offline.startRendering()).getChannelData(0)
  let lastSpeech = samples.length
  for (let end = samples.length; end >= 320; end -= 320) {
    let energy = 0
    for (let i = end - 320; i < end; i++) energy += samples[i] ** 2
    if (energy / 320 > 0.000144) {
      lastSpeech = end
      break
    }
  }
  const bytes = new ArrayBuffer(44 + samples.length * 2)
  const view = new DataView(bytes)
  for (const [offset, text] of [[0, 'RIFF'], [8, 'WAVEfmt '], [36, 'data']]) {
    [...text].forEach((letter, i) => view.setUint8(offset + i, letter.charCodeAt(0)))
  }
  for (const [offset, value] of [[4, bytes.byteLength - 8], [16, 16], [24, 16000],
    [28, 32000], [40, samples.length * 2]]) view.setUint32(offset, value, true)
  for (const [offset, value] of [[20, 1], [22, 1], [32, 2], [34, 16]]) view.setUint16(offset, value, true)
  samples.forEach((sample, i) => view.setInt16(44 + i * 2, Math.max(-1, Math.min(1, sample)) * 32767, true))
  return { bytes, endpointMs: (samples.length - lastSpeech) / 16 }
}

export async function transcribe(bytes, language, voiceSession) {
  const started = performance.now()
  const response = await fetch('/api/voice/transcribe?language=' + language, {
    method: 'POST',
    headers: { 'Content-Type': 'audio/wav', ...(voiceSession && { 'X-Voice-Session': voiceSession }) },
    body: bytes,
  })
  const result = await response.json()
  if (!response.ok) throw Error(typeof result.detail === 'string' ? result.detail : 'Transcription failed.')
  return { ...result, transferMs: Math.max(0, performance.now() - started - result.api_ms) }
}

export function createPlayback(context, onStart, onError, onSpeaking = () => {}, voiceSession) {
  const abort = new AbortController()
  let queue = Promise.resolve()
  let source
  let utterance

  function browserSpeech(text) {
    if (!('speechSynthesis' in window)) throw Error('Browser speech is unavailable.')
    return new Promise((resolve, reject) => {
      utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = /[\u0900-\u097f]/u.test(text) ? 'hi-IN' : 'en-IN'
      utterance.onstart = () => {
        if (abort.signal.aborted) return
        onSpeaking(true)
        onStart('Browser speech')
      }
      utterance.onend = resolve
      utterance.onerror = () => reject(Error('Browser speech is unavailable.'))
      window.speechSynthesis.speak(utterance)
    })
  }

  async function play(text, mode) {
    if (abort.signal.aborted) return
    let response
    let provider
    let firstByte = null
    const clip = approvedAudio.get(text)
    if (clip) {
      const started = performance.now()
      response = await fetch(clip, { signal: abort.signal })
      firstByte = performance.now() - started
      provider = 'Bundled speech'
    } else if (mode !== 'mock') {
      response = await fetch('/api/voice/speak', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...(voiceSession && { 'X-Voice-Session': voiceSession }) },
        body: JSON.stringify({ text }),
        signal: abort.signal,
      })
      provider = response.headers.get('X-TTS-Provider')
      if (response.headers.has('X-TTS-First-Byte-Ms')) {
        firstByte = Number(response.headers.get('X-TTS-First-Byte-Ms'))
      }
    }
    if (abort.signal.aborted) return
    if (!response?.ok || response.status === 204) return browserSpeech(text)
    const buffer = await context.decodeAudioData(await response.arrayBuffer())
    if (abort.signal.aborted) return
    await new Promise(resolve => {
      source = context.createBufferSource()
      source.buffer = buffer
      source.connect(context.destination)
      source.onended = () => { source = null; resolve() }
      source.start()
      onSpeaking(true)
      onStart(provider, firstByte)
    })
  }

  return {
    enqueue(text, mode) {
      queue = queue.then(async () => {
        try {
          await play(text, mode)
        } finally {
          if (!abort.signal.aborted) onSpeaking(false)
        }
      }).catch(() => {
        if (!abort.signal.aborted) onError('Speech playback failed. Read the reply in the transcript.')
      })
    },
    stop() {
      abort.abort()
      source?.stop()
      if (utterance) window.speechSynthesis.cancel()
    },
  }
}
