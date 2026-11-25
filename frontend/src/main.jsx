import React, { lazy, Suspense } from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'

const Page = location.pathname === '/console'
  ? lazy(() => import('./Console.jsx'))
  : lazy(() => import('./Showcase.jsx'))

createRoot(document.getElementById('root')).render(
  <Suspense fallback={<main>Loading ShelfPilot…</main>}><Page /></Suspense>
)
