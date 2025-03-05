import logging
import httpx
import aiohttp
import asyncio
from .methods import *
from .errors import *
from .types import *
from .api import Api

log = logging.getLogger(__name__)
clients = []

class Client(Methods):
  def __init__(
    self,
    name: str,
    bot_token: str,
  ):
    self.name = name
    self.bot_token = bot_token
    self.connected = False
    self.me = None
    self.offset = 0
    self.polling = False
    self.ApiUrl = f"https://api.telegram.org/bot{self.bot_token}/"
    self.api = Api()
    self.log = log
    clients.append(self)
    # Decorators --
    self.on_message_listeners = {}
    self.on_disconnect_listeners = {}
    self.on_callback_query_listeners = {}
    self.on_inline_query_listeners = {}
    self.on_listeners = {}
    
  async def start(self, start_polling=True):
    url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
    async with aiohttp.ClientSession() as session:
      async with session.get(url) as r:
        r = await r.json()
        if r.get("ok"):
          self.connected = True
          r = r["result"]
          self.me = User(
            client=self,
            id=r['id'],
            first_name=r['first_name'],
            username=r['username'],
            is_self=True,
            is_bot=True,
          )
          log.info(f"Client connected as {self.me.first_name} (@{self.me.username})")
          if start_polling:
            asyncio.create_task(self.start_polling())
            log.info("Exp. Feature Started: Loop created.")
          return self.me
        raise ValueError("Failed to connect with your bot token. Please make sure your bot token is correct.")

  async def start_polling(self):
    if not self.connected:
      raise ConnectionError("Client is not connected. Please connect the client and start polling.")
    elif self.polling: raise PollingAlreadyStartedError("Polling already started, why you trying again and again? didn't you receive any updates?")
    self.polling = True
    log.info("Nexgram.py - polling started!")
    first_start = True
    max_retry, retry = 25, 0
    while self.polling:
      try:
        params = {"offset": self.offset, "timeout": 15}
        updates = await self.api.get(self.ApiUrl+"getUpdates", params=params)
        if "result" in updates and not first_start:
          for update in updates["result"]:
            self.offset = update["update_id"] + 1
            asyncio.create_task(self.dispatch_update(update))
        elif "result" in updates and first_start:
          first_start = False
      except Exception as e:
        if retry > max_retry:
          break
        log.error(f"[{retry}/{max_retry}] Error in polling: {e}")
        retry += 1
    await self.stop()
  
  async def __aenter__(self):
    return self
  async def __aexit__(self, exc_type, exc, tb):
    pass