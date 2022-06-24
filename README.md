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
```json
{
 "keyX": [
     ["Aktion", "Parameter"],
     ["Aktion", "Parameter"],
     ...
     ],
  "keyY": ...,
  "keyX+keyZ": ...,
  "color_change_key": "key8",
  "std_colormode": "single",
  "rage_quit_keys": 5,
  "startup_leds": [1, 0, 2, 3, 4, 7, 6, 5, 10, 9, 8]
}
```


**keyX,keyY,keyZ**: key1 bis key8 - Kann mit einem + für Tastenkombinationen aneinander gehängt werden.
**Hinweis**: Damit eine Tastenkombination (oder irgendeine Taste) aktiviert wird *müssen* alle und *dürfen* nur die angegeben Tasten gedrückt werden.

**Aktion** - einer der folgenden Buchstaben:
  * **P** - Press - Parameter
  * **U** - Up - Parameter
  * **R** - Release - kein Parameter
  * **T** - Text - Parameter 
  * **C** - Consumer-Control - Parameter
  * **D** - Delay - Parameter
  * **F** - zusätzliche Funktion ausführen - Parameter

**Parameter**:
  * Bei **P** und **U**: Jene Taste, welche gedrückt bzw. wieder losgelassen werden soll. (lib/keycode_win_de.py)
  * Bei **T**: Der Text der "getippt werden soll. \n wird erkannt. 
  * Bei **C**: Die Fernbedienungstaste die gedrückt werden soll. (lib/consumer_control_extended.py)
  * Bei **D**: Wartezeit in Sekunden. Dezimalzahlen erlaubt.
  * Bei **F**: Name der zusätzlichen Funktion die ausgeführt werden soll. Schon enthalten sind die Funktionen "colormodechange", welche den Farbmodus wechselt, "ledtoggle", welche die LEDs an- oder ausschaltet und "init_catch", welche das kleine Spiel startet. Die Funktionen bitte in die Datei code.py ab Zeile 55 schreiben.

#### Zusatzeigenschaften:

  * **color_change_key**: Die Taste, die gedrückt werden muss, damit aus dem Lautstärkeregler der Farbregler wird. Standardmäßig die Taste rechts unten

  * **std_colormode**: Der Standard Farbmodus. Mögliche Werte sind "wave", "single" und "wheel". Standardmäßig "wave"

  * **rage_quit_keys**: Wenn die Anzahl der gedrückten Tasten gleich oder höher als ist, wird das aktuelle Fenster geschlossen. Standardmäßig deaktiviert. Wenn das passiert, werden alle folgenden Aktionen nicht ausgeführt.

  * **startup_leds**: Die Reihenfolge der LEDs beim Einschalten als Liste. Standardmäßig horizontal in Schlangenlinien von rechts oben nach links unten.

  * **game_difficulty**: Das Delay zwischen den Bewegungen des Punktes im catch-game. Standardmäßig 8.

**Hinweis**: Die oben genannten zusätzlichen Eigenschaften sind alle optional und haben Standardwerte, die verwendet werden, wenn die Eigenschaft nicht angegeben ist.

  ## boot.py
  Die Datei boot.py verhindert, dass das USB Laufwerk beim anschließen der Tastatur eingebunden wird. Im Normalfall wird
  man das Laufwerk nicht benötigen.
  Um das Laufwerk dennoch zu sehen um z.B. die keyconf.json zu ändern wird in der boot.py der Taster des Encoders abgefragt.
  Ist dieser beim Einschalten / -stecken gedrückt, wird das Laufwerk eingebunden. Dies funktioniert nur bei einem Hard-Reset.
  Ein Neustart über die REPL Console über den virtuellen COM Port reicht nicht.

  ## Das catch-game
  Kleines eingebautes Spiel, wenn einem langweilig ist. Standardmäßig ist es mit der Tastenkombination links-oben + mitte + rechts-unten erreichbar. Das Ziel ist es, den kleinen, sich bewegenden Punkt zu fangen, indem man im richtigen Moment die Leuchtende Taste drückt. Die drei LEDs links zeigen an wie viele Leben man noch hat (am Anfang 3). Jedes mal wenn mann daneben drückt, verliert man ein Leben. Wenn man alle Leben verloren hat, ist das Spiel aus. Außerdem kann man das Spiel zu jedem Zeipunkt, an dem keine Animation spielt mit dem Mute-Knopf beenden.

Hinweis: Während das Spiel läuft, funktioniert nichts anderes auf der Tastatur