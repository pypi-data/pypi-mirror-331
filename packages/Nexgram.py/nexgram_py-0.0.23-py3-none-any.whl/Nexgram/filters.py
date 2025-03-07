import logging
import inspect
import asyncio

log = logging.getLogger(__name__)

class Filter:
  def __init__(self, func):
    self.func = func
    self.is_async = inspect.iscoroutinefunction(func)
  async def __call__(self, *args, **kwargs):
    if self.is_async:
      return await self.func(*args, **kwargs)
    return self.func(*args, **kwargs)
  def __and__(self, other):
    async def combined(*args, **kwargs):
      r1 = await self(*args, **kwargs) if self.is_async else self(*args, **kwargs)
      r2 = await other(*args, **kwargs) if other.is_async else other(*args, **kwargs)
      return r1 and r2
    return Filter(combined)
  def __or__(self, other):
    async def combined(*args, **kwargs):
      r1 = await self(*args, **kwargs) if self.is_async else self(*args, **kwargs)
      r2 = await other(*args, **kwargs) if other.is_async else other(*args, **kwargs)
      return r1 or r2
    return Filter(combined)
  def __invert__(self):
    async def inverted(*args, **kwargs):
      r1 = await self(*args, **kwargs) if self.is_async else self(*args, **kwargs)
      return not r1
    return Filter(inverted)
    
def create(func):
  if isinstance(func, Filter):
    return func
  name = getattr(func, "__name__", "CustomFilter")
  return type(name, (Filter,), {"__call__": func})(func)
     
text = create(lambda _, message: message.text)

def command(cmd, prefix=['/']):
  async def wrapper(_, __, m):
    p = next((p for p in prefix if m.text.startswith(p)), None)
    return p and (m.text[len(p):] in cmd if isinstance(cmd, list) else m.text[len(p):] == cmd)
  return create(wrapper)
  
def user(id):
  async def wrapper(_, __, m):
    if isinstance(id, (int, str)) and str(id).isdigit():
      return m.from_user.id == int(id)
    elif isinstance(id, list):
      return any(user(u)(_, __, m) for u in id)
    urls = ["http://t.me/", "https://t.me/", "www.t.me/", "@", "http://telegram.dog/", "https://telegram.dog/"]
    return any(id.replace(x, "").lower() == m.from_user.username.lower() for x in urls)
  return create(wrapper)
  
def chat(id):
  async def wrapper(_, __, m):
    if isinstance(id, (int, str)) and str(id).replace('-', '').isdigit():
      return m.chat.id == int(id)
    elif isinstance(id, list):
      return any(chat(c)(_, __, m) for c in id)
    urls = ["http://t.me/", "https://t.me/", "www.t.me/", "@", "http://telegram.dog/", "https://telegram.dog/"]
    return any(id.replace(x, "").lower() == (m.chat.username or "").lower() for x in urls)
  return create(wrapper)