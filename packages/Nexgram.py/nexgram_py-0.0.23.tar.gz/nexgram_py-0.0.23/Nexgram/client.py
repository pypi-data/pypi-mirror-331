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
    self.mode = None
    clients.append(self)
    # Decorators --
    self.on_message_listeners = {}
    self.on_disconnect_listeners = {}
    self.on_callback_query_listeners = {}
    self.on_inline_query_listeners = {}
    self.on_listeners = {}