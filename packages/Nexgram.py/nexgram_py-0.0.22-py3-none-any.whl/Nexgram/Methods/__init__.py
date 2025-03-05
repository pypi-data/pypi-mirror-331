from .send_message import sendMessage
from .dispatch_update import Dispatch
from .decorators import Decorators
from .call import Call
from .forward_messages import ForwardMessages
from .copy_messages import CopyMessages
from .create_message import CreateMessage
from .stop import Stop

class Methods(
  sendMessage,
  Dispatch,
  Decorators,
  Call,
  ForwardMessages,
  CopyMessages,
  CreateMessage,
  Stop,
):
  pass