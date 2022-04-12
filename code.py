# Allgemeine Imports

import time
import board
import neopixel
import usb_hid
import json


# HTL Bibliothek
from htl_keyboard import HtlKeyboard

# Tastatur - Adafruit Code mit DE Erweiterung
from adafruit_hid.keyboard import Keyboard
from keyboard_layout_win_de import KeyboardLayout
from keycode_win_de import Keycode
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.consumer_control import ConsumerControl

# Definitionen
PIXEL_PIN = board.GP28
ORDER = neopixel.GRB
NUM_PIXELS = 11
COLOR_CHANGE = 8
DEBUG = True

# Initialisierung:
pixels = neopixel.NeoPixel(
    PIXEL_PIN, NUM_PIXELS, brightness=0.2, auto_write=False, pixel_order=ORDER
)
hw_keyboard = HtlKeyboard()
consumer_control = ConsumerControl(usb_hid.devices)
sw_keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayout(sw_keyboard)
encoder = 0
pixelcount = 0
leds_on = True


def debugprint(outtext: str) -> None:
    """debugprint Ausgabe über die Serielle Schnittstelle - Ist die globale Variable DEBUG True, wird der Text ausgegeben

    Args:
        outtext (str): Auszugebender Text
    """
    if DEBUG:
        print(outtext)


def wheel(pos: int) -> tuple:
    """wheel  Verwandelt eine Zahl von 0 bis 255 in RGB Werte für einen Farbwechsel von R zu G zu B retour zu R

    Args:
        pos (_type_): Zahl von 0 bis 255

    Returns:
        tuple: R,G,B Farbwerte
    """
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)


def send_keys(keypressed: str) -> None:
    if keypressed in keyconf:
        for command in keyconf[keypressed]:
            # P: Key Press - Taste drücken und gedrückt halten
            if command[0] == "P":  
                sw_keyboard.press(getattr(Keycode,command[1]))
            # U: Key Up - Taste loslassen
            elif command[0] == "U":
                sw_keyboard.release(getattr(Keycode,command[1]))
            # R: Release - Alle Tasten loslassen
            elif command[0] == "R":
                sw_keyboard.release_all()
            # D: Delay
            elif command[0] == "D":
                time.sleep(command[1])
            # T: Text ausgeben
            elif command[0] == "T":
                keyboard_layout.write(command[1])
    else:
        pixels.fill(0x0000FF)
        pixels.show()
        time.sleep(1)
        pixels.fill(0x000000)
        pixels.show()

#Konfiguration einlesen:

try:
    with open("keyconf.json") as f:
        keyconf = json.load(f)
except OSError as e:
    debugprint(f"Konfigurationsdatei konnte nicht gelesen werden!\n{e}")
    pixels.fill(0xFF3300)
    pixels.show()
    while True:
        pass
except ValueError as e:
    debugprint(f"Fehler in der Konfiguratioinsdatei!\n{e}")
    pixels.fill(0x330000)
    pixels.show()
    while True:
        pass

# Hauptprogramm:
while True:
    keys_pressed = hw_keyboard.key_pressed_debounced()
    new_encoder = hw_keyboard.get_encoder_value()

    # Eine Taste wurde gedrückt
    if len(keys_pressed) == 1:
        debugprint(keys_pressed)
        if "key0" in keys_pressed:
            consumer_control.send(ConsumerControlCode.MUTE)
        else:
            send_keys(keys_pressed[0])

    # LEDs ein- und ausschalten (Tasten 6 + 7 + 8 gleichzeitig drücken) 
    if len(keys_pressed) == 3 and ["key6", "key7", "key8"] == keys_pressed:
        debugprint(keys_pressed)
        if leds_on == True:
            leds_on = False
            pixels.fill((0, 0, 0))
        else:
            leds_on = True

    # Lautstärkeregelung
    if encoder != new_encoder:
        if encoder < new_encoder:
            consumer_control.send(ConsumerControlCode.VOLUME_INCREMENT)
        else:
            consumer_control.send(ConsumerControlCode.VOLUME_DECREMENT)
        encoder = new_encoder
        debugprint(f"Neuer Encoderwert: {encoder}")

    # Wheel:
    pixelcount += 3
    if pixelcount > 255:
        pixelcount -= 255

    if leds_on:
        for i in range(COLOR_CHANGE):
            pixel_index = (i * 256 // NUM_PIXELS) + pixelcount
            pixels[i] = wheel(pixel_index & 255)
    pixels.show()
    time.sleep(0.03)
