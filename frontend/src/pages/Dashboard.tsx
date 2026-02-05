import { useEffect, useMemo, useRef, useState } from 'react'
import { useVirtualizer } from '@tanstack/react-virtual'
import { apiFetch } from '../services/api'
import { useDashboard } from '../hooks'
import '../App.css'

const SRS_LINE_HEIGHT = 24

export function Dashboard() {
  const {
    data: dashboardData,
    status: dashboardStatus,
    error: dashboardError,
    lastUpdated,
  } = useDashboard({ enableRealtime: true })

  const [srsContent, setSrsContent] = useState('')
  const [filter, setFilter] = useState('')
  const [srsExpanded, setSrsExpanded] = useState(false)
  const [srsStatus, setSrsStatus] = useState<'idle' | 'loading' | 'error'>('idle')
  const [srsError, setSrsError] = useState('')

  // Lazy load SRS only when user expands the section (reduces initial load time)
  useEffect(() => {
    if (!srsExpanded || srsContent) return
    let isMounted = true
    const loadSrs = async () => {
      setSrsStatus('loading')
      setSrsError('')
      try {
        const response = await apiFetch('/srs', { requiresAuth: false })
        if (!response.ok) {
          throw new Error(`Failed to load SRS (HTTP ${response.status})`)
        }
        const text = await response.text()
        if (isMounted) {
          setSrsContent(text)
          setSrsStatus('idle')
        }
      } catch (err) {
        if (isMounted) {
          setSrsStatus('error')
          setSrsError(err instanceof Error ? err.message : 'Failed to load SRS')
        }
      }
    }
    loadSrs()
    return () => {
      isMounted = false
    }
  }, [srsExpanded])

  const { displayLines, totalLines, matchedLines } = useMemo(() => {
    const lines = srsContent ? srsContent.split('\n') : []
    const normalizedFilter = filter.trim().toLowerCase()

    if (!normalizedFilter) {
      return {
        displayLines: lines,
        totalLines: lines.length,
        matchedLines: lines.length,
      }
    }

    const matched = lines.filter((line) =>
      line.toLowerCase().includes(normalizedFilter)
    )

    return {
      displayLines: matched,
      totalLines: lines.length,
      matchedLines: matched.length,
    }
  }, [filter, srsContent])

  const srsScrollRef = useRef<HTMLDivElement>(null)
  const virtualizer = useVirtualizer({
    count: displayLines.length,
    getScrollElement: () => srsScrollRef.current,
    estimateSize: () => SRS_LINE_HEIGHT,
    overscan: 15,
  })

  return (
    <div className="dashboard-content">
      <header className="app-header">
        <div>
          <p className="app-eyebrow">ApexAsset AI</p>
          <h1 className="app-title">MVP Operations Dashboard</h1>
          <p className="app-subtitle">
            Core visibility for production, maintenance, and SRS reference.
          </p>
        </div>
        <div className="status">
          <span>Last updated: {lastUpdated.toLocaleString()}</span>
          <span className="status-live" aria-hidden> ● Live</span>
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
        <div className="kpi-grid" aria-busy={dashboardStatus === 'loading'} aria-live="polite">
          {dashboardStatus === 'loading' ? (
            Array.from({ length: 4 }).map((_, i) => (
              <div className="card kpi-card" key={`skeleton-kpi-${i}`} aria-hidden>
                <span className="skeleton skeleton-text-sm" />
                <span className="skeleton skeleton-text-lg" />
                <span className="skeleton skeleton-text-sm" />
              </div>
            ))
          ) : (
            dashboardData.kpis.map((kpi) => (
              <div className="card kpi-card" key={kpi.label}>
                <p className="kpi-label">{kpi.label}</p>
                <p className="kpi-value">{kpi.value}</p>
                <p className={`kpi-change ${kpi.tone}`}>{kpi.change}</p>
              </div>
            ))
          )}
        </div>

        <div className="section-split">
          <div className="card section-card">
            <div className="section-header">
              <h3 className="section-title">Module readiness</h3>
              <span className="section-meta">
                {dashboardStatus === 'loading' ? 'Loading...' : 'Lifecycle coverage'}
              </span>
            </div>
            <div
              className="module-grid"
              aria-busy={dashboardStatus === 'loading'}
              aria-live="polite"
            >
              {dashboardStatus === 'loading' ? (
                Array.from({ length: 3 }).map((_, i) => (
                  <div
                    className="module-card skeleton-module-card"
                    key={`skeleton-module-${i}`}
                    aria-hidden
                  >
                    <div>
                      <span className="skeleton skeleton-text" style={{ maxWidth: '70%' }} />
                      <span className="skeleton skeleton-text-sm" style={{ display: 'block', marginTop: '0.35rem', maxWidth: '90%' }} />
                    </div>
                    <span className="skeleton" style={{ width: 56, height: 24, borderRadius: 999 }} />
                  </div>
                ))
              ) : (
                dashboardData.modules.map((module) => (
                  <div className="module-card" key={module.title}>
                    <div>
                      <p className="module-name">{module.title}</p>
                      <p className="module-detail">{module.summary}</p>
                    </div>
                    <span className={`badge badge-${module.status.toLowerCase()}`}>
                      {module.status}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="card section-card">
            <div className="section-header">
              <h3 className="section-title">Critical alerts</h3>
              <span className="section-meta">
                {dashboardStatus === 'loading' ? 'Loading...' : 'Requires attention'}
              </span>
            </div>
            <div
              className="alert-list"
              aria-busy={dashboardStatus === 'loading'}
              aria-live="polite"
            >
              {dashboardStatus === 'loading' ? (
                Array.from({ length: 4 }).map((_, i) => (
                  <div
                    className="skeleton-alert-item"
                    key={`skeleton-alert-${i}`}
                    aria-hidden
                  >
                    <span className="skeleton skeleton-text" />
                    <span className="skeleton skeleton-text" />
                  </div>
                ))
              ) : (
                dashboardData.alerts.map((alert) => (
                  <div className="alert-item" key={alert.title}>
                    <div>
                      <p className="alert-title">{alert.title}</p>
                      <p className="alert-meta">
                        {alert.severity} • {alert.time}
                      </p>
                    </div>
                    <p className="alert-action">{alert.action}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </section>

      <section className="modules-section">
        <div className="section-header">
          <h2 className="section-title">Key modules</h2>
          <span className="section-meta">
            {dashboardStatus === 'loading' ? 'Loading...' : 'Exploration → Decommissioning'}
          </span>
        </div>
        <div
          className="modules-grid"
          aria-busy={dashboardStatus === 'loading'}
          aria-live="polite"
        >
          {dashboardStatus === 'loading' ? (
            Array.from({ length: 3 }).map((_, i) => (
              <div className="card module-card-extended" key={`skeleton-module-ext-${i}`} aria-hidden>
                <div className="module-card-header">
                  <div>
                    <span className="skeleton skeleton-text" style={{ display: 'block', maxWidth: '60%' }} />
                    <span className="skeleton skeleton-text-sm" style={{ display: 'block', marginTop: '0.35rem', maxWidth: '85%' }} />
                  </div>
                  <span className="skeleton" style={{ width: 56, height: 24, borderRadius: 999 }} />
                </div>
                <ul className="module-bullets">
                  {[1, 2, 3].map((j) => (
                    <li key={j}>
                      <span className="skeleton skeleton-text-sm" style={{ display: 'inline-block', width: '90%' }} />
                    </li>
                  ))}
                </ul>
                <span className="skeleton" style={{ width: 100, height: 36, borderRadius: 8, display: 'block' }} />
              </div>
            ))
          ) : (
            dashboardData.modules.map((module) => (
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
          ))
          )}
        </div>
      </section>

      <section className="srs-section">
        <div className="section-header">
          <h2 className="section-title">SRS viewer</h2>
          <span className="section-meta">
            {!srsExpanded && 'Click to load'}
            {srsExpanded && srsStatus === 'loading' && 'Loading...'}
            {srsExpanded && srsStatus === 'error' && srsError}
            {srsExpanded && srsStatus === 'idle' &&
              `${matchedLines.toLocaleString()} of ${totalLines.toLocaleString()} lines`}
          </span>
        </div>

        {!srsExpanded ? (
          <button
            type="button"
            className="ghost-button srs-load-trigger"
            onClick={() => setSrsExpanded(true)}
          >
            Load SRS reference
          </button>
        ) : (
          <>
            <div className="toolbar" role="search" aria-label="SRS document filter">
              <label className="search" htmlFor="srs-filter-input">
                <span>Filter</span>
                <input
                  id="srs-filter-input"
                  type="search"
                  placeholder="Type to filter lines..."
                  value={filter}
                  onChange={(event) => setFilter(event.target.value)}
                  aria-label="Filter SRS document lines by text"
                />
              </label>
              <button
                type="button"
                onClick={() => setFilter('')}
                disabled={!filter}
                aria-label="Clear SRS filter"
              >
                Clear
              </button>
              <button
                type="button"
                className="ghost-button"
                onClick={() => setSrsExpanded(false)}
                aria-label="Collapse SRS"
              >
                Collapse
              </button>
            </div>

            <main className="srs-panel">
              <div
                ref={srsScrollRef}
                className="srs-scroll"
                aria-label="SRS document"
              >
                {displayLines.length === 0 ? (
                  <p className="srs-empty">No content available.</p>
                ) : (
                  <div
                    className="srs-virtual-inner"
                    style={{
                      height: `${virtualizer.getTotalSize()}px`,
                      width: '100%',
                      position: 'relative',
                    }}
                  >
                    {virtualizer.getVirtualItems().map((virtualRow) => (
                      <div
                        key={virtualRow.key}
                        className="srs-line"
                        data-index={virtualRow.index}
                        style={{
                          position: 'absolute',
                          top: 0,
                          left: 0,
                          width: '100%',
                          height: `${virtualRow.size}px`,
                          transform: `translateY(${virtualRow.start}px)`,
                        }}
                      >
                        {displayLines[virtualRow.index] ?? ''}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </main>
          </>
        )}
      </section>
    </div>
  )
}
