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
**Aktion**:
  * **P** Press - Parameter 
  * **U** Up - Parameter
  * **R** Release - kein Parameter
  * **T** Text - Parameter  
  * **D** Delay - Parameter

**Parameter**:
  * Bei **P** und **U** die Taste die gedrückt bzw. wieder losgelassen werden soll
  * Bei **T**: Der Text der "getippt werden soll. \n wird erkannt.
  * Bei **D**: Wartezeit in Sekunden. Dezimalzahlen erlaubt.
    
    
  
