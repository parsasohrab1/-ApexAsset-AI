const API_BASE =
  (import.meta.env.VITE_API_URL as string | undefined) ??
  'http://localhost:8000'

function getWebSocketUrl(): string {
  const base = API_BASE.replace(/^http/, 'ws')
  return `${base}/ws`
}

export type WebSocketMessage =
  | { type: 'connection'; status: string }
  | { type: 'subscription'; status: string; topic: string }
  | { type: 'alert'; data: unknown; timestamp: string }
  | { type: 'production'; data: unknown; timestamp: string }
  | { type: 'sensor_data'; data: unknown; timestamp: string }
  | { type: 'pong'; timestamp: string }

export interface UseWebSocketOptions {
  onAlert?: () => void
  onProduction?: () => void
  onSensorData?: () => void
}

/**
 * Connects to WebSocket and subscribes to topics. Calls callbacks when relevant messages arrive.
 * Returns cleanup function to disconnect.
 */
export function connectWebSocket(
  topics: string[],
  onMessage: (msg: WebSocketMessage) => void
): () => void {
  const url = getWebSocketUrl()
  const ws = new WebSocket(url)

  ws.onopen = () => {
    topics.forEach((topic) => {
      ws.send(JSON.stringify({ action: 'subscribe', topic }))
    })
  }

  ws.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data) as WebSocketMessage
      onMessage(msg)
    } catch {
      // ignore parse errors
    }
  }

  ws.onerror = () => {
    // Silently reconnect on next mount; optional: log or notify
  }

  return () => {
    topics.forEach((topic) => {
      try {
        ws.send(JSON.stringify({ action: 'unsubscribe', topic }))
      } catch {
        /* ignore */
      }
    })
    ws.close()
  }
}
