import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import './Navbar.css'

export function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <nav className="navbar">
      <div className="navbar-content">
        <div className="navbar-brand">
          <span className="brand-logo">⚡</span>
          <span className="brand-name">ApexAsset AI</span>
        </div>

        <div className="navbar-user">
          <div className="user-info">
            <span className="user-name">{user?.email}</span>
            <span className="user-role">{user?.role?.replace('_', ' ')}</span>
          </div>
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </div>
      </div>
    </nav>
  )
}
