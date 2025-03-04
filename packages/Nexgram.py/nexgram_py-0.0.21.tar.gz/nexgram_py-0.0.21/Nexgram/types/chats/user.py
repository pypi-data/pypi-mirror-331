import json

class User:
  def __init__(
    self,
    id: int,
    first_name: str,
    last_name: str = None,
    username: str = None,
    is_self: bool = False,
    is_bot: bool = False,
  ):
    self._ = "Nexgram.types.User"
    self.id = id
    self.is_self = is_self
    self.is_bot = is_bot
    self.first_name = first_name
    if last_name: self.last_name = last_name
    if username: self.username = username
      
  def __repr__(self):
    return json.dumps(self.__dict__, indent=2, ensure_ascii=False)