# This is a class which can be used on CircuitPy boards, to manage files remotely via MIDI.
# The MidiBridgeWrapper class has the same send/receive methods like the adafruit MIDI handler, 
# so you can just put this in between: Create your adafruit MIDI handler, pass it to this class and
# use this in your application just like the adafruit handler, and the MIDI bridge will be able to
# communicate (as long as your application calls receive() regularily of course).

from time import sleep


# Manufacturer ID of PyMidiBridge (copy!)
_PMB_MANUFACTURER_ID = b'\x00\x7c\x7d' 


# This passes all MIDI through to/from the passed MIDI handler, plus the PyMidiBridge is 
# listening for commands to read/change the configuration files via SysEx.
class MidiBridgeWrapper:
    def __init__(self, 
                 midi, 
                 temp_file_path = None, 
                 storage_factory = None
        ):
        self._midi = midi

        # Storage wrapper to the filesystem
        if not storage_factory:
            def get_storage():
                from .MidiBridgeStorageProvider import MidiBridgeStorageProvider
                return MidiBridgeStorageProvider(          
                    temp_file_path = temp_file_path
                )
            
            storage_factory = get_storage

        self.__storage_factory = storage_factory

        # MIDI bridge (created on demand)
        self.__bridge = None

    @property
    def bridge(self):
        # Check if the message has the necessary attributes
        if not self.__bridge:
            from .PyMidiBridge import PyMidiBridge

            # MIDI bridge (sends and receives MIDI messages to transfer files)
            self.__bridge = PyMidiBridge(
                storage_factory = self.__storage_factory,
                midi = self,                               # The bridge calls send_system_exclusive to send its data
                event_handler = self                       # handle errors and messages here directly 
            )
        
        return self.__bridge

    # Called to send messages (this is directly forwarded to the MIDI handler)
    def send(self, midi_message):
        self._midi.send(midi_message)

    # Called to receive messages. All messages will be passed to the MIDI bridge first,
    # then returned to the caller.
    def receive(self):
        msg = self._midi.receive()
        
        if msg:
            # Only import the bridge when the first bessage comes in which really belongs to the bridge
            if hasattr(msg, "manufacturer_id") and hasattr(msg, "data") and msg.manufacturer_id == _PMB_MANUFACTURER_ID:
                if self.bridge.receive(msg):
                    # Message handled by the bridge.

                    # It is important to have some time between the MIDI receive calls,
                    # else SysEx messages will not come in completely and will be parsed as unknown events
                    # because the end status is not reached. We assume that after a bridge related message
                    # has been parsed, there will come more, so we wait here, not interfering with your normal
                    # communication.
                    sleep(0.01)

                    return None
            
        return msg
    
    # Sends the passed error message via MIDI and keeps receiving messages forever 
    # This method will never terminate!
    def error(self, messageOrException):
        # If it is an exception, convert to string
        if isinstance(messageOrException, Exception):
            messageOrException = self.get_trace(messageOrException)
        
        # Print error on console
        print(messageOrException)        

        # Send error message
        self.bridge.error(messageOrException)

        # Initiate a simple transmission loop to enable receiving files
        while True:
            self.receive()


    ## Callbacks ###################################################################################


    # Must send the passed data as MIDI system exclusive message (used by the bridge)
    def send_system_exclusive(self, manufacturer_id, data):
        from adafruit_midi.system_exclusive import SystemExclusive
        
        self._midi.send(
            SystemExclusive(
                manufacturer_id = manufacturer_id,
                data = data
            )
        )

    # Called when the bridge received an error message
    def handle(self, message):
        print(repr(message))

    # Called when the bridge received notice about a finished transfer on the other side
    def transfer_finished(self, file_id_bytes):
        pass

    # Returns the trace of an exception
    def get_trace(self, exception):
        import traceback     
        return str(traceback.format_exception(None, exception, exception.__traceback__))

