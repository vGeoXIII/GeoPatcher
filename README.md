# GeoPatcher by [@vGeoXIII](https://github.com/vGeoXIII)
GitHub: https://github.com/vGeoXIII/GeoPatcher  

Project for streamlining the translation process of editing pc98 games.  
Originally designed for editing "Variable Geo II: Bout of Cabalistic Goddess" by GIGA.

A demo translation patch is provided as an ![xDelta file](https://github.com/vGeoXIII/GeoPatcher/blob/main/VG2-EN_MTL.xdelta).  
![Yuka Translation](https://github.com/vGeoXIII/GeoPatcher/blob/main/images/yuka_prefight.BMP)

## GeoPatcher.py
Tool for extracting, editing, and patching text data from VGII. Run in shell/cli with:  
`python GeoPatcher.py <mode> <arg> <arg> <...>`  
Commands: 
```
---File Commands-----------------------------------------------
(File commands can be passed together in one call)
   Ex: $ python GeoPatcher.py game.hdi -r -t -w -p

<hdi_file>
   Extracts text, translates text, applies translation, and patches game in one call.
-r hdi_file <lcl_file>
   Read and extract JP text from hdi file and create a .geolcl text file for editing.
-t lcl_file
   Translate replacement text using translate-shell cli program
   Translate shell can be found here: https://github.com/soimort/translate-shell
-w game_file lcl_file
   Write to game_file with text edits from lcl_file
-p vg2_hdi
   Patches VGII hdi file to display halfwidth characters

---Debugging Commands--------------------------------------------
-h
   Displays help info
-c <str>
   Converts and prints given string as byte data for patched game
-cc <str>
   Converts and prints given string as halfwidth byte data for un-patched game
-cb <str>
   Prints given string as bytes
-p_<cheat>
   -p_p1zero : Start player 1 with 0 health
   -p_p2zero : Start player 2 with 0 health
   -p_thintext : Displays text at single pixel width
```

## Resources + References
- [np2debug](https://github.com/nmlgc/np2debug):
    - Software used to play and debug pc98 games. Originally modified to debug the Touhou series of pc98 games.
- [translate-shell](https://github.com/soimort/translate-shell):
    - A command line tool for translating text. GeoPatcher.py makes calls to this for translations.
- ["How to translate pc98 games (.hdi files)"](https://youtu.be/rWMU0fcJZHE?si=hgzjCP3YQxxYR6ku) by @bunnelbi
    - Describes a method of locating and replacing Japanese text via hex editors.
- ["Modifying text display ASM in Rusty"](https://46okumen.com/2019/03/05/modifying-text-display-asm-in-rusty-folkulore-part-4/) on 46okumen.com
    - Details process of editing assembly code to correctly display latin characters in the game Rusty.
- ["Complete Character List for Shift_JIS"](https://www.fileformat.info/info/charset/Shift_JIS/list.htm)
    - Table of Japanese characters for the encoding format used in pc98 games.

I have a write-up on the development of GeoPatcher for VGII on this ![Wiki page](https://github.com/vGeoXIII/GeoPatcher/blob/main/VG2-EN_MTL.xdelta).

---


