from .dispatch_update import Dispatch
from .call import Call
from .create_message import CreateMessage
from .stop import Stop
from .start import Start
from .start_polling import StartPolling
from .webhook import Webhook

class Utilities(
  Dispatch,
  Call,
  CreateMessage,
  Stop,
  Start,
  StartPolling,
  Webhook
):
  pass