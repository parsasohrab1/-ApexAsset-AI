"""
Readiness probe for Kubernetes / load balancers.
Checks Database (required), InfluxDB (if configured), MQTT (if initialized).
"""

from typing import Tuple

from sqlalchemy import text

from .config import settings


async def check_database(db) -> Tuple[bool, str]:
    """Check PostgreSQL connectivity. Returns (ok, message)."""
    try:
        await db.execute(text("SELECT 1"))
        return True, "connected"
    except Exception as e:
        return False, str(e)


def check_influxdb() -> Tuple[bool, str]:
    """Check InfluxDB if configured (INFLUXDB_TOKEN set). Returns (ok, message)."""
    if not settings.INFLUXDB_TOKEN:
        return True, "skipped (not configured)"

    from .influxdb_client import influxdb_manager

    if not influxdb_manager.client:
        return False, "client not initialized"

    try:
        # InfluxDB 2.x client has ping()
        ok = influxdb_manager.client.ping()
        return bool(ok), "connected" if ok else "ping failed"
    except Exception as e:
        return False, str(e)


def check_mqtt() -> Tuple[bool, str]:
    """Check MQTT broker if client was initialized. Returns (ok, message)."""
    from .realtime.mqtt_client import get_mqtt_client

    client = get_mqtt_client()
    if client is None:
        return True, "skipped (not initialized)"

    return (client.connected, "connected" if client.connected else "disconnected")


async def run_readiness_checks(db) -> Tuple[bool, dict]:
    """
    Run all readiness checks. Returns (ready, details).
    Ready is False if database is down; InfluxDB/MQTT are reported but optional.
    """
    db_ok, db_msg = await check_database(db)
    influx_ok, influx_msg = check_influxdb()
    mqtt_ok, mqtt_msg = check_mqtt()

    details = {
        "database": {"status": "ok" if db_ok else "error", "message": db_msg},
        "influxdb": {"status": "ok" if influx_ok else "degraded", "message": influx_msg},
        "mqtt": {"status": "ok" if mqtt_ok else "degraded", "message": mqtt_msg},
    }

    # Database is required for readiness
    ready = db_ok

    return ready, details
