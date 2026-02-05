"""
WebSocket Server for Real-time Data Streaming
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Set
import json
import asyncio
from datetime import datetime


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscriptions: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        self.active_connections.remove(websocket)
        # Remove from all subscriptions
        for topic in self.subscriptions:
            self.subscriptions[topic].discard(websocket)
    
    def subscribe(self, websocket: WebSocket, topic: str):
        """Subscribe a connection to a topic"""
        if topic not in self.subscriptions:
            self.subscriptions[topic] = set()
        self.subscriptions[topic].add(websocket)
    
    def unsubscribe(self, websocket: WebSocket, topic: str):
        """Unsubscribe a connection from a topic"""
        if topic in self.subscriptions:
            self.subscriptions[topic].discard(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific connection"""
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        """Broadcast message to all connections"""
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass
    
    async def broadcast_to_topic(self, topic: str, message: str):
        """Broadcast message to all subscribers of a topic"""
        if topic in self.subscriptions:
            dead_connections = []
            for connection in self.subscriptions[topic]:
                try:
                    await connection.send_text(message)
                except:
                    dead_connections.append(connection)
            
            # Clean up dead connections
            for connection in dead_connections:
                self.unsubscribe(connection, topic)


# Global connection manager
manager = ConnectionManager()


async def handle_websocket_client(websocket: WebSocket):
    """
    Handle WebSocket client connection
    
    Expected message format:
    {
        "action": "subscribe" | "unsubscribe" | "data",
        "topic": "alerts" | "sensors" | "production",
        "data": {...}
    }
    """
    await manager.connect(websocket)
    
    try:
        # Send welcome message
        await manager.send_personal_message(
            json.dumps({
                "type": "connection",
                "status": "connected",
                "timestamp": datetime.utcnow().isoformat()
            }),
            websocket
        )
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            action = message.get("action")
            topic = message.get("topic")
            
            if action == "subscribe" and topic:
                manager.subscribe(websocket, topic)
                await manager.send_personal_message(
                    json.dumps({
                        "type": "subscription",
                        "status": "subscribed",
                        "topic": topic,
                        "timestamp": datetime.utcnow().isoformat()
                    }),
                    websocket
                )
            
            elif action == "unsubscribe" and topic:
                manager.unsubscribe(websocket, topic)
                await manager.send_personal_message(
                    json.dumps({
                        "type": "subscription",
                        "status": "unsubscribed",
                        "topic": topic,
                        "timestamp": datetime.utcnow().isoformat()
                    }),
                    websocket
                )
            
            elif action == "ping":
                await manager.send_personal_message(
                    json.dumps({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }),
                    websocket
                )
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def broadcast_sensor_data(sensor_data: dict):
    """Broadcast sensor data to all subscribers"""
    message = json.dumps({
        "type": "sensor_data",
        "data": sensor_data,
        "timestamp": datetime.utcnow().isoformat()
    })
    await manager.broadcast_to_topic("sensors", message)


async def broadcast_alert(alert_data: dict):
    """Broadcast alert to all subscribers"""
    message = json.dumps({
        "type": "alert",
        "data": alert_data,
        "timestamp": datetime.utcnow().isoformat()
    })
    await manager.broadcast_to_topic("alerts", message)


async def broadcast_production_update(production_data: dict):
    """Broadcast production update to all subscribers"""
    message = json.dumps({
        "type": "production",
        "data": production_data,
        "timestamp": datetime.utcnow().isoformat()
    })
    await manager.broadcast_to_topic("production", message)
