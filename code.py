# Allgemeine Imports
from random import choice
import time
import board
import neopixel
import usb_hid
import json

# HTL Bibliothek
from lib.htl_keyboard import HtlKeyboard

# Tastatur - Adafruit Code mit DE Erweiterung
from adafruit_hid.keyboard import Keyboard
from keyboard_layout_win_de import KeyboardLayout
from keycode_win_de import Keycode
from consumer_control_extended import ConsumerControlExtended
from adafruit_hid.consumer_control import ConsumerControl

# Definitionen
PIXEL_PIN = board.GP28
ORDER = neopixel.GRB
# Anzahl der RGB Leds ist 11 - 0 bis 7 sind unter den Tastern 1 bis 8, die LEDS 8, 9 und 10
# befinden sich unter dem Raspberry Pi Pico
NUM_PIXELS = 11
# Nur die ersten acht LEDS werden für den Color Change herangezogen
COLOR_CHANGE = 8
# Farbdefinitionen
COLOR_FILE_NOT_FOUND = 0xFF3300  # Konfigurationsdatei konnte nicht gelesen werden
COLOR_FORMAT_ERROR = 0x330000  # Konfigurationsdatei nicht gefunden oder fehlerhaft
COLOR_UNKNOWN = 0x424242  # Kommando nicht bekannt
COLOR_UNDEFINED = 0x0000FF  # Kein Kommando für die Taste hinterlegt
COLOR_LOAD_SUCCESS = 0x00FF00  # Datei korrekt geladen
COLOR_LOAD_SUCCESS_DEV = 0x00FFFF  # Datei korrekt geladen und Laufwerk aktiviert
COLOR_EMPTY = 0x000000  # Led ausschalten

# Sollen Debugmeldungen auf die serielle Schnittstelle ausgegeben werden?
DEBUG = True

# Initialisierung:
pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS,
                           brightness=0.2, auto_write=False, pixel_order=ORDER)

# USB Endpoints
consumer_control = ConsumerControl(usb_hid.devices)
sw_keyboard = Keyboard(usb_hid.devices)

hw_keyboard = HtlKeyboard()
keyboard_layout = KeyboardLayout(sw_keyboard)

encoder = 0
pixelcount = 0
COLOR_MODES = ["wave", "rainbow", "single", "wheel"]
ACCEPTABLE_KEYS = ["key0", "key1", "key2", "key3", "key4", "key5", "key6", "key7", "key8"]
current_color = 0
leds_on = True
catch_game = False
catch_moves = [(1, 2), (0, 3), (0, 3, 5), (1, 2, 4, 6),
               (3, 7), (2, 6), (3, 5, 7), (4, 6)]

# ----------------------- Hier die zusätzlichen Funktionen hinschreiben ----------------------- #


# ============================================================================================= #

def init_catch():
    global catch_game, catch_pos, catch_lives, catch_cooldown, catch_score
    catch_game = True
    catch_pos = 3
    catch_lives = 3
    catch_cooldown = 8
    catch_score = 0
    pixels.fill(COLOR_EMPTY)
    pixels[3] = COLOR_UNKNOWN
    pixels.show()
    time.sleep(3)


def colormodechange():
    global colormode
    pixels.fill(COLOR_EMPTY)
    colormode = COLOR_MODES[(COLOR_MODES.index(
        colormode) + 1) % len(COLOR_MODES)]
    debugprint(f"Colormode ist jetzt {colormode}")


def ledtoggle():
    global leds_on
    if leds_on == True:
        leds_on = False
        pixels.fill(COLOR_EMPTY)
        pixels.show()
    else:
        leds_on = True

def blink(color):
    pixels.fill(color)
    pixels.show()
    time.sleep(1)
    pixels.fill(COLOR_EMPTY)
    pixels.show()
    

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
        pos (int): Zahl von 0 bis 255

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
    # Spannendes return voraus - return <Tupel A> if <Bedingung> else <Tupel B>... Ja - das gibt's auch :)
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)


def send_keys(keyspressed: tuple):
    debugprint(f"Attempting to send key(s) {keyspressed}")
    if keyspressed in keyconf:
        for command in keyconf[keyspressed]:
            # sicher ist SICHER ;)
            command[0] = command[0].upper()
            # P: Key Press - Taste drücken und gedrückt halten
            if command[0] == "P":
                sw_keyboard.press(getattr(Keycode, command[1]))
            # U: Key Up - Taste loslassen
            elif command[0] == "U":
                sw_keyboard.release(getattr(Keycode, command[1]))
            # R: Release - Alle Tasten loslassen
            elif command[0] == "R":
                sw_keyboard.release_all()
            # D: Delay
            elif command[0] == "D":
                time.sleep(command[1])
            # T: Text ausgeben
            elif command[0] == "T":
                keyboard_layout.write(command[1])
            # M: Consumer Control / Multimedia Kommando
            elif command[0] == "C":
                if hasattr(ConsumerControlExtended, command[1]):
                    consumer_control.send(
                        getattr(ConsumerControlExtended, command[1]))
                else:
                    debugprint(f"Could not send consumer control code {command[1]}")
                    blink(COLOR_UNKNOWN)
                
            # F: Funktion ausführen
            elif command[0] == "F":
                if command[1] in globals():
                    debugprint(f"Funktion ausführen: {command[1]}")
                    if len(command) == 2:
                        globals()[command[1]]()
                    elif len(command) == 3:
                        globals()[command[1]](command[2])
                    else:
                        pixels.fill(COLOR_UNKNOWN)
                        pixels.show()
                        time.sleep(1)
                        pixels.show()
                else:
                    debugprint(f"Funktion {command[1]} existiert nicht")
                    blink(COLOR_UNKNOWN)
            # Unbekanntes Kommand
            else:
                blink(COLOR_UNKNOWN)
    else:
        blink(COLOR_UNDEFINED)


# Konfiguration einlesen:
def read_config_from_file() -> json:
    try:
        with open("keyconf.json", "r") as f:
            keyconf = json.load(f)
        for k in list(keyconf.keys()):
            if "+" in k:
                new = tuple(sorted(k.split("+")))
                keyconf[new] = keyconf[k]
                debugprint(f"Initialized Keys {k} -> {new} with {keyconf[new]}")
                del keyconf[k]
            elif DEBUG and k.startswith("key"):
                debugprint(f"Initialized Key {k} with {keyconf[k]}")
        return keyconf
    
    except OSError as e:
        debugprint(f"Konfigurationsdatei konnte nicht gelesen werden!\n{e}")
        for _ in range(50):
            pixels.fill(COLOR_FILE_NOT_FOUND)
            pixels.show()
            time.sleep(.4)
            pixels.fill(COLOR_EMPTY)
            pixels.show()
            time.sleep(.3)

    except ValueError as e:
        debugprint(f"Fehler in der Konfiguratioinsdatei!\n{e}")
        for _ in range(50):
            pixels.fill(COLOR_FORMAT_ERROR)
            pixels.show()
            time.sleep(.4)
            pixels.fill(COLOR_EMPTY)
            pixels.show()
            time.sleep(.3)



# Hauptprogramm:

# Konfiguration der Tasten einlesen
keyconf = read_config_from_file()

startup_leds = keyconf.get('startup_leds', [1, 0, 2, 3, 4, 7, 6, 5, 10, 9, 8])
if not (isinstance(startup_leds, (list, tuple))) or not all(isinstance(i, int) and i in range(11) for  i in startup_leds):
    startup_leds = [1, 0, 2, 3, 4, 7, 6, 5, 10, 9, 8]

color_change_key = keyconf.get('color_change_key', 'key8')
if not color_change_key in ACCEPTABLE_KEYS:
    color_change_key = 'key8'

colormode = keyconf.get('colormode', "wave")
if not colormode in COLOR_MODES:
    colormode = 'wave'

rage_quit_keys = keyconf.get('rage_quit_keys', 12)
if not isinstance(rage_quit_keys, int) or rage_quit_keys < 1:
    rage_quit_keys = 12

game_difficulty = keyconf.get('game_difficulty', 8)
if not isinstance(game_difficulty, int):
    game_difficulty = 8

# Wenn das Laufwerk angeschlossen wird nicht grün sondern hellblau leuchten
startup_color = COLOR_LOAD_SUCCESS_DEV if 'key0' in hw_keyboard.key_pressed() else COLOR_LOAD_SUCCESS

for i in startup_leds:
    pixels[i] = startup_color
    pixels.show()
    time.sleep(0.1)
pixels.fill(COLOR_EMPTY)
time.sleep(0.7)

# Da unser Python Programm das einzige laufende Programm ist, darf es nicht enden ->
# wir verwenden hier bewusst eine Endlosschleife
while True:
    # Tastendrücke abfragen - keys_pressed liefert eine Liste zurück - wenn diese nicht leer ist, wurde mindestens eine Taste gedrückt
    # get_encoder_value liefert den aktuellen Wert des Drehencoders zurück - so kann später überprüft werden, ob er gedreht wurde.
    keys_pressed = hw_keyboard.key_pressed_debounced()
    new_encoder = hw_keyboard.get_encoder_value()

    keylen = len(keys_pressed)
    # Eine oder mehrere Tasten wurden gedrückt
    if keylen:
        debugprint(keys_pressed)
    if catch_game:
        # Verbliebene Leben anzeigen
        pixels.fill(COLOR_EMPTY)
        for i in range(catch_lives):
            pixels[i + 8] = 0xaa1010
        pixels[catch_pos] = COLOR_UNKNOWN
        pixels.show()

        # Taste wurde gedrückt
        if keylen == 1:
            if keys_pressed[0] == "key0":
                catch_game = False
                pixels.fill(COLOR_EMPTY)

            # Selbe Position = gewonnen
            elif (keypos := (int(keys_pressed[0][3]) - 1)) == catch_pos:
                catch_score += 1
                for i in range(4):
                    pixels.fill(COLOR_LOAD_SUCCESS)
                    pixels.show()
                    time.sleep(.075)
                    pixels.fill(COLOR_EMPTY)
                    pixels.show()
                    time.sleep(.075)

            # Andere Position = verloren
            else:
                for i in range(4):
                    pixels.fill(COLOR_FORMAT_ERROR)
                    pixels.show()
                    time.sleep(.075)
                    pixels.fill(COLOR_EMPTY)
                    pixels.show()
                    time.sleep(.075)

                catch_lives -= 1
                pixels[keypos] = COLOR_FORMAT_ERROR
                pixels[catch_pos] = COLOR_LOAD_SUCCESS
                pixels.show()
                time.sleep(1.5)
                if catch_lives == 0:
                    for i in range(3):
                        pixels.fill(COLOR_FILE_NOT_FOUND)
                        pixels.show()
                        time.sleep(.75)
                        pixels.fill(COLOR_FORMAT_ERROR)
                        pixels.show()
                        time.sleep(.75)
                    for i in startup_leds[::-1]:
                        pixels[i] = COLOR_EMPTY
                        pixels.show()
                        time.sleep(.2)
                    pixels.fill(COLOR_EMPTY)
                    pixels.show()
                    time.sleep(1)
                    debugprint(catch_score)
                    catch_game = False

        if catch_cooldown:
            catch_cooldown -= 1
        else:
            catch_cooldown = 8
            catch_pos = choice(catch_moves[catch_pos])

    else:
        # Leds darstellen
        if leds_on:
            if colormode == "wave":
                pixelcount = (pixelcount + 3) % 256
                # Wheel:
                for i in range(COLOR_CHANGE):
                    pixel_index = (i * 256 // NUM_PIXELS) + pixelcount
                    pixels[i] = wheel(pixel_index & 255)

            elif colormode == "rainbow":
                for i in range(COLOR_CHANGE):
                    pixel_index = (i * 256 // NUM_PIXELS) + pixelcount
                    pixels[i] = wheel(pixel_index & 255)

            elif colormode == "single":
                pixels.fill(wheel(current_color))

            elif colormode == "wheel":
                current_color = (current_color + 1) % 256
                pixels.fill(wheel(current_color & 255))

            pixels.show()

        if keylen >= rage_quit_keys:
            send_keys(("ragequit"))

        elif keylen > 0:
            send_keys(tuple(keys_pressed) if keylen > 1 else keys_pressed[0])

        if encoder != new_encoder:
            # Wenn color_change_key gedrückt ist, wird aus dem Lautstärkeregler ein Farbregler
            if leds_on == True and getattr(hw_keyboard, color_change_key):
                if colormode in ('wave', 'rainbow'):
                    if encoder < new_encoder:
                        pixelcount = (pixelcount + 7) % 256
                    else:
                        pixelcount = (pixelcount - 7) % 256
                else:
                    if encoder < new_encoder:
                        current_color = (current_color + 7) % 256
                    else:
                        current_color = (current_color - 7) % 256
            # Lautstärkeregelung
            else:
                if encoder > new_encoder:
                    consumer_control.send(ConsumerControlExtended.VOLUME_UP)
                else:
                    consumer_control.send(ConsumerControlExtended.VOLUME_DOWN)
            # den "neuen" Encoder Wert speichern damit wir die nächste Änderung mitbekommen...
            encoder = new_encoder
            debugprint(f"Neuer Encoderwert: {encoder}")

    time.sleep(0.03)
