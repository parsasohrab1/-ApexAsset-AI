"""
MQTT Client for Real-time Data Ingestion
Receives sensor data from MQTT broker and stores in database
"""

import json
import asyncio
from typing import Optional, Callable
from datetime import datetime

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    print("Warning: paho-mqtt not installed. MQTT functionality disabled.")

from ..influxdb_client import influxdb_manager
from ..database import SessionLocal
from ..db_models import Alert, AlertSeverity, AlertStatus
from .websocket import broadcast_sensor_data, broadcast_alert


class MQTTClient:
    """MQTT Client for receiving sensor data"""
    
    def __init__(
        self,
        broker_host: str = "localhost",
        broker_port: int = 1883,
        client_id: str = "apexasset_backend"
    ):
        if not MQTT_AVAILABLE:
            print("MQTT client cannot be initialized: paho-mqtt not installed")
            self.client = None
            return
        
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client_id = client_id
        self.client = mqtt.Client(client_id=client_id)
        
        # Set callbacks
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        
        self.connected = False
        self.subscribed_topics = []
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            print(f"✓ Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
            self.connected = True
            
            # Subscribe to default topics
            self.subscribe("sensors/#")
            self.subscribe("alerts/#")
        else:
            print(f"✗ Failed to connect to MQTT broker. Return code: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker"""
        print(f"Disconnected from MQTT broker. Return code: {rc}")
        self.connected = False
    
    def _on_message(self, client, userdata, msg):
        """Callback when message is received"""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            # Route message based on topic
            if topic.startswith("sensors/"):
                self._handle_sensor_data(topic, payload)
            elif topic.startswith("alerts/"):
                self._handle_alert(topic, payload)
            
        except Exception as e:
            print(f"Error processing MQTT message: {e}")
    
    def _handle_sensor_data(self, topic: str, payload: dict):
        """Handle incoming sensor data"""
        try:
            # Extract information from payload
            asset_id = payload.get('asset_id')
            sensor_id = payload.get('sensor_id')
            value = payload.get('value')
            timestamp = payload.get('timestamp')
            
            if not all([asset_id, sensor_id, value is not None]):
                print(f"Invalid sensor data: {payload}")
                return
            
            # Parse timestamp
            if timestamp:
                timestamp = datetime.fromisoformat(timestamp)
            else:
                timestamp = datetime.utcnow()
            
            # Write to InfluxDB
            measurement = payload.get('measurement', 'sensor_reading')
            influxdb_manager.write_sensor_data(
                measurement=measurement,
                asset_id=asset_id,
                sensor_id=sensor_id,
                value=value,
                timestamp=timestamp,
                additional_tags=payload.get('tags'),
                additional_fields=payload.get('fields')
            )
            
            # Broadcast via WebSocket
            asyncio.create_task(broadcast_sensor_data(payload))
            
        except Exception as e:
            print(f"Error handling sensor data: {e}")
    
    def _handle_alert(self, topic: str, payload: dict):
        """Handle incoming alert"""
        try:
            # Create alert in database
            db = SessionLocal()
            
            # Map severity
            severity_map = {
                'critical': AlertSeverity.CRITICAL,
                'high': AlertSeverity.HIGH,
                'medium': AlertSeverity.MEDIUM,
                'low': AlertSeverity.LOW
            }
            
            alert = Alert(
                title=payload.get('title', 'MQTT Alert'),
                description=payload.get('description'),
                severity=severity_map.get(payload.get('severity', 'medium'), AlertSeverity.MEDIUM),
                status=AlertStatus.OPEN,
                asset_id=payload.get('asset_id'),
                alert_type=payload.get('alert_type'),
                source='mqtt',
                threshold_value=payload.get('threshold_value'),
                actual_value=payload.get('actual_value'),
                occurred_at=datetime.utcnow()
            )
            
            db.add(alert)
            db.commit()
            db.refresh(alert)
            db.close()
            
            # Broadcast via WebSocket
            asyncio.create_task(broadcast_alert({
                'id': alert.id,
                'title': alert.title,
                'severity': alert.severity.value,
                'asset_id': alert.asset_id
            }))
            # Invalidate dashboard cache so next fetch returns fresh KPIs/alerts
            async def _invalidate_dashboard():
                from ..cache import get_cache
                c = get_cache()
                await c.delete("dashboard")
            asyncio.create_task(_invalidate_dashboard())
            
        except Exception as e:
            print(f"Error handling alert: {e}")
    
    def connect(self):
        """Connect to MQTT broker"""
        if not self.client:
            print("MQTT client not available")
            return False
        
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            return True
        except Exception as e:
            print(f"Failed to connect to MQTT broker: {e}")
            return False
    
    def subscribe(self, topic: str):
        """Subscribe to a topic"""
        if not self.client:
            return
        
        self.client.subscribe(topic)
        self.subscribed_topics.append(topic)
        print(f"Subscribed to MQTT topic: {topic}")
    
    def publish(self, topic: str, payload: dict):
        """Publish a message to a topic"""
        if not self.client:
            return
        
        self.client.publish(topic, json.dumps(payload))
    
    def start(self):
        """Start MQTT client loop"""
        if not self.client:
            return
        
        self.client.loop_start()
    
    def stop(self):
        """Stop MQTT client loop"""
        if not self.client:
            return
        
        self.client.loop_stop()
        self.client.disconnect()


# Global MQTT client instance
mqtt_client = None


def initialize_mqtt_client(broker_host: str = "localhost", broker_port: int = 1883):
    """Initialize and start MQTT client"""
    global mqtt_client
    
    if not MQTT_AVAILABLE:
        print("MQTT functionality disabled - paho-mqtt not installed")
        print("Install with: pip install paho-mqtt")
        return None
    
    mqtt_client = MQTTClient(broker_host=broker_host, broker_port=broker_port)
    
    if mqtt_client.connect():
        mqtt_client.start()
        print("✓ MQTT client started successfully")
    else:
        print("✗ Failed to start MQTT client")
        mqtt_client = None
    
    return mqtt_client


def get_mqtt_client() -> Optional[MQTTClient]:
    """Get the global MQTT client instance"""
    return mqtt_client
