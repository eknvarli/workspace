from __future__ import annotations

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from organizations.models import WorkspaceMember


class WorkspaceConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.organization_id = self.scope['url_route']['kwargs']['organization_id']
        self.user = self.scope['user']
        if self.user.is_anonymous or not await self._has_membership():
            await self.close()
            return

        self.organization_group = f'organization_{self.organization_id}'
        self.user_group = f'user_{self.user.id}'
        await self.channel_layer.group_add(self.organization_group, self.channel_name)
        await self.channel_layer.group_add(self.user_group, self.channel_name)
        await self.accept()
        await self.send_json({'event': 'connection.ready', 'payload': {'organization_id': self.organization_id}})

    async def disconnect(self, close_code):
        if hasattr(self, 'organization_group'):
            await self.channel_layer.group_discard(self.organization_group, self.channel_name)
        if hasattr(self, 'user_group'):
            await self.channel_layer.group_discard(self.user_group, self.channel_name)

    async def receive_json(self, content, **kwargs):
        if content.get('event') == 'presence.ping':
            await self.send_json({'event': 'presence.pong', 'payload': {'status': 'ok'}})

    async def workspace_event(self, event):
        await self.send_json({'event': event['event'], 'payload': event['payload']})

    @database_sync_to_async
    def _has_membership(self) -> bool:
        return WorkspaceMember.objects.filter(organization_id=self.organization_id, user=self.user).exists()
