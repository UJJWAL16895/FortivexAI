import React from 'react'

const shapes = {
  mic: <><rect x="9" y="2" width="6" height="12" rx="3"/><path d="M5 10v1a7 7 0 0 0 14 0v-1M12 18v4m-3 0h6"/></>,
  stop: <rect x="6" y="6" width="12" height="12" rx="2"/>,
  chat: <path d="M20 11a8 8 0 0 1-8 8H4l1.5-4A8 8 0 1 1 20 11ZM8 11h8"/>,
  send: <path d="M3 11 21 3l-6 18-4-8-8-2Zm8 2L21 3"/>,
  screen: <><rect x="3" y="4" width="18" height="13" rx="2"/><path d="M8 21h8m-4-4v4"/></>,
  refresh: <path d="M20 7v5h-5M20 12a8 8 0 1 0-2.3 5.7"/>,
  doc: <path d="M5 3h10l4 4v14H5V3Zm4 9h6m-6 4h6"/>,
  ticket: <path d="M3 7h18v4a2 2 0 0 0 0 4v4H3v-4a2 2 0 0 0 0-4V7Zm12 2v2m0 4v2"/>,
  pulse: <path d="M2 13h5l3-7 4 13 3-6h5"/>,
  close: <path d="m6 6 12 12M18 6 6 18"/>,
  check: <path d="m5 12 4 4L19 6"/>,
}

export function Icon({ name, size = 18 }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="1.65" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{shapes[name]}</svg>
}
