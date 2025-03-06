from .messages import MessageHandler
from .utils import code_block
from .settings import DEFAULTS

class Notifier:
    """Context manager class with built in messaging and error handling.
    
    Requires a `DcalertsSettings` object to set parameters.
    """
    def __init__(self,dcalerts_settings:dict):
        
        self.messagehandler=MessageHandler(dcalerts_settings.get("webhook"))
        self.before=dcalerts_settings.get("before", DEFAULTS["before"])
        self.after=dcalerts_settings.get("after", DEFAULTS["after"])
        self.list_item_sep = dcalerts_settings.get("separator", DEFAULTS["separator"])
        self.send_error=dcalerts_settings.get("send_error", DEFAULTS["send_error"])
        self.error_message=dcalerts_settings.get("error_message", DEFAULTS["error_message"])

    def __enter__(self):
        if self.before:
            self.send(self.before)
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        if exc_type is not None and self.send_error:
            error_message = ["ERROR:" if self.error_message is None else self.error_message, code_block(str(exc_type.__name__)+": "+str(exc_val))]
            self.send(error_message)
            return False
        
        if self.after:
            self.send(self.after)
    
    def send(self,message):
        self.messagehandler.send(message, self.list_item_sep)