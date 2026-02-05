import { useCallback, useEffect, useState } from 'react'
import { apiFetch } from '../services/api'
import { connectWebSocket, type WebSocketMessage } from '../services/websocket'
import { useError } from '../contexts/ErrorContext'

export type KPI = {
  label: string
  value: string
  change: string
  tone: string
}

export type ModuleCard = {
  title: string
  summary: string
  bullets: string[]
  status: string
}

export type AlertItem = {
  title: string
  severity: string
  time: string
  action: string
}

export type DashboardData = {
  kpis: KPI[]
  modules: ModuleCard[]
  alerts: AlertItem[]
}

export type DashboardStatus = 'idle' | 'loading' | 'error'

export interface UseDashboardOptions {
  /** Connect to WebSocket and auto-refresh on alerts/production. Default: true */
  enableRealtime?: boolean
}

export interface UseDashboardResult {
  data: DashboardData
  status: DashboardStatus
  error: string
  lastUpdated: Date
  refresh: () => Promise<void>
}

export function useDashboard(options: UseDashboardOptions = {}): UseDashboardResult {
  const { enableRealtime = true } = options
  const { reportError } = useError()

  const [status, setStatus] = useState<DashboardStatus>('idle')
  const [error, setError] = useState('')
  const [data, setData] = useState<DashboardData>({
    kpis: [],
    modules: [],
    alerts: [],
  })
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())

  const refresh = useCallback(async () => {
    setStatus('loading')
    setError('')
    try {
      const response = await apiFetch('/dashboard')
      if (!response.ok) {
        throw new Error(`Failed to load dashboard (HTTP ${response.status})`)
      }
      const json = (await response.json()) as DashboardData
      setData(json)
      setStatus('idle')
      setLastUpdated(new Date())
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load dashboard'
      setStatus('error')
      setError(message)
      reportError(message, refresh)
    }
  }, [reportError])

  // Initial load
  useEffect(() => {
    refresh()
  }, [refresh])

  // WebSocket: auto-refresh on alerts/production
  useEffect(() => {
    if (!enableRealtime) return

    const disconnect = connectWebSocket(
      ['alerts', 'production'],
      (msg: WebSocketMessage) => {
        if (msg.type === 'alert' || msg.type === 'production') {
          refresh()
        }
      }
    )
    return disconnect
  }, [refresh, enableRealtime])

  return {
    data,
    status,
    error,
    lastUpdated,
    refresh,
  }
}
