import storage
from htl_keyboard import HtlKeyboard


hw_keyboard = HtlKeyboard()

if not hw_keyboard.key0:
    storage.disable_usb_drive()

