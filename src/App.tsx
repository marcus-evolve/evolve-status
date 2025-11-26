import { useEffect, useState } from 'react'
import { StatusData, HistoryData } from './types'
import StatusBanner from './components/StatusBanner'
import ComponentRow from './components/ComponentRow'
import IncidentHistory from './components/IncidentHistory'
import ThemeToggle from './components/ThemeToggle'
import Header from './components/Header'
import Footer from './components/Footer'

function App() {
  const [status, setStatus] = useState<StatusData | null>(null)
  const [history, setHistory] = useState<HistoryData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [theme, setTheme] = useState<'dark' | 'light'>(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('theme')
      if (saved === 'light' || saved === 'dark') return saved
    }
    return 'dark'
  })

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  }, [theme])

  useEffect(() => {
    const fetchData = async () => {
      try {
        const cacheBuster = `?t=${Date.now()}`
        const [statusRes, historyRes] = await Promise.all([
          fetch(`./status.json${cacheBuster}`, { cache: 'no-store' }),
          fetch(`./history.json${cacheBuster}`, { cache: 'no-store' }).catch(() => null),
        ])

        if (!statusRes.ok) {
          throw new Error('Failed to fetch status')
        }

        const statusData = await statusRes.json()
        setStatus(statusData)

        if (historyRes?.ok) {
          const historyData = await historyRes.json()
          setHistory(historyData)
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 60000)
    return () => clearInterval(interval)
  }, [])

  if (error) {
    return (
      <div className="app">
        <Header />
        <main className="main">
          <div className="card error-card">
            <p>Unable to load status: {error}</p>
          </div>
        </main>
        <Footer />
      </div>
    )
  }

  if (!status) {
    return (
      <div className="app">
        <Header />
        <main className="main">
          <div className="card loading-card">
            <div className="loading-spinner" />
            <p>Loading status...</p>
          </div>
        </main>
        <Footer />
      </div>
    )
  }

  return (
    <div className="app">
      <Header>
        <ThemeToggle theme={theme} onToggle={() => setTheme(t => t === 'dark' ? 'light' : 'dark')} />
      </Header>
      
      <main className="main">
        <StatusBanner overall={status.overall} message={status.message} />
        
        <div className="card components-card">
          {status.checks.map((check) => (
            <ComponentRow
              key={check.name}
              check={check}
              history={history}
            />
          ))}
        </div>

        <IncidentHistory incidents={status.incidents} />
      </main>

      <Footer generatedAt={status.generated_at} />
    </div>
  )
}

export default App
