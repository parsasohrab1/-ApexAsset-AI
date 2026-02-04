import { useEffect, useMemo, useState } from 'react'
import './App.css'

const API_BASE =
  (import.meta.env.VITE_API_URL as string | undefined) ??
  'http://localhost:8000'

type KPI = {
  label: string
  value: string
  change: string
  tone: string
}

type ModuleCard = {
  title: string
  summary: string
  bullets: string[]
  status: string
}

type AlertItem = {
  title: string
  severity: string
  time: string
  action: string
}

type DashboardData = {
  kpis: KPI[]
  modules: ModuleCard[]
  alerts: AlertItem[]
}

function App() {
  const [srsContent, setSrsContent] = useState('')
  const [filter, setFilter] = useState('')
  const [status, setStatus] = useState<'idle' | 'loading' | 'error'>('idle')
  const [error, setError] = useState('')
  const [dashboardStatus, setDashboardStatus] = useState<
    'idle' | 'loading' | 'error'
  >('idle')
  const [dashboardError, setDashboardError] = useState('')
  const [dashboardData, setDashboardData] = useState<DashboardData>({
    kpis: [],
    modules: [],
    alerts: [],
  })

  useEffect(() => {
    let isMounted = true
    const loadSrs = async () => {
      setStatus('loading')
      setError('')

      try {
        const response = await fetch('http://localhost:8000/srs')
        if (!response.ok) {
          throw new Error(`Failed to load SRS (HTTP ${response.status})`)
        }
        const text = await response.text()
        if (isMounted) {
          setSrsContent(text)
          setStatus('idle')
        }
      } catch (err) {
        if (isMounted) {
          setStatus('error')
          setError(err instanceof Error ? err.message : 'Failed to load SRS')
        }
      }
    }

    loadSrs()
    return () => {
      isMounted = false
    }
  }, [])

  useEffect(() => {
    let isMounted = true
    const loadDashboard = async () => {
      setDashboardStatus('loading')
      setDashboardError('')

      try {
        const response = await fetch(`${API_BASE}/dashboard`)
        if (!response.ok) {
          throw new Error(`Failed to load dashboard (HTTP ${response.status})`)
        }
        const data = (await response.json()) as DashboardData
        if (isMounted) {
          setDashboardData(data)
          setDashboardStatus('idle')
        }
      } catch (err) {
        if (isMounted) {
          setDashboardStatus('error')
          setDashboardError(
            err instanceof Error ? err.message : 'Failed to load dashboard'
          )
        }
      }
    }

    loadDashboard()
    return () => {
      isMounted = false
    }
  }, [])

  const { displayText, totalLines, matchedLines } = useMemo(() => {
    const lines = srsContent ? srsContent.split('\n') : []
    const normalizedFilter = filter.trim().toLowerCase()

    if (!normalizedFilter) {
      return {
        displayText: srsContent,
        totalLines: lines.length,
        matchedLines: lines.length,
      }
    }

    const matched = lines.filter((line) =>
      line.toLowerCase().includes(normalizedFilter)
    )

    return {
      displayText: matched.join('\n'),
      totalLines: lines.length,
      matchedLines: matched.length,
    }
  }, [filter, srsContent])

  const lastUpdated = new Date().toLocaleString()

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <p className="app-eyebrow">ApexAsset AI</p>
          <h1 className="app-title">MVP Operations Dashboard</h1>
          <p className="app-subtitle">
            Core visibility for production, maintenance, and SRS reference.
          </p>
        </div>
        <div className="status">
          <span>Last updated: {lastUpdated}</span>
        </div>
      </header>

      <section className="dashboard">
        <div className="section-header">
          <h2 className="section-title">Key metrics</h2>
          <span className="section-meta">
            {dashboardStatus === 'loading' && 'Loading...'}
            {dashboardStatus === 'error' && dashboardError}
            {dashboardStatus === 'idle' && 'Live snapshot'}
          </span>
        </div>
        <div className="kpi-grid">
          {dashboardData.kpis.map((kpi) => (
            <div className="card kpi-card" key={kpi.label}>
              <p className="kpi-label">{kpi.label}</p>
              <p className="kpi-value">{kpi.value}</p>
              <p className={`kpi-change ${kpi.tone}`}>{kpi.change}</p>
            </div>
          ))}
        </div>

        <div className="section-split">
          <div className="card section-card">
            <div className="section-header">
              <h3 className="section-title">Module readiness</h3>
              <span className="section-meta">Lifecycle coverage</span>
            </div>
            <div className="module-grid">
              {dashboardData.modules.map((module) => (
                <div className="module-card" key={module.title}>
                  <div>
                    <p className="module-name">{module.title}</p>
                    <p className="module-detail">{module.summary}</p>
                  </div>
                  <span className={`badge badge-${module.status.toLowerCase()}`}>
                    {module.status}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="card section-card">
            <div className="section-header">
              <h3 className="section-title">Critical alerts</h3>
              <span className="section-meta">Requires attention</span>
            </div>
            <div className="alert-list">
              {dashboardData.alerts.map((alert) => (
                <div className="alert-item" key={alert.title}>
                  <div>
                    <p className="alert-title">{alert.title}</p>
                    <p className="alert-meta">
                      {alert.severity} • {alert.time}
                    </p>
                  </div>
                  <p className="alert-action">{alert.action}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="modules-section">
        <div className="section-header">
          <h2 className="section-title">Key modules</h2>
          <span className="section-meta">Exploration → Decommissioning</span>
        </div>
        <div className="modules-grid">
          {dashboardData.modules.map((module) => (
            <div className="card module-card-extended" key={module.title}>
              <div className="module-card-header">
                <div>
                  <p className="module-name">{module.title}</p>
                  <p className="module-detail">{module.summary}</p>
                </div>
                <span className={`badge badge-${module.status.toLowerCase()}`}>
                  {module.status}
                </span>
              </div>
              <ul className="module-bullets">
                {module.bullets.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
              <button type="button" className="ghost-button">
                Open module
              </button>
            </div>
          ))}
        </div>
      </section>

      <section className="srs-section">
        <div className="section-header">
          <h2 className="section-title">SRS viewer</h2>
          <span className="section-meta">
            {status === 'loading' && 'Loading...'}
            {status === 'error' && error}
            {status === 'idle' &&
              `${matchedLines.toLocaleString()} of ${totalLines.toLocaleString()} lines`}
          </span>
        </div>

        <div className="toolbar">
          <label className="search">
            <span>Filter</span>
            <input
              type="search"
              placeholder="Type to filter lines..."
              value={filter}
              onChange={(event) => setFilter(event.target.value)}
            />
          </label>
          <button
            type="button"
            onClick={() => setFilter('')}
            disabled={!filter}
          >
            Clear
          </button>
        </div>

        <main className="srs-panel">
          <pre className="srs-content">
            {displayText || 'No content available.'}
          </pre>
        </main>
      </section>
    </div>
  )
}

export default App
