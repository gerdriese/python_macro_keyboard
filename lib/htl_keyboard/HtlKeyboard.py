import board
import digitalio
import rotaryio
from adafruit_debouncer import Debouncer


class HtlKeyboard:
    """ HTL Keyboard - Tastenverwaltung
    """
    def __init__(self):
        """__init__  HTL Keyboard - Tastenabfrage
        """
        self.PIXEL_PIN = board.GP28
        self.ROTARY1 = board.GP1
        self.ROTARY2 = board.GP0
        self.ROTKEY = board.GP2
        self.KEYS = [self.ROTKEY, board.GP26, board.GP22, board.GP21, board.GP20, board.GP19, board.GP18, board.GP17, board.GP16]
        self.keys = {}
        self.keys_d = {}
        
        # Tasten definieren
        for i in range(9):
            x = digitalio.DigitalInOut(self.KEYS[i])
            x.direction = digitalio.Direction.INPUT
            x.pull = digitalio.Pull.UP
            d = Debouncer(x)
            self.keys[f"key{i}"] = x
            self.keys_d[f"key{i}"] = d
        
        # Encoder initialisieren:
        self.encoder = rotaryio.IncrementalEncoder(self.ROTARY1, self.ROTARY2)
        self.last_position = None


        
    def __getattr__(self, attr: str) -> bool:
        """__getattr__ Liefert den  Status der Tasten [key0..key8] zurück. True: gedrückt, False: nicht gedrückt

        Args:
            attr (str): Taste [key0..key8]

        Returns:
            bool: True: Taste gedrückt, False: Taste nicht gedrückt oder nicht bekannt
        """
        if int(attr[3]) in range(9):
            i = int(attr[3])
            return(not self.keys[f"key{i}"].value)
        return False

    def key_pressed(self) -> list:
        pressed = []
        for key, key_object in self.keys.items():
            if not key_object.value:
                pressed.append(key)
        pressed.sort()
        return pressed 

    def key_pressed_debounced(self) -> list:
        pressed = []
        for key, key_object in self.keys_d.items():
             key_object.update()
             if key_object.fell:
                 pressed.append(key)
        pressed.sort()
        return pressed

    def get_encoder_value(self) -> int:
        return self.encoder.position