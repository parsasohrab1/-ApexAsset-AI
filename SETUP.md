# ApexAsset AI - Setup Guide

## ✅ Authentication System Implemented

سیستم احراز هویت کامل با ویژگی‌های زیر پیاده‌سازی شده است:

### Backend Features:
- ✅ JWT Authentication (Access & Refresh Tokens)
- ✅ Password Hashing (bcrypt)
- ✅ Role-Based Access Control (RBAC)
- ✅ User Management (Register/Login/Logout)
- ✅ Token Refresh Mechanism
- ✅ Protected API Endpoints
- ✅ 8 User Roles (Field Operator, Engineer, Manager, etc.)

### Frontend Features:
- ✅ Login Page با Demo Credentials
- ✅ Register Page با Role Selection
- ✅ Auth Context برای Global State
- ✅ Protected Routes
- ✅ Automatic Token Refresh
- ✅ Navbar با User Info و Logout
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

سه کاربر آزمایشی به‌صورت خودکار ساخته شده‌اند:

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
│   │   ├── main.py              # FastAPI app با auth routes
│   │   ├── models.py            # Pydantic models (User, Token, etc.)
│   │   ├── auth.py              # JWT و RBAC utilities
│   │   ├── database.py          # In-memory user database
│   │   └── routes/
│   │       └── auth_routes.py   # Auth endpoints
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── Navbar.tsx       # Navigation با logout
    │   │   └── ProtectedRoute.tsx
    │   ├── contexts/
    │   │   └── AuthContext.tsx  # Global auth state
    │   ├── pages/
    │   │   ├── Login.tsx        # صفحه ورود
    │   │   ├── Register.tsx     # صفحه ثبت‌نام
    │   │   └── Dashboard.tsx    # داشبورد اصلی (protected)
    │   ├── services/
    │   │   ├── auth.ts          # Auth service (login, register, etc.)
    │   │   └── api.ts           # API client با token refresh
    │   ├── App.tsx              # Routing
    │   └── main.tsx             # App entry با providers
    └── package.json
```

## 🔒 Security Features

### Backend:
- Password hashing با bcrypt
- JWT tokens با expiration
- Refresh token برای security
- Role-based middleware
- CORS configuration

### Frontend:
- Token storage در localStorage
- Automatic token refresh
- Protected routes
- Logout clears all tokens

## 📝 API Endpoints

### Authentication:
- `POST /auth/register` - ثبت‌نام کاربر جدید
- `POST /auth/login` - ورود و دریافت tokens
- `POST /auth/refresh` - تمدید access token
- `GET /auth/me` - اطلاعات کاربر جاری
- `POST /auth/logout` - خروج از سیستم

### Protected Endpoints:
- `GET /dashboard` - داده‌های داشبورد (نیاز به احراز هویت)
- `GET /srs` - محتوای SRS (عمومی)

## 🎯 Next Steps

برای تکمیل پروژه، مراحل بعدی:

1. **Database Integration**: جایگزینی in-memory database با PostgreSQL
2. **Email Verification**: احراز هویت ایمیل
3. **Password Reset**: فراموشی رمز عبور
4. **User Profile**: مدیریت پروفایل کاربر
5. **Audit Logs**: ثبت فعالیت‌های کاربران
6. **Rate Limiting**: محدودسازی درخواست‌ها
7. **Testing**: Unit و Integration tests

## 🐛 Troubleshooting

### Backend Issues:
```bash
# اگر خطای import گرفتید:
pip install --upgrade pip
pip install -r requirements.txt

# اگر پورت اشغال است:
uvicorn app.main:app --reload --port 8001
```

### Frontend Issues:
```bash
# اگر خطای dependency گرفتید:
rm -rf node_modules package-lock.json
npm install

# اگر پورت اشغال است:
# در vite.config.ts تغییر دهید
```

## 📚 Documentation

- FastAPI Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

**تمام ویژگی‌های Authentication پیاده‌سازی شدند! ✅**
