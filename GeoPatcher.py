import sys
import subprocess
import os

# ==============================================================================
# CONSTANTS
# ==============================================================================

VERSION = (0,0,1)

SEARCH_EXT_EXCLUDE = ".bmp .png .zip .7z .rar".split()
ENCODING_JP = 'shift_jis'
ENCODING_EN = 'utf-8'
DEFAULT_SEARCH_KEYS = "・・・。,"
ZEROPADDING = b'\x00' * 100

NEWLINE_CODE = 0x0A 	# Patch newline code
JPFIRSTBYTERANGE = (0x80, 0x9F)

HELP_STR = "\n".join([
"GeoPatcher.py v%s" % str(VERSION),
"A tool for editing text data in \"Variable Geo II: Bout of Cabalistic Goddess\"",
"GitHub: https://github.com/vGeoXIII/GeoPatcher",
"",
"-h \t\t\tDisplay help info",
"-c <string>\t\tConverts and prints given string as byte data for patched game",
"-cc <string>\t\tConverts and prints given string as halfwidth byte data for un-patched game",
"-cb <string>\t\tPrints string as bytes",
"-s file_or_dir <str> <str> <...> \tScan and report instances of str(s) in file or directory.",
"-sb file_or_dir <hex> <hex> <...> \tScan and report instances of hex in file or directory.",
"-r game_file <lcl_file>\tRead quoted text from game_file and generate lcl_file for text editing.",
"\tUses Japanese quotes to locate text.",
"\tSearches for Shift-JIS code patterns to locate text.",
"-t lcl_file \t\tTranslate replacement text in localizer_file using Google Translate.",
"\tUses \"translate-shell\" cli program from https://github.com/soimort/translate-shell",
"\tCaches translated text to \"geodictionary.txt\" in the same directory as the lcl file.",
"-w game_file lcl_file \tWrite to game_file with text edits from lcl_file.",
"\tText that exceeds original bytelength is truncated when writing to game_file",
"-p vg2_hdi \t\tPatches VG2 hdi file to display halfwidth characters.",
])

LOCALTXT_HEADER = """
# Generated translation script file by @GeoXIII
# Parameters are read per line in a looping order:
#     Bytelength Offset1 Offset2 ...
#		- First value is the maximum size of the source text being replaced.
#		- Following values are offsets to write the text line to.
#     ReplacementText
#		- Line breaks are done with "\\n"
#		- Once the text line is read, bytelength and offsets are cleared for next item.
# (Lines starting with hashtag "#" are comments and skipped during parse)
# ======================================================================\n\n
"""

ASCII_ART = """
 @@@@    @%%%##%%%@@%%####%%%%%%#+++###+=--+%%#+==#%#%%%@@%%%@@@%##%%%%%%%%%%%%%%%%%%%%%%%%%@@%%%%%@
 @@@     @%%%%%%  %%#####%%%%#*+++*#%*==---+%%#=-=##**#%@@%%%%@@%#=++++*%%%%%%%%%%%%%%%%%%%%%%@%%%%%
       @@@%##@   @%####%%**%%*--=####+-----+%%#=-=##*=+@%%#%%%%@@#-----=+#%%%%%%%%%%%%%%@@%%%%@%%@%%
       @@%%%%  @@%%####%%###%*--=%%#+=-----+%%#=-=+#%++%%%***%%@@#-------==#%@@%%%%%%%%%@%%%@@%%%@%%
       #####   %%####%@@%%%%*=:-+#%#=------+%%#=--=*%*+=#%@#*#%%%#==------=#%%%%%%%%%%%%%@%%%%%%@%%%
      @%#%%%   %####%%% %%###*-=+%*=-------+#%#=---+%%*-+*%%%+*%%#*=------=#%%%%%%%%%%%%%%%%%%%@@%%%
      @@%%@@   ####%%%% %%*-=+**##+--------=+##=---+#%#===#%%++*#%%+=-----=*#%%%%@@%%%%%%%%%%%%%%%%%
      %%@@   @@%##%@@   %%*--=*%%#+----------++=----=+*#+-=*##+-=*@*+-------*%@@@@@%%%%%%%@@%%%%%%%%
    @@@%     @@%##%@@  @%#+=*#%%%%%*=----------=------+*##+**%%##%%%#*+++=--*@%%%%%%%%%%%%%%%%@@%%%%
@@  @@@@       ##%@    %%%*--=+***#%%*------------=+*#%%%%%%%%%%#*+**==-----+%%%%%%@@@%%%%%%%%@%%%%%
@@@@@@@@       ##%@    %%%*-----==*#%*----------=+#%#%%%%%@@%#+===--=+=-----+#%@@%%%%%%%%%%%%%@%%%%%
%%@@@@@        %%%        **=--:..=+=++-=+==+**###*++#%%%%%%%%%%#*+==--------=*##*+=+++#%%%@@@%%%%%%
#%%%@@@@      @@@@        %#==+=-.:-=*#==**+++=----=****##--=#%@@@@#*+==------====++**+*@@@@@@%%%%%%
####%%@@@@@@@ @@@@        %#+--===--=#%*+-----------=--=++..:*%%%%*####****==--=*+=====+#%@@@%%%%%%%
**###%%%@@@@@@@@@@        %%+---=+++=*%%*------------:::=+..-%%#%*-==++++++=---+#+=----=*%@%%%%%%%%%
****####%%%%%%@@@@@@@@@   %%+---------=*+-------------:..:*#%%%%#+:-=----------=**+--==#@@%%%%%%%%%%
+****###%%%%%%%%%%%@@@@@@@%%+---------+#*---------------==-=+**+==+*+=---------=*=--=+%@@%%%%%%%%%%%
++++***###%%%%%%%%%%%%@@@@@%+-----===+##+-----------===+**++==+*#**+=--------======+*#%%%%%%%%%%%%%%
*++++++**###%%%%%%%%%%%%%%%%#+---+#@%*--------------=++++=------------------=+****#@@@%%%%%%%%%%%%%%
**+++++++**##%%%%%%%%%%%%%%%%*----=+%*--------------------------------------====+#%@@%%%%%%%%%%%%%%%
##**+++++++********#%%%%%%%%%##+----=++==----------------------------------------+*%%%%%%%%%%%%%%%%%
####*+++++++++++++++*#%%%%%%%%%%*-------=###**+=-----------------------=++=------=+%%%%%%%%%%%%%%%%%
%%####**+++++++++++++++**#%%%%%%%%#+----=*%%%#+++*#+----------------==*#==--------+%%%%%%%%%%%%%%%%%
%%%#####*++++++++++++++++##%%%%%%%%%*=----+#%*====**=--------------=+#*+=---====+**###%%%%%%%%%%%%%%
@%%%####***+++++++++++++++*###%%%%%%%#++=--=**+====*%*+--------====++===++++++++**++==+*%%%%%%%%%%%%
@@%%%###+****++++++++++++++++*%%%%%%%%%%#*=--=+**+=*%*+-------=***++**##%##*+==--------+#%%%%%%%%%%%
@@%%%%##++*#*+++++++++++++++++**#%%%%%%%%%%*--=*###*+=------=*#%%%%%##*+=---=*++-------==*#%%%%%%%%%
@@%%%%%#+++*+++++++++++++++++++++**#%%%%%%%%%%##*=------=+##*+=----====------===++++==---=+%%%%%%%%%
                 (Yuka Takeuchi from Variable Geo)
"""[1:-1]

JPCHARMAP = {
	" ": bytes((0x81, 0x40)).decode(ENCODING_JP),
	"!": bytes((0x81, 0x49)).decode(ENCODING_JP),
	"@": bytes((0x81, 0x97)).decode(ENCODING_JP),
	"?": bytes((0x81, 0x48)).decode(ENCODING_JP),
	":": bytes((0x81, 0x46)).decode(ENCODING_JP),
	".": bytes((0x81, 0x44)).decode(ENCODING_JP),
	"·": bytes((0x81, 0x45)).decode(ENCODING_JP),
	"-": bytes((0x81, 0x5b)).decode(ENCODING_JP),
	"#": bytes((0x81, 0x94)).decode(ENCODING_JP),
	"$": bytes((0x81, 0x90)).decode(ENCODING_JP),
	"%": bytes((0x81, 0x93)).decode(ENCODING_JP),
	"&": bytes((0x81, 0x95)).decode(ENCODING_JP),
	"(": bytes((0x81, 0x69)).decode(ENCODING_JP),
	")": bytes((0x81, 0x6A)).decode(ENCODING_JP),
	"'": bytes((0x81, 0x65)).decode(ENCODING_JP),
	",": bytes((0x81, 0x43)).decode(ENCODING_JP),
	"\"": bytes((0x81, 0x67)).decode(ENCODING_JP),
	"...": bytes((0x81, 0x63)).decode(ENCODING_JP),
}
JPCHARMAP.update({c: bytes((0x82, ord(c)-ord('0')+0x4f)).decode(ENCODING_JP) for c in "0123456789"})
JPCHARMAP.update({c: bytes((0x82, ord(c)-ord('A')+0x60)).decode(ENCODING_JP) for c in "qwertyuiopasdfghjklzxcvbnm".upper()})
JPCHARMAP.update({c: bytes((0x82, ord(c)-ord('a')+0x81)).decode(ENCODING_JP) for c in "qwertyuiopasdfghjklzxcvbnm".lower()})
JPCHARUNKNOWN = bytes((0x81, 0xA1)).decode(ENCODING_JP)

if 0:
	JPCHARMAP.update({c: bytes((0x20, ord(c))).decode(ENCODING_JP) for c in "0123456789"})
	JPCHARMAP.update({c: bytes((0x20, ord(c))).decode(ENCODING_JP) for c in "qwertyuiopasdfghjklzxcvbnm".upper()})
	JPCHARMAP.update({c: bytes((0x20, ord(c))).decode(ENCODING_JP) for c in "qwertyuiopasdfghjklzxcvbnm".lower()})

VGCHARMAP = {
	" ": 0x3F,
	"!": 0x40,
	"\"": 0x41,
	"#": 0x42,
	"$": 0x43,
	"%": 0x44,
	"&": 0x45,
	"'": 0x46,
	"(": 0x47,
	")": 0x48,
	"*": 0x49,
	"+": 0x4A,
	",": 0x4B,
	"-": 0x4C,
	".": 0x4D,
	"/": 0x4E,
	"[": 0x7A,
	"\\": 0x7B,
	"]": 0x7C,
	"^": 0x7D,
	"_": 0x7E,
	"`": 0x7F,
	"{": 0x9B,
}



# ======================================================================
# FUNCTIONS
# ======================================================================

HexString = lambda value, digits=8: "".join(["0123456789ABCDEF"[(value >> (i*4)) & 0xF] for i in range(0, digits)])[::-1]
HexRead = lambda hexstring: sum(["0123456789ABCDEF".index(c) * (1<<(i*4)) for i,c in enumerate(hexstring.replace("0x", "").upper()[::-1]) if c in "01234567890ABCDEFG"])

JPBytes = lambda s: s.encode('shift_jis')

# Converts letters to their shift_jis counterparts 
def JPLetters(text, linenum=0):
	unknowns = []
	jptext = ""
	text = text.replace("...", JPCHARMAP["..."])
	for c in text:
		# Charmap
		if c in JPCHARMAP.keys():
			jptext += JPCHARMAP[c]
		else:
			# Japanese characters
			try:
				if tuple(c.encode(ENCODING_JP)) > tuple((0x81, 0x00)):
					jptext += c
				else:
					unknowns.append((c, c.encode(ENCODING_JP)))
					jptext += JPCHARUNKNOWN
			# Unknown
			except:
				unknowns.append((c, ord(c)))
				jptext += JPCHARUNKNOWN
	
	if unknowns:
		print(linenum)
		print("EN:", text)
		print("JP:", jptext)
		print("Unknowns:", str([x for x in list(set(unknowns))]))
	return jptext

# Converts letters to their in-game counterparts
def LettersToVGBytes(text, linenum=0):
	outbytes = []
	n = len(text)
	i = 0
	while i < n:
		c = text[i]
		if c == "\\" and text[i+1] == "n":
			outbytes.append(NEWLINE_CODE)
			i += 1
		elif c in VGCHARMAP.keys():
			outbytes.append(VGCHARMAP[c])
		elif c in '0123456789':
			outbytes.append(ord(c)-ord('0')+0x4F)
		elif c in 'qwertyuiopasdfghjklzxcvbnm'.upper():
			outbytes.append(ord(c)-ord('A')+0x60)
		elif c in 'qwertyuiopasdfghjklzxcvbnm'.lower():
			outbytes.append(ord(c)-ord('a')+0x81)
		else:
			pass
		i += 1
	return bytes(outbytes)

# Cleans duplicate letters in text
def CleanDuplicateChars(text, repeat_max):
    if repeat_max <= 1:
        return text
    
    i = 0
    clast = ""
    n = len(text)
    while i < n:
        if text[i] == clast:
            istart = i-1
            # Stop at first non-repeating character
            while i < n-1 and text[i] == clast:
                i += 1
            repeat_hits = i-istart
            # Limit repeat characters
            if repeat_hits >= repeat_max:
                text = text[:istart] + text[istart+repeat_hits-repeat_max+1:]
                i = istart
                n = len(text)
            clast = ""
        else:
            clast = text[i]
        i += 1
    return text

# Reduces number of duplicate instances of strings in text
def CleanDuplicateStrings(text, min_size, max_size, duplicate_limit=3):
    n = len(text)
    k = ""
    i = 0
    
    # Iterate per character
    while i < n-max_size:
        c = text[i]
        if c.lower() in "qwertyuiopasdfghjklzxcvbnm0123456789":
            for size in range(min_size, max_size):
                pattern = text[i:i+size]
                # Check if instances exist at all
                if text.count(pattern) < duplicate_limit:
                    continue
                # Count consecutive instances
                j = i
                consecutive_hits = 0
                while j < n-size:
                    if text[j:j+size] == pattern:
                        j += size
                        consecutive_hits += 1
                    else:
                        break
                # Number of consecutive hits above limit
                if consecutive_hits > duplicate_limit:
                    print("\"%s\""%pattern, consecutive_hits)
                    
                    # Reduce number of instances to limit
                    text = text[:i] + (pattern*duplicate_limit) + text[j+size:]
                    n = len(text)
        i += 1
    return text

# Returns list of nested files in directory
def ListNestedFiles(rootpath):
	outpaths = []
	if rootpath[-1] not in "/\\":
		rootpath += "/"
	
	def FindDirs(path):
		for fname in os.listdir(path):
			fpath = path+fname
			if os.path.isdir(fpath):
				FindDirs(fpath+"/")
			else:
				outpaths.append(fpath)
	FindDirs(rootpath)
	return outpaths

# ......................................................................
def GeoPatcher_SearchKeys(dir_or_filepath, keys):
	# Converts keys into list if not already
	search_keys = keys
	if isinstance(keys, (list, tuple)):
		search_keys = keys[:]
	elif isinstance(keys, str):
		if "," in keys:
			search_keys = [k.replace(",", "") for k in keys.split(",")]
		elif "|" in keys:
			search_keys = keys.split("|")
		elif " " in keys:
			search_keys = keys.split()
		else:
			search_keys = [keys]
	
	search_keys = [k.strip() for k in search_keys if k.strip()]
	search_keys = [(k, bytes(k.encode(ENCODING_JP))) for k in search_keys]
	print([k[0] for k in search_keys])
	
	exclude_ext = SEARCH_EXT_EXCLUDE[:]
	
	# Find Files
	filelist = []
	if os.path.isdir(dir_or_filepath):
		filelist = ListNestedFiles(dir_or_filepath)
	else:
		filelist = [dir_or_filepath] 
	
	# Parse Files
	hitfiles = []
	for fpath in filelist:
		# Skip excluded extensions
		fext = os.path.splitext(fpath)[1]
		if fext.lower() in exclude_ext:
			continue
		
		# Read file into buffer
		f = open(fpath, 'rb')
		data = bytes(f.read())
		f.close()
		fsize = len(data)
		
		# Parse file
		hits = 0
		keyhits = {ks: [] for ks,kb in search_keys}	# {k: offsets}
		for k, kbytes in search_keys:
			if kbytes in data:
				ksize = len(kbytes)
				for i in range(0, fsize-ksize):
					if data[i:i+ksize] == kbytes:
						keyhits[k].append(i)
						hits += 1
		if hits > 0:
			hitfiles.append((fpath, keyhits))
	
	# Print results
	if len(filelist) > 1:
		print("Files hit:", len(hitfiles))
		hitfiles.sort(key=lambda hitkeyitem: -len(hitkeyitem[1]))
	for fpath, keyhits in hitfiles:
		print(fpath, fpath)
		for k, offsets in keyhits.items():
			if offsets:
				print("   %s:\t"%k, ", ".join(["0x"+HexString(offset, 8) for offset in offsets]))
	print("> Search Complete!")

def GeoPatcher_SearchBytes(path, keys):
	kbytes = bytes([HexRead(x) for x in keys.split()])
	print(kbytes, kbytes[::-1])
	
	exclude_ext = SEARCH_EXT_EXCLUDE[:]
	
	# Find Files
	filelist = []
	if os.path.isdir(dir_or_filepath):
		filelist = ListNestedFiles(dir_or_filepath)
	else:
		filelist = [dir_or_filepath] 
	
	# Parse Files
	hitfiles = []
	for fpath in filelist:
		# Skip excluded extensions
		fext = os.path.splitext(fpath)[1]
		if fext.lower() in exclude_ext:
			continue
		
		# Read file into buffer
		f = open(fpath, 'rb')
		data = bytes(f.read())
		f.close()
		
		# Parse File
		fsize = len(data)
		ksize = len(kbytes)
		k = kbytes
		if k in data: 	# Forward bytes
			hits = 0
			for i in range(0, fsize-ksize):
				if data[i:i+ksize] == k:
					hitfiles.append((fpath, k, i))
					hits += 1
		k = k[::-1]
		if k in data: 	# Reverse bytes
			hits = 0
			for i in range(0, fsize-ksize):
				if data[i:i+ksize] == k:
					hitfiles.append((fpath, k, i))
					hits += 1
	
	# Print results
	if len(filelist) > 1:
		print("Files hit:", len(hitfiles))
		hitfiles.sort(key=lambda hitkeyitem: -len(hitkeyitem[1]))
	for fpath, k, linenum in hitfiles:
		print(fpath, "\t{"+", ".join(["%s: %s" % (str(k), HexString(linenum))])+"}" )
	print("> Search Complete!")

# Parses binary file and outputs a text file for translation
def GeoPatcher_GenerateLocalizerFile(srcpath, outpath="", deep_search=True):
	if not outpath:
		outpath = srcpath + ".geolcl"
	
	# Read src file ............................................
	f = open(srcpath, 'rb')
	data = bytes(f.read())
	f.close()
	
	# Staging ...........................................
	jpstrings = [] # [ (offset, size, original) ]
	
	datalen = len(data)
	d1 = bytes(JPBytes("「"))
	d2 = bytes(JPBytes("」"))
	
	textitems = {} # { (textbytes): [offsets] }
	textorder = [] # [textbytes, textbytes, ...]
	hits = 0
	
	def AddTextItem(textbytes, offset):
		textbytes = bytes(textbytes)
		if textbytes not in textitems:
			textitems[textbytes] = []
			textorder.append(textbytes)
		if offset not in textitems[textbytes]:
			textitems[textbytes].append(offset)
	
	# Parse for strings ..........................................
	searchregions = []
	regionstart = 0
	regionend = 0
	regionsep = 0x1000
	
	# Method 1: Look for quoted Japanese text. Mostly character dialogue
	i = 0
	while i < datalen-16:
		# Skip zeroes
		while data[i] == 0x00 and i < datalen-16:
			i += 1
		
		# Character has first byte of delimiter
		if data[i] == d1[0]:
			if data[i:i+len(d1)] == d1: # Sequence matches delimiter
				offset = i
				# Read up to second delimiter
				while (i < datalen) and (data[i:i+2] != d2):
					i += 1
				i += 2
				# Cull super long byte strings
				if i-offset < 512:
					# Use this to locate regions where strings are
					if deep_search:
						# Start of region
						if regionstart == 0x00:
							regionstart = i
							regionend = i
						# In region
						else:
							# Offset difference is too large: split region
							if i-regionend > regionsep:
								print((HexString(regionstart), HexString(regionend)))
								searchregions.append((regionstart-regionsep, regionend+regionsep))
								regionstart = 0x00
								regionend = 0x00
							# Extend region
							else:
								regionend = i
					# Use this to locate strings
					else:
						if data[i] == 0x6e: # Ensure newline is included
							i += 1
						textbytes = data[offset:i]
						
						# Handle null characters found between quotes
						while 0x00 in textbytes:
							inull = textbytes.index(0x00)
							try:
								text = textbytes[:inull].decode(ENCODING_JP)
								if len(text) > 4:
									AddTextItem(textbytes[:inull], offset)
									offset += inull+1
									textbytes = textbytes[inull+1:]
									hits += 1
							except:
								print("Error parsing Shift-JIS at offset 0x%s:" % HexString(offset, 8), " ".join([HexString(x, 2) for x in textbytes[:inull]]))
								textbytes = []
								break
						# Add to list of text items
						if textbytes:
							text = textbytes.decode(ENCODING_JP)
							if len(text) > 4:
								AddTextItem(textbytes, offset)
								hits += 1
		i += 1
	
	# Method 2: Search for ShiftJIS pattern using fullwidth bytes. Finds almost ALL strings
	if deep_search:
		firstbytesJP = tuple(range(JPFIRSTBYTERANGE[0], JPFIRSTBYTERANGE[1]+1))
		minhits = 2
		i = 0
		istep = 0x100000
		iprogress = 0
		
		for regionstart, regionend in searchregions:
			i = regionstart
			while i < regionend:
				if i//istep > iprogress:
					print("Offset", "0x"+HexString(i))
					iprogress = i//istep
				
				# Skip zeroes
				if data[i] == 0x00:
					while data[i] == 0x00 and i < datalen-16:
						i += 1
				# First byte of JP char
				if data[i] in firstbytesJP:
					# Sequence of JP chars
					if sum([data[i+o*2] in firstbytesJP and data[i+o*2+1] > 0x30 for o in range(0, minhits)]) == minhits:
						offset = i
						validjis = True
						while i < datalen-16:
							if data[i] == 0x6e: # Newline char
								i += 1
							elif data[i] in firstbytesJP: # Starts with 0x80-0xFF
								i += 2
							elif data[i] == 0x00: # Ends with null byte
								break
							else: # Pattern error
								validjis = False
								break
						# Validate JIS
						if not validjis:
							#print("Error byte:", HexString(data[i], 2))
							pass
						else:
							size = i-offset
							if size < 256:
								textbytes = data[offset:i]
								try:
									text = textbytes.decode(ENCODING_JP).strip()
									if not text:
										textbytes = []
								except:
									pass
									textbytes = []
								
								if textbytes:
									hits += 1
									AddTextItem(textbytes, offset)
				i += 1
	
	# Compose localization file ................................
	outtext = "# %s" % os.path.split(srcpath)[1]
	outtext += LOCALTXT_HEADER
	
	textitems = list(textitems.items())
	textitems.sort(key=lambda item: textorder.index(item[0]))
	
	for textbytes, offsets in textitems:
		text = textbytes.decode(ENCODING_JP)
		
		size = len(textbytes)
		#print("%2d" % size, text, ["0x"+HexString(x) for x in offsets])
		
		outtext += "%02d " % size
		for offset in offsets:
			outtext += "0x" + HexString(offset) + " "
		outtext += "\n"
		outtext += text.replace("n", "\\n") + "\n\n"
	
	if hits == 0:
		print("> No hits in file (already translated?)")
		print("> No files were changed")
	else:
		print("Hits:", hits, "| Offsets:", len(textitems))
		f = open(outpath, 'w')
		f.write(outtext)
		f.close()
		
		print("> Localization file written to: \"%s\"" % outpath)

# ......................................................................
def GeoPatcher_DictionaryFile(outpath, translation_map=None, keyorder=None):
	if translation_map:
		translation_map = {k: v for k,v in translation_map.items()}
	else:
		translation_map = {}
	
	if not keyorder:
		keyorder = list(translation_map.keys())
	
	srclines = []
	usedkeys = []
	outblocks = {}	# {original: lines[]}
	
	# Read previous dictionary
	if os.path.exists(outpath):
		f = open(outpath, "r")
		srclines = [x for x in f]
		f.close()
	
	# Update existing lines
	mode = 0
	block = []
	for line in srclines:
		line = line.rstrip()
		if not line or line[0] == "#":
			if block and block[-1] != "":
				if "# MTL" in line or "# Bytelength" in line:
					continue
				block.append(line)
		elif mode == 0: # Original
			original = line
			usedkeys.append(original)
			block.append(line)
			mode = 1
		else:
			translation = translation_map.get(original, line)
			translation_map[original] = translation
			
			# Write comments
			if sum(["# Bytelength:" in x for x in block]) == 0:
				block.insert(block.index(original)+1, "# Bytelength: %2d" % len(original.encode(ENCODING_JP)))
			if 1:
				if sum(["# MTL:" in x for x in block]) == 0:
					block.append("# MTL: %s" % translation)
			
			block.append(line)
			
			outblocks[original] = block
			block = [""]
			mode = 0
	
	# Add new entries
	block = []
	for original,translation in translation_map.items():
		if original not in usedkeys:
			block = [
				original,
				"# Bytelength: %2d" % len(original.encode(ENCODING_JP)),
				"# MTL: %s" % translation,
				translation, 
				""
			]
			outblocks[original] = block
	
	# Sort by order in inputmap
	outblocks = list(outblocks.items())
	outblocks.sort(key=lambda item: keyorder.index(item[0]) if item[0] in keyorder else 0xFFFF)
	
	outtext = "\n".join([line for k,block in outblocks for line in block])
	
	# Write to output
	f = open(outpath, "w")
	f.write(outtext)
	f.close()
	
	return translation_map

def GeoPatcher_TranslateLocalizerFile(localizer_filepath, outpath=""):
	if not outpath:
		outpath = localizer_filepath
	
	# Read localization file
	f = open(localizer_filepath, "r")
	flines = [x for x in f]
	f.close()
	
	# Staging
	outlines = []
	linecount = len(flines)
	progress_percent = 0
	progress_step = 5
	
	dictionary_path = os.path.split(localizer_filepath)[0] + "/geodictionary.txt"
	translation_map = GeoPatcher_DictionaryFile(dictionary_path) # {original: translation}
	translation_order = []
	
	def WritePartofFile(path, currentlines, restoflines):
		f = open(outpath, "w")
		f.write("\n".join(currentlines) + "".join(restoflines))
		f.close()
	
	jplinecount = sum([
		1 for srcline in flines 
		if srcline.rstrip() and srcline[0] != "#" and (sum([ord(c) >= 255 for c in srcline]) >= len(srcline)//2)
	])
	
	totallinecount = len([1 for line in flines if line[0] in "0123456789" and "0x" in line])
	
	print("Dictionary size:", len(translation_map))
	print("Number of lines to translate: %d/%d" % (jplinecount, totallinecount))
	
	# Translation loop ...........................................
	outlineblock = []
	offsetline = ""
	hits = 0
	linehits = 0
	queue_save = False
	mode = 0
	original_comment = False
	print("> Translating lines. Saves will occur periodically. Feel free to cancel operation.")
	for lineindex, srcline in enumerate(flines):
		# Print progress
		if 100*linehits/totallinecount >= progress_percent:
			if queue_save:
				outlines += outlineblock
				outlineblock = []
				WritePartofFile(outpath, outlines, flines[lineindex:])
				GeoPatcher_DictionaryFile(dictionary_path, translation_map, translation_order)
				queue_save = False
				print("%3d%% (%4d/%4d Lines left, Progress saved.)" % (progress_percent, linehits, totallinecount))
			else:
				print("%3d%% (%4d/%4d Lines left)" % (progress_percent, linehits, totallinecount))
			progress_percent += progress_step
		
		srcline = srcline.rstrip()
		original = ""
		
		# Empty Line
		if not srcline:
			outlineblock.append(srcline)
		# Comment line
		elif srcline[0] == "#":
			if "# Src: " in srcline:
				original = srcline[len("# Src: "):].rstrip()
				original_comment = True
			outlineblock.append(srcline)
		# Offset Line
		elif srcline[0] in "0123456789" and "0x" in srcline:
			offsetline = srcline
			outlineblock.append(srcline)
			linehits += 1
			mode = 1
		# JP line
		elif mode == 1:
			if not original:
				original = srcline
			contains_jp = sum([ord(c) >= 255 for c in original]) >= len(original)//2
			hits += 1
			
			if contains_jp:
				# Check if original is already translated (prevents unnecessary calls to translator)
				if original in translation_map.keys():
					#print("Prefetching:", original)
					translation = translation_map[original]
				# Use cli translator program to translate string
				elif contains_jp:
					#print("Translating:", original)
					size = len(original.encode(ENCODING_JP))
					
					translation = subprocess.check_output(["trans", "-b", "ja:", original]).decode('utf-8')
					# Only use first line from cil
					if "\n" in translation:
						translation = translation.split("\n")[0]
					translation = translation.rstrip() # Get rid of newline at the end
					
					# Add newline character from original
					if "\\n" in original:
						translation += "\\n"
					# Cleanup
					translation = CleanDuplicateChars(translation, 4)
					translationlen = len(translation)
					if translationlen > 32 and translationlen > size*2:
						print("! Size Warning at", offsetline)
						print("  Original:   ", original)
						print("  Translation:", translation)
						translation = CleanDuplicateStrings(translation, 3, 10, 4)
			
			# Add to stringmap and output
			translation_map[original] = translation
			if not original_comment:
				outlineblock.append("# Src: " + original)
				outlineblock.append("# MTL: " + translation)
			outlineblock.append(translation)
			
			queue_save = True
			mode = 0
			original = ""
			original_comment = False
		# Data Line
		else:
			outlineblock.append(srcline)
	
	if outlineblock:
		outlines += outlineblock
	
	# Write to file
	f = open(outpath, "w")
	f.write("\n".join(outlines))
	f.close()
	
	print("> Translation written to:", outpath)

# ......................................................................
def GeoPatcher_ApplyLocalizerFile(localizer_filepath, target_filepath=""):
	# Read localization file
	f = open(localizer_filepath, "r", encoding='utf-8')
	flines = [x for x in f]
	f.close()
	
	# Read target file
	f = open(target_filepath, "rb")
	data = bytearray(f.read())
	f.close()
	
	srcsize = len(data)
	
	stringmap = {}
	offset = 0
	size = 0
	text = ""
	
	largelist = []
	
	mode = 0
	for lineindex, line in enumerate(flines):
		line = line.rstrip()
		if not line or line[0] == "#":
			continue
		# Offset line
		elif mode == 0:
			lineinfo = line.split()
			size = int(lineinfo[0])
			offsets = [HexRead(x) for x in lineinfo[1:]]
			mode = 1
		elif mode == 1:
			line = line.replace("\" ", "\"").replace(" \"", "\"")
			
			# Convert to in-game bytes
			textbytes = LettersToVGBytes(line, lineindex+1)
			
			# Result is above size limit
			if len(textbytes) > size:
				largelist.append((lineindex, offsets[0], size, textbytes[:], line))
				textbytes = bytearray([x for x in textbytes if x != VGCHARMAP["\""]])
				
				# Ensure newline is present
				if "\\n" in line[-4:]:
					textbytes[min(size, len(textbytes))-1] = NEWLINE_CODE
			
			# Write to offsets
			for offset in offsets:
				data[offset:offset+size] = (textbytes+ZEROPADDING)[:size]
				data[offset+size] = 0
			mode = 0
	
	for lineindex, offset, size, textbytes, line in largelist[::-1]:
		print("L%4d 0x%s too large (%2d < %2d):" % (lineindex, HexString(offset), size, len(textbytes)), line)
	
	# Write to target file
	if len(data) != srcsize:
		print("> Error: Size of new file does not match old!: %d -> %d" % (srcsize, len(data)))
	else:
		f = open(target_filepath, "wb")
		f.write(data)
		f.close()
		print("> New text written to game: \"%s\"" % target_filepath)

# ......................................................................
def GeoPatcher_PatchVG2(filepath):
	f = open(filepath, 'rb')
	data = bytearray(f.read())
	f.close()
	
	def GeoPatch(data, offsets, code):
		n = len(code)
		for offset in offsets:
			for i,x in enumerate(code):
				if x > 0:
					data[offset+i] = x
	
	# Single Byte to Halfwidth
	GeoPatch(
		data,
		[0x20EF38, 0x21B5F4, 0x236E6C],
		[0xb4,0x85,0x8b,0xf0,0x90,0x90,0x90,0x90,0x90,0x90,0x90,0x90,0x90], 
	)
	
	# Single Byte increment
	GeoPatch(
		data,
		[0x20EFDB, 0x21B697, 0x236F0F],
		[0x83,0xC4,0x08,0x90], 
	)
	
	# Halfwidth Char spacing, 5 bytes after above's noop
	GeoPatch(
		data,
		[0x20EFE3, 0x21B69F, 0x236F17],
		[0x01], 
	)
	
	# Change newline from "n" 6E to "\n" 0A
	GeoPatch(
		data,
		[0x20F015, 0x21B6D1, 0x236F49],
		[0x80, 0x39, NEWLINE_CODE],
	)
	
	print("> Applying halfwidth patch to:", filepath)
	f = open(filepath, 'wb')
	f.write(data)
	f.close()
	
# ==============================================================================
# MAIN
# ==============================================================================

def main():
	argc = len(sys.argv)
	argv = list(sys.argv)
	
	if argc <= 1:
		print(ASCII_ART)
		print("=== GeoPatcher.py v%s by @vGeoXIII ===========" % str(VERSION))
		print(HELP_STR)
	# Help .........................................
	elif argv[1] == "-h":
		print(HELP_STR)
	# Convert .........................................
	elif argv[1] == "-c" or argv[1] == "-cc" or argv[1] == "-cb":
		text = argv[2]
		if argv[1] != "-cb":
			textbytes = LettersToVGBytes(text)
		else:
			textbytes = text.encode(ENCODING_JP)
			
		if argv[1] == "-cc":
			print(" ".join([HexString(0x85, 2) + HexString(x, 2) for x in textbytes]))
		else:
			print(" ".join([HexString(x, 2) for x in textbytes]))
	# Search Text .......................................
	elif argv[1] == "-s":
		fdir = argv[2]
		keys = argv[3]
		if not keys:
			keys = DEFAULT_SEARCH_KEYS
		elif argc > 4:
			keys = argv[3:]
		if fdir and os.path.exists(fdir):
			GeoPatcher_SearchKeys(fdir, keys)
	# Search Bytes .......................................
	elif argv[1] == "-sb":
		fdir = argv[2]
		if fdir and os.path.exists(fdir):
			GeoPatcher_SearchBytes(fdir, argv[3])
	# File Operations ..............................
	else:
		pathhdi = ""
		pathlcl = ""
		pathother = ""
		
		# Find paths in arguments
		for v in argv[1:]:
			vlower = v.lower()
			if ".lcl" in vlower or '.geolcl' in vlower:
				pathlcl = v
			elif vlower[-4:] == ".hdi":
				pathhdi = v
			elif "-" not in v:
				pathother = v
		
		# File operations
		for v in argv[1:]:
			# Read
			if v == "-r":
				if pathhdi:
					GeoPatcher_GenerateLocalizerFile(pathhdi, pathlcl, deep_search=True)
			# Translate
			elif v == "-t":
				if not pathlcl and pathhdi:
					pathlcl = pathhdi+".geolcl"
				if pathlcl:
					GeoPatcher_TranslateLocalizerFile(pathlcl, pathlcl)
			# Write
			elif v == "-w":
				if not pathlcl and pathhdi:
					pathlcl = pathhdi+".geolcl"
				if not pathhdi and pathlcl:
					pathhdi = pathlcl.replace(".geolcl", ".hdi").replace(".lcl", ".hdi")
				if pathlcl == pathhdi:
					print("> Filenames are the same!")
				else:
					print("In: ", pathlcl)
					print("Out:", pathhdi)
					GeoPatcher_ApplyLocalizerFile(pathlcl, pathhdi)
			# VG2 Patch
			elif v == "-p":
				for v in argv[1:]:
					if v and v[-4:] == ".hdi":
						GeoPatcher_PatchVG2(v)
						break

main()

