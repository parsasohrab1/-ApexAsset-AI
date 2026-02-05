import {
  createContext,
  useContext,
  useState,
  useCallback,
  type ReactNode,
} from 'react'

interface ErrorState {
  message: string
  retry: (() => void | Promise<void>) | null
}

interface ErrorContextType {
  error: ErrorState | null
  reportError: (message: string, retry?: () => void | Promise<void>) => void
  clearError: () => void
}

const ErrorContext = createContext<ErrorContextType | undefined>(undefined)

export function ErrorProvider({ children }: { children: ReactNode }) {
  const [error, setError] = useState<ErrorState | null>(null)

  const reportError = useCallback(
    (message: string, retry?: () => void | Promise<void>) => {
      setError({ message, retry: retry ?? null })
    },
    []
  )

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  const handleRetry = useCallback(async () => {
    if (!error?.retry) return
    clearError()
    try {
      await error.retry()
    } catch {
      // Hook will report the new error
    }
  }, [error?.retry, clearError])

  const value: ErrorContextType = {
    error,
    reportError,
    clearError,
  }

  return (
    <ErrorContext.Provider value={value}>
      {children}
      {error && (
        <ErrorBanner
          message={error.message}
          onRetry={error.retry ? handleRetry : undefined}
          onDismiss={clearError}
        />
      )}
    </ErrorContext.Provider>
  )
}

interface ErrorBannerProps {
  message: string
  onRetry?: () => void | Promise<void>
  onDismiss: () => void
}

function ErrorBanner({ message, onRetry, onDismiss }: ErrorBannerProps) {
  const [retrying, setRetrying] = useState(false)

  const handleRetry = async () => {
    if (!onRetry) return
    setRetrying(true)
    try {
      await onRetry()
    } finally {
      setRetrying(false)
    }
  }

  return (
    <div
      className="error-banner"
      role="alert"
      aria-live="assertive"
    >
      <div className="error-banner-content">
        <span className="error-banner-icon" aria-hidden>⚠</span>
        <p className="error-banner-message">{message}</p>
        <div className="error-banner-actions">
          {onRetry && (
            <button
              type="button"
              className="error-banner-retry"
              onClick={handleRetry}
              disabled={retrying}
            >
              {retrying ? 'Retrying...' : 'Retry'}
            </button>
          )}
          <button
            type="button"
            className="error-banner-dismiss"
            onClick={onDismiss}
            aria-label="Dismiss"
          >
            Dismiss
          </button>
        </div>
      </div>
    </div>
  )
}

export function useError() {
  const ctx = useContext(ErrorContext)
  if (ctx === undefined) {
    throw new Error('useError must be used within ErrorProvider')
  }
  return ctx
}
