# ApexAsset AI - Setup Guide

## ✅ Authentication System Implemented

A complete authentication system has been implemented with the following features:

### Backend Features:
- ✅ JWT Authentication (Access & Refresh Tokens)
- ✅ Password Hashing (bcrypt)
- ✅ Role-Based Access Control (RBAC)
- ✅ User Management (Register/Login/Logout)
- ✅ Token Refresh Mechanism
- ✅ Protected API Endpoints
- ✅ 8 User Roles (Field Operator, Engineer, Manager, etc.)

### Frontend Features:
- ✅ Login Page with Demo Credentials
- ✅ Register Page with Role Selection
- ✅ Auth Context for Global State
- ✅ Protected Routes
- ✅ Automatic Token Refresh
- ✅ Navbar with User Info and Logout
- ✅ Responsive Design

## 🚀 Quick Start

### 1. Backend Setup

```bash
cd backend

# Copy environment template and configure
cp .env.example .env
# Edit .env: set SECRET_KEY and REFRESH_SECRET_KEY (openssl rand -hex 32)

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload
```

Backend will run on: `http://localhost:8000`

**Environment variables:** All configuration (database, JWT, InfluxDB, MQTT, etc.) is read from `.env` via `config.py`. See `backend/ENV_SETUP.md` for the full list and production requirements.

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run the dev server
npm run dev
```

Frontend will run on: `http://localhost:5173`

## 🔐 Demo Users

Three demo users are created automatically:

| Email | Password | Role |
|-------|----------|------|
| admin@apexasset.ai | admin123 | Admin |
| engineer@apexasset.ai | engineer123 | Production Engineer |
| operator@apexasset.ai | operator123 | Field Operator |

## 📁 Project Structure

```
ApexAssetAi/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app with auth routes
│   │   ├── models.py            # Pydantic models (User, Token, etc.)
│   │   ├── auth.py              # JWT and RBAC utilities
│   │   ├── database.py          # In-memory user database
│   │   └── routes/
│   │       └── auth_routes.py   # Auth endpoints
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── Navbar.tsx       # Navigation with logout
    │   │   └── ProtectedRoute.tsx
    │   ├── contexts/
    │   │   └── AuthContext.tsx  # Global auth state
    │   ├── pages/
    │   │   ├── Login.tsx        # Login page
    │   │   ├── Register.tsx     # Registration page
    │   │   └── Dashboard.tsx    # Main dashboard (protected)
    │   ├── services/
    │   │   ├── auth.ts          # Auth service (login, register, etc.)
    │   │   └── api.ts           # API client with token refresh
    │   ├── App.tsx              # Routing
    │   └── main.tsx             # App entry with providers
    └── package.json
```

## 🔒 Security Features

### Backend:
- Password hashing with bcrypt
- JWT tokens with expiration
- Refresh token for security
- Role-based middleware
- CORS configuration

### Frontend:
- Token storage in localStorage
- Automatic token refresh
- Protected routes
- Logout clears all tokens

## 📝 API Endpoints

### Authentication:
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Log in and receive tokens
- `POST /auth/refresh` - Renew the access token
- `GET /auth/me` - Current user information
- `POST /auth/logout` - Log out of the system

### Protected Endpoints:
- `GET /dashboard` - Dashboard data (requires authentication)
- `GET /srs` - SRS content (public)

## 🎯 Next Steps

To complete the project, the next steps:

1. **Database Integration**: Replace the in-memory database with PostgreSQL
2. **Email Verification**: Email authentication
3. **Password Reset**: Forgot password
4. **User Profile**: User profile management
5. **Audit Logs**: Logging user activities
6. **Rate Limiting**: Limiting requests
7. **Testing**: Unit and Integration tests

## 🐛 Troubleshooting

### Backend Issues:
```bash
# If you get an import error:
pip install --upgrade pip
pip install -r requirements.txt

# If the port is busy:
uvicorn app.main:app --reload --port 8001
```

### Frontend Issues:
```bash
# If you get a dependency error:
rm -rf node_modules package-lock.json
npm install

# If the port is busy:
# Change it in vite.config.ts
```

## 📚 Documentation

- FastAPI Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

**All Authentication features have been implemented! ✅**
