DEFAULTS={
    "before":None,
    "after":None,
    "separator":" ",
    "send_error":False,
    "error_message":"ERROR:"
}

class DcalertsSettings(dict):
    """A dictionary-like class used to set the parameters in other `dcalerts` functions.
    
    This is where you can set what messages you want to send and to what webhook.
    Accepts lists and functions as messages, which will be evaluated and sent together as one string.
    You can specify a list item separator and send error messages as well.
    If a message isn't given it will not be sent. If an error occurs, the error message will be sent.
    
    Attributes:
        webhook (str | MessageHandler): Required webhook URL you get from Discord.
        before (str | list | func, optional): A value to be included before the main content (default: None).
        after (str | list | func, optional): A value to be appended after the main content (default: None).
        separator (str, optional): A string used to separate elements (default: " ").
        send_error (bool, optional): Determines whether to send an error message (default: False).
        error_message (str | list | func, optional): The default error message content (default: "ERROR:").

    Example Usage:

    DcalertsSettings(
        webhook = webhook_url,
        before = "Starting code execution",
        after = ["Code finished. Results:", code_block(result_func())],
        separator='\\n',
        send_error = True,
        error_message="An error occured:"
    )
    """

    allowed_keys = {"webhook", "before", "after", "separator", "send_error", "error_message"}

    def __init__(self, webhook, before=DEFAULTS["before"], after=DEFAULTS["after"], separator=DEFAULTS["separator"], send_error=DEFAULTS["send_error"], error_message=DEFAULTS["error_message"]):
        if not webhook:
            raise ValueError("You have to set a webhook.")
        
        #initialization with aother dict
        if type(webhook)==dict:
            hook=webhook.get("webhook")
            if hook is None:
                raise ValueError("You have to set a webhook.")
            super().__init__({
                "webhook": hook,
                "before": webhook.get("before", before),
                "after": webhook.get("after", after),
                "separator": webhook.get("separator", separator),
                "send_error": webhook.get("send_error", send_error),
                "error_message": webhook.get("error_message", error_message)
            })
        #initialization with parameters
        else:
            super().__init__({
                "webhook": webhook,
                "before": before,
                "after": after,
                "separator": separator,
                "send_error": send_error,
                "error_message": error_message
            })

    def __setitem__(self, key, value):
        if key not in self.allowed_keys:
            raise KeyError(f"Key '{key}' is not allowed. Allowed keys: {self.allowed_keys}")
        super().__setitem__(key, value)