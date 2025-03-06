import requests
from .settings import DEFAULTS

class MessageHandler:
    """
    This class lets you send messages via the given webhook.
    """
    def __init__(self, webhook_url:str|object):
        if type(webhook_url)==MessageHandler:
            self.webhook_url=webhook_url.webhook_url
        else:
            self.webhook_url=webhook_url

    def send(self, message, list_item_sep):
        """
        Send a message to the objects given webhook.
        """
        send_message(webhook_url=self.webhook_url, message=message, list_item_sep=list_item_sep)

def send_message(webhook_url:str|dict, message:str, list_item_sep:str=DEFAULTS["separator"]):
    """
    Send a message to a Discord webhook.
    """
    if( type(webhook_url)== dict):
        webhook_url=webhook_url["webhook"]
    payload = {"content": make_message(message, list_item_sep=list_item_sep)}
    requests.post(webhook_url, json=payload)

def make_message(input, list_item_sep=DEFAULTS["separator"]):
    """
    Converts strings, lists of strings, functions and other inputs into a single string and returns it.
    """
    final_message=""
    original_list_item_sep=list_item_sep
    
    if type(input)==str:
        final_message+=input

    elif callable(input):
        final_message+=str(input())

    elif type(input)==list:
        for item in input:
            if type(item)==Specialsep: # this exception has to exist because of how utils.py functions operate
                list_item_sep=item.separator
                continue
            final_message+=make_message(item, list_item_sep=list_item_sep)+list_item_sep
    else:
        final_message+=str(input)

    return final_message

class Specialsep():
    """Class used to define separator character exceptions for `makemessage`."""
    def __init__(self, separator=""):
        self.separator = separator

    def separator(self):
        return self.separator