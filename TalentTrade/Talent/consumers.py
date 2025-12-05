import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.current_user = self.scope['user']
        self.other_user_id = self.scope['url_route']['kwargs']['user_id']
        user_ids = sorted([self.current_user.id, int(self.other_user_id)])
        self.room_name = f'chat_{user_ids[0]}_{user_ids[1]}'     
        # Join room group
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )        
        # Accepta conexiunea
        await self.accept()       
        print(f"{self.current_user.username} joined room {self.room_name}")
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
            #Unique ID for THIS WebSocket connection
        )      
        print(f"{self.current_user.username} left room {self.room_name}")
    
    async def receive(self, text_data):
        # Parse message
        data = json.loads(text_data)
        message_text = data['message']      
        # Save to database (async)
        await self.save_message(message_text)
        
        # Send to everyone in the room group
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_message',
                'message': message_text,
                'sender': self.current_user.username,
                'sender_id': self.current_user.id
            }
        )
    
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'sender_id': event['sender_id']
        }))
    #Only put @database_sync_to_async on functions that do DATABASE OPERATIONS!
    @database_sync_to_async
    def save_message(self, message_text):
        # Save message to database
        receiver = User.objects.get(id=self.other_user_id)
        Message.objects.create(
            sender=self.current_user,
            receiver=receiver,
            content=message_text
        )

## **COMPLETE FLOW:**
# ```
# 1. Browser opens WebSocket
#    ws://localhost:8000/ws/chat/5/
#    ↓
# 2. connect() runs
#    - Saves user_id = 5
#    - Accepts connection
#    ↓
# 3. User types "Hello!" and clicks send
#    ↓
# 4. JavaScript sends through WebSocket:
#    {"message": "Hello!"}
#    ↓
# 5. receive() runs
#    - Parses JSON
#    - Saves to database
#    - Sends back to browser
#    ↓
# 6. Browser displays message
#    ↓
# 7. User closes tab
#    ↓
# 8. disconnect() runs
# -------------------------------------------------------------------------
# Channel Layer = The postal service
# Groups = Mailing lists
# channel_name = Your address
# group_send = Sending a mass email to everyone on the list!