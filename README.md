# Python Macro Keyboard

Hier wird der Sourcecode für das CABS Projekt des ersten Jahrganges an der HTL St. Pölten Abteilung Informatik zur Verfügung gestellt.

Es geht um ein Macro Keyboard mit einem Raspberry Pi Pico und Circuitpython.

Featueres:
  * 8 Taster
  * 1 Encoder mit Taster
  * 11 Neopixel RGB Leds
  * Taster Hotswapable
  * Tastenkappen 3D gedruckt


Die Konfugiration der Befehle erfolgt in der Datei **keyconf.json** nach folgendem Format:

{
 "keyX": [
     ["Aktion", "Parameter"],
     ["Aktion", "Parameter"],
     ...
     ],
}

**keyX**: key1 bis key8 - key0 kann nicht konfiguriert werden. Dieser ist der Taster des Encoders und wird für Mute verwendet.

**Aktion** - einer der folgenden Buchstaben:
  * **P** - Press - Parameter
  * **U** - Up - Parameter
  * **R** - Release - kein Parameter
  * **T** - Text - Parameter 
  * **C** - Consumer-Control - Parameter
  * **D** - Delay - Parameter

**Parameter**:
  * Bei **P** und **U**: Jene Taste, welche gedrückt bzw. wieder losgelassen werden soll. (lib/keycode_win_de.py)
  * Bei **T**: Der Text der "getippt werden soll. \n wird erkannt. 
  * Bei **C**: Die Fernbedienungstaste die gedrückt werden soll. (lib/consumer_control_extended.py)
  * Bei **D**: Wartezeit in Sekunden. Dezimalzahlen erlaubt.

  ## boot.py
  Die Datei boot.py verhindert, dass das USB Laufwerk beim anschließen der Tastatur eingebunden wird. Im Normalfall wird
  man das Laufwerk nicht benötigen.
  Um das Laufwerk dennoch zu sehen um z.B. die keyconf.json zu ändern wird in der boot.py der Taster des Encoders abgefragt.
  Ist dieser beim Einschalten / -stecken gedrückt, wird das Laufwerk eingebunden. Dies funktioniert nur bei einem Hard-Reset.
  Ein Neustart über die REPL Console über den virtuellen COM Port reicht nicht.