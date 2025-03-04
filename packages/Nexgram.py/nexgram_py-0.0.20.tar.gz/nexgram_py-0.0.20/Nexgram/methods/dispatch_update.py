from Nexgram.errors import *
from Nexgram.types import *
import asyncio

class Dispatch:
  async def dispatch_update(self, update):
    log = self.log
    for gf in self.on_listeners:
      asyncio.create_task(gf(update))
    if update.get('message'):
      try:
        m = update.get('message')
        frm = m.get('from')
        ch = m.get('chat')
        from_user = User(
          frm['id'],
          frm['first_name'],
          username=frm.get('username'),
          is_bot=frm.get('is_bot'),
          is_self=frm['id'] == self.me.id,
        )
        chat = Chat(
          id=ch['id'],
          title=ch.get('title'),
          first_name=ch.get('first_name'),
          last_name=ch.get('last_name'),
          type=ch.get('type'),
          username=ch.get('username')
        )
        reply_to_message = None
            
        message = Message(
          client=self,
          id=m['message_id'],
          from_user=from_user,
          chat=chat,
          reply_to_message=reply_to_message,
          text=m.get('text')
        )
        
        for x in self.on_message_listeners:
          asyncio.create_task(self.call(self.on_message_listeners, x, self, message))
      except Exception as e:
        log.error(f"[DispatchUpdate] Line 44: {e}, message: {m}")