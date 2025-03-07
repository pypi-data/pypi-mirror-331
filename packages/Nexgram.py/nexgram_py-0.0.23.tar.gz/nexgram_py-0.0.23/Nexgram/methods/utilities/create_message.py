from Nexgram.types import *

class CreateMessage:
  async def create_message(self, data, update_type='message'):
    frm = data.get('from_user') or data.get('from')
    chat = data.get('chat')
    callback_query_message = data.get('message')
    forward_from = data.get('forward_from')
    forward_from_chat = data.get("forward_from_chat")
    
    if frm:
      from_user = User(
        client=self,
        id=frm.get('id'),
        first_name=frm.get('first_name'),
        last_name=frm.get('last_name'),
        username=frm.get('username'),
        is_bot=frm.get('is_bot'),
      )  
    if chat:
      chat = Chat(
        id=chat.get('id'),
        title=chat.get('title'),
        first_name=chat.get('first_name'),
        last_name=chat.get('last_name'),
        type=chat.get('type'),
        username=chat.get('username'),
      )
    if callback_query_message:
      callback_query_message = await self.create_message(callback_query_message)
    if forward_from:
      forward_from = User(
        client=self,
        id=forward_from.get('id'),
        first_name=forward_from.get('first_name'),
        last_name=forward_from.get('last_name'),
        username=forward_from.get("username"),
        is_bot=forward_from.get("is_bot")
      )
    if forward_from_chat:
      forward_from_chat = Chat(
        id=forward_from_chat.get('id'),
        title=forward_from_chat.get('title'),
        first_name=forward_from_chat.get('first_name'),
        last_name=forward_from_chat.get('last_name'),
        type=forward_from_chat.get('type'),
        username=forward_from_chat.get('username'),
      )
    if update_type == "message":
      return Message(
        client=self,
        id=data.get('message_id') or data.get('id'),
        from_user=from_user,
        chat=chat,
        forward_from=forward_from,
        forward_from_chat=forward_from_chat,
        reply_markup=None,
        caption=data.get('caption'),
        text=data.get('text')
      )
    elif update_type == "callback_query":
      return CallbackQuery(
        client=self,
        id=data.get('id'),
        from_user=from_user,
        message=callback_query_message,
        data=data.get('data')
      )
    elif update_type == "inline_query":
      return InlineQuery(
        client=self,
        id=data.get('id'),
        from_user=from_user,
        query=data.get('query'),
        offset=data.get('offset')
      )