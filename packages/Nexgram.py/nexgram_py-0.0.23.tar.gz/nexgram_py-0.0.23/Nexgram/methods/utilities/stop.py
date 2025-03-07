class Stop:
  async def stop(self):
    await self.trigger_disconnect()
    self.polling = False
    self.connected = False
    self.log.info("Client stopped.")