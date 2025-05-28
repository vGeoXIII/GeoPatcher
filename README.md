# GeoPatcher by [@vGeoXIII](https://github.com/vGeoXIII)
GitHub: https://github.com/vGeoXIII/GeoPatcher  

Project for streamlining the translation process of editing pc98 games.  
Originally designed for editing "Variable Geo II: Bout of Cabalistic Goddess" by GIGA.

![Example Translation](https://github.com/vGeoXIII/GeoPatcher/blob/main/images/yuka_prefight.BMP)

## GeoPatcher.py
Tool for extracting, editing, and patching text data from VGII. Run in shell/cli with:  
`python GeoPatcher.py <mode> <arg> <arg> <...>`  
Commands:  
- `-h` : Prints commands and info about the program.
- `-c string` : Converts and prints given string as byte data for patched game. Used for live debugging.
   - Ex: `python GeoPatcher.py -c "Hello Geo!"` prints `67 85 8C 8C 8F 3F 66 85 8F 40`
- `-d target_file <translation_file>` : Generates translation_file with offsets and strings found in target_file.
   - translation_file is read per line as offset (in hex), size, text; repeating until end of file.
   - Comment lines start with \#
   - See example at [Translation File Example](https://github.com/vGeoXIII/GeoPatcher/blob/main/sample.geolcl)


## Resources
- [np2debug](https://github.com/nmlgc/np2debug):
    - Software used to test and debug pc98 games. Originally modified to debug the Touhou series of pc98 games.
- ["How to translate pc98 games (.hdi files)"](https://youtu.be/rWMU0fcJZHE?si=hgzjCP3YQxxYR6ku) by @bunnelbi
    - Describes a method of locating and replacing Japanese text via hex editors.
- ["Modifying text display ASM in Rusty"](https://46okumen.com/2019/03/05/modifying-text-display-asm-in-rusty-folkulore-part-4/) on 46okumen.com
    - Details process of editing assembly code to correctly display latin characters in the game Rusty.

---


