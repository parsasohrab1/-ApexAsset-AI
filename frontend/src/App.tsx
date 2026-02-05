import { Routes, Route, Navigate } from 'react-router-dom'
import { Login } from './pages/Login'
import { Register } from './pages/Register'
import { Dashboard } from './pages/Dashboard'
import { ProtectedRoute } from './components/ProtectedRoute'
import { Navbar } from './components/Navbar'
import { useAuth } from './contexts/AuthContext'
import { useError } from './contexts/ErrorContext'
import './App.css'

function App() {
  const { isAuthenticated } = useAuth()
  const { error } = useError()

  return (
    <div className={`app ${error ? 'app-with-error-banner' : ''}`}>
      {isAuthenticated && <Navbar />}
      
      <div className={isAuthenticated ? 'app-with-navbar' : ''}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </div>
  )
}

export default App
