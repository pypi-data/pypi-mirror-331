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
        message = await self.create_message(m)
        for x in self.on_message_listeners:
          asyncio.create_task(self.call(self.on_message_listeners, x, self, message))
      except Exception as e:
        log.error(f"[DispatchUpdate] Line 17: {e}, message: {m}")
    if update.get("callback_query"):
      try:
        m = update.get("callback_query")
        message = await self.create_message(m, type="callback_query")
        for x in self.on_callback_query_listeners:
          asyncio.create_task(self.call(self.on_callback_query_listeners, x, self, message))
      except Exception as e:
        log.error(f"[DispatchUpdate] Line 25: {e}, message: {m}")