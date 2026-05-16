"""
WebSocket consumer - real vaqt monitoring
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class FieldMonitoringConsumer(AsyncWebsocketConsumer):
    """Dala monitoring uchun WebSocket consumer"""

    async def connect(self):
        self.field_id = self.scope['url_route']['kwargs']['field_id']
        self.group_name = f"field_{self.field_id}"

        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info(f"WebSocket connected: field={self.field_id}, user={user.username}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        logger.info(f"WebSocket disconnected: field={self.field_id}, code={close_code}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            if data.get('type') == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))
        except json.JSONDecodeError:
            pass

    async def sensor_reading(self, event):
        """Sensor o'lchovi kelganda frontendga yuborish"""
        await self.send(text_data=json.dumps({
            'type': 'sensor_reading',
            'sensor_id': event.get('sensor_id'),
            'sensor_type': event.get('sensor_type'),
            'value': event.get('value'),
            'unit': event.get('unit'),
            'timestamp': event.get('timestamp'),
        }))

    async def irrigation_status(self, event):
        """Sug'orish holati o'zgarganda frontendga yuborish"""
        await self.send(text_data=json.dumps({
            'type': 'irrigation_status',
            'status': event.get('status'),
            'event_id': event.get('event_id'),
        }))
