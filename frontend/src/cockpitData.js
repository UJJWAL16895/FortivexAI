export const navigation = [
  ['home', 'Home'], ['features', 'Features'], ['flow', 'How it works'], ['live', 'Live console'],
  ['architecture', 'Architecture'], ['scale', 'Scale & Cost'], ['about', 'About'],
]

export const scenarios = {
  Ask: ['How much does Growth cost?', 'How does the multi-store dashboard work?'],
  Book: ['Book a demo', 'Confirm booking'],
  Objection: ['Can I get 40% off?', 'It is too expensive.'],
  Hindi: ['Growth प्लान की कीमत क्या है?', 'मेरी तीन दुकानें हैं।'],
}

export const hero = [
  ['Ask for a sourced price', scenarios.Ask[0]],
  ['Check an unsupported offer', scenarios.Objection[0]],
  ['Introduce the fictional buyer', 'My name is Asha.'],
  ['Give a qualification signal', 'I am the owner. We need inventory tools this month. Our budget is fixed.'],
  ['Save a fictional contact', 'My email is cockpit-hero@example.test'],
  ['Request an appointment', scenarios.Book[0]],
  ['Confirm the offered time', scenarios.Book[1]],
]

export const bant = [
  ['Budget', 'Buyer mentioned a budget.'],
  ['Authority', 'Buyer identified a decision-making role.'],
  ['Need', 'Buyer stated a need.'],
  ['Timeline', 'Buyer mentioned a timeline.'],
]

export function formatClock(ms) {
  const seconds = Math.floor(ms / 1000)
  return [Math.floor(seconds / 60), seconds % 60].map(value => String(value).padStart(2, '0')).join(':')
}

export function bookingTime(mode, text) {
  if (mode !== 'booking') return null
  return /^(?:Demo booked for|Demo moved to|Your demo is booked for) (.+)\.$/.exec(text)?.[1] ?? null
}

export function receivedLanguage(text) {
  if (/[\u0900-\u097f]/u.test(text)) return /[A-Za-z]/.test(text) ? 'Hinglish · mixed script' : 'HI · Devanagari'
  return null
}
