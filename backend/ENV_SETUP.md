# Environment Variables for Production

All sensitive configuration is read from environment variables via `app/config.py`.

## Health & Readiness Probes

| Endpoint | Purpose | Kubernetes |
|----------|---------|------------|
| `GET /health` | Liveness: app + DB | `livenessProbe` |
| `GET /ready` | Readiness: DB, InfluxDB, MQTT | `readinessProbe` |

`/ready` returns 200 if the database is reachable, 503 otherwise. InfluxDB and MQTT status are reported but optional.

```yaml
# Example Kubernetes probes
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10
readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
``` This document lists every variable used by the backend and which are required for production.

## Required for Production

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | JWT access token signing key (min 32 chars) | `openssl rand -hex 32` |
| `REFRESH_SECRET_KEY` | JWT refresh token signing key (min 32 chars) | `openssl rand -hex 32` |
| `DATABASE_URL` | PostgreSQL sync connection URL | `postgresql://user:pass@host:5432/dbname` |
| `DATABASE_ASYNC_URL` | PostgreSQL async connection URL | `postgresql+asyncpg://user:pass@host:5432/dbname` |
| `ENVIRONMENT` | Must be `production` for production | `production` |

## Optional (with defaults)

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_READ_ASYNC_URL` | `""` | Read replica for reports; empty = use primary |
| `INFLUXDB_URL` | `http://localhost:8086` | InfluxDB server URL |
| `INFLUXDB_TOKEN` | `""` | InfluxDB API token; empty = time-series disabled |
| `INFLUXDB_ORG` | `apexasset` | InfluxDB organization |
| `INFLUXDB_BUCKET` | `sensor_data` | InfluxDB bucket name |
| `CORS_ORIGINS` | `http://localhost:5173,...` | Comma-separated allowed origins |
| `DASHBOARD_CACHE_TTL_SECONDS` | `10` | Dashboard cache TTL |
| `REDIS_URL` | `""` | Redis URL; empty = in-memory cache |
| `MQTT_BROKER_HOST` | `localhost` | MQTT broker host |
| `MQTT_BROKER_PORT` | `1883` | MQTT broker port |
| `API_BASE_URL` | `http://localhost:8000` | Public API base URL (for health/websocket) |
| `RATE_LIMIT_LOGIN` | `5/minute` | Login rate limit per IP |
| `RATE_LIMIT_REGISTER` | `3/minute` | Register rate limit per IP |
| `RATE_LIMIT_REFRESH` | `10/minute` | Token refresh rate limit per IP |
| `RATE_LIMIT_DEFAULT` | `""` | Optional global limit (e.g. `60/minute`) |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token expiry |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token expiry |

## Frontend (Vite)

The frontend reads `VITE_API_URL` (e.g. in `.env` or build-time):

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API base URL | `https://api.example.com` |

Build with:

```bash
VITE_API_URL=https://api.example.com npm run build
```

## Production Checklist

1. Set `ENVIRONMENT=production`
2. Generate and set `SECRET_KEY` and `REFRESH_SECRET_KEY` (min 32 chars)
3. Set `DATABASE_URL` and `DATABASE_ASYNC_URL` to your production PostgreSQL
4. Set `CORS_ORIGINS` to your frontend domain(s)
5. Set `API_BASE_URL` to your public API URL (e.g. `https://api.example.com`)
6. Set `INFLUXDB_TOKEN` if using time-series data
7. Set `REDIS_URL` if using Redis for cache
8. Set `MQTT_BROKER_HOST`/`MQTT_BROKER_PORT` if using MQTT

## Example .env for Production

```env
ENVIRONMENT=production
SECRET_KEY=<64-char-hex-from-openssl-rand-hex-32>
REFRESH_SECRET_KEY=<64-char-hex-from-openssl-rand-hex-32>

DATABASE_URL=postgresql://dbuser:securepass@dbhost:5432/apexasset_db
DATABASE_ASYNC_URL=postgresql+asyncpg://dbuser:securepass@dbhost:5432/apexasset_db
DATABASE_READ_ASYNC_URL=

INFLUXDB_URL=https://influx.example.com
INFLUXDB_TOKEN=<influx-token>
INFLUXDB_ORG=apexasset
INFLUXDB_BUCKET=sensor_data

CORS_ORIGINS=https://app.example.com
API_BASE_URL=https://api.example.com

REDIS_URL=redis://redis.example.com:6379/0
MQTT_BROKER_HOST=mqtt.example.com
MQTT_BROKER_PORT=1883
```
