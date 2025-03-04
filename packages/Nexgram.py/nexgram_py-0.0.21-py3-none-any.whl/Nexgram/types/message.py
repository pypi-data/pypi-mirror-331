import json
from Nexgram.errors import *

class Message:
  def __init__(
    self,
    client: "Nexgram.Client",
    id: int,
    from_user: "Nexgram.types.User",
    chat: "Nexgram.types.Chat",
    reply_to_message: "Nexgram.types.Message",
    text: str = None,
  ):
    from Nexgram.types import User, Chat
    from Nexgram import Client
    
    if not isinstance(from_user, User): raise InvalidObject("You should pass 'Nexgram.types.User' object in 'from_user' argument not others.")
    if not isinstance(chat, Chat): raise InvalidObject("You should pass 'Nexgram.types.Chat' object in 'chat' argument not others.")
    if not isinstance(client, Client): raise InvalidObject("You should pass 'Nexgram.Client' object in 'client' argument not others")
    
    self._ = "Nexgram.types.Message"
    self.id = id
    self.from_user = from_user
    self.chat = chat
    if reply_to_message:
      if not isinstance(reply_to_message, self):
        raise InvalidObject("You should pass 'Nexgram.Client.Message' object in 'reply_to_message' argument not others")
      self.reply_to_message = reply_to_message
    self.text = text
    self.client = client
  
  def __repr__(self):
    mf = ["client"]
    data = {k: v for k, v in self.__dict__.items() if k not in mf}
    return json.dumps(
      data,
      indent=2,
      ensure_ascii=False,
      default=lambda o: o.__dict__ if hasattr(o, "__dict__") else o
    )
    
  async def reply(self, text: str, reply_markup = None,parse_mode: str = None):
    client = self.client
    await client.send_message(
      chat_id=self.chat.id,
      text=text,
      reply_markup=reply_markup,
      reply_to_message_id=self.id,
      parse_mode=parse_mode,
    )
  async def delete(self):
    client, api, url = self.client, self.client.api, self.client.ApiUrl
    return await api.post(url+"deleteMessage", {"chat_id": self.chat.id, "message_id": self.id})
  async def forward(self, chat_id):
    client, api, url = self.client, self.client.api, self.client.ApiUrl
    return await client.forward_messages(chat_id, self.chat.id, self.id)
  async def copy(self, chat_id, caption=None, parse_mode=None):
    client, api, url = self.client, self.client.api, self.client.ApiUrl
    return await client.copy_messages(chat_id, self.chat.id, self.id, caption=caption, parse_mode=parse_mode)
