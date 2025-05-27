import sys
import subprocess
import os

# ==============================================================================
# CONSTANTS
# ==============================================================================

VERSION = (0,0,1)
HELP_STR = "\n".join([
"GeoLocalizer.py v%s" % str(VERSION),
"-h \t\t\tDisplay help info",
"-c \"string\"\t\tConverts and prints given string as byte data for patched game",
"-cc \"string\"\t\tConverts and prints given string as halfwidth byte data for un-patched game",
"-d target_file <localizer_file> \t\tScan and generate .geolocalizer file for given file.",
"-t localizer_file \tTranslate items in localizer_file using Google Translate.",
"-a target_file localizer_file \tUpdate target_file with localizer_file edits.",
"-s  dir <key_string> <key_string> <...> \tScan and report instances of key_string(s) in dir.",
"-p vg2_hdi \tPatches VG2 file to display halfwidth characters.",
])

LOCALTXT_HEADER = """
# Generated translation script file by @GeoXIII
# File format:
#     Offset - Hexadecimal offset of source string in target file:
#     Size - Maximum size (in bytes) of source string in target file (DO NOT EXCEED!) :
#     Text - Text to place at the offset. Number of bytes must remain below source size.:
# (Lines starting with hashtag "#" are comments and skipped during parse)
# ======================================================================\n\n
"""

SEARCH_EXT_EXCLUDE = ".bmp .png .zip .7z .rar".split()
ENCODING_JP = 'shift_jis'
ENCODING_EN = 'utf-8'
DEFAULT_SEARCH_KEYS = "・・・。,"
ZEROPADDING = b'\x00' * 100

NEWLINE_CODE = 0x0D 	# Patch newline code

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
			outbytes.append(0xA)
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
# ......................................................................
def GeoLocalizer_SearchKeys(path, keys):
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
	
	# Folder loop
	exclude_ext = SEARCH_EXT_EXCLUDE[:]
	hitfiles = []
	def GSearch(path):
		for fname in os.listdir(path):
			fpath = path+fname
			# Directory
			if os.path.isdir(fpath):
				GSearch(fpath+"/")
			# File
			else:
				# Skip excluded extensions
				fext = os.path.splitext(fname)[1]
				if fext.lower() in exclude_ext:
					continue
				# Read file into buffer
				f = open(fpath, 'rb')
				data = bytes(f.read())
				f.close()
				
				fsize = len(data)
				hitmap = {}
				hitnet = 0
				for kstring, kbytes in search_keys:
					if kbytes in data:
						hits = 0
						ksize = len(kbytes)
						for i in range(0, fsize-ksize):
							if data[i:i+ksize] == kbytes:
								hits += 1
						if hits:
							hitmap[kstring] = hits
							hitnet += hits
				if hitmap and hitnet > 1:
					hitfiles.append((fpath, hitmap))
	GSearch(os.path.split(path+"/")[0]+"/")
	
	# Print results
	print("Files hit:", len(hitfiles))
	hitfiles.sort(key=lambda hitkeyitem: -len(hitkeyitem[1]))
	for fpath, hitmap in hitfiles:
		print(fpath, "\t{"+", ".join(["\"%s\": %d" % (k,hits) for k,hits in hitmap.items()])+"}" )
	print("> Search Complete!")

def GeoLocalizer_SearchBytes(path, keys):
	kbytes = bytes([HexRead(x) for x in keys.split()])
	print(kbytes, kbytes[::-1])
	
	# Folder loop
	exclude_ext = SEARCH_EXT_EXCLUDE[:]
	hitfiles = []
	def GSearch(path):
		for fname in os.listdir(path):
			fpath = path+fname
			# Directory
			if os.path.isdir(fpath):
				GSearch(fpath+"/")
			# File
			else:
				# Skip excluded extensions
				fext = os.path.splitext(fname)[1]
				if fext.lower() in exclude_ext:
					continue
				# Read file into buffer
				f = open(fpath, 'rb')
				data = bytes(f.read())
				f.close()
				
				fsize = len(data)
				ksize = len(kbytes)
				k = kbytes
				if k in data:
					hits = 0
					for i in range(0, fsize-ksize):
						if data[i:i+ksize] == k:
							hitfiles.append((fpath, k, i))
							hits += 1
				k = k[::-1]
				if k in data:
					hits = 0
					for i in range(0, fsize-ksize):
						if data[i:i+ksize] == k:
							hitfiles.append((fpath, k, i))
							hits += 1
					
	GSearch(os.path.split(path+"/")[0]+"/")
	
	# Print results
	print("Files hit:", len(hitfiles))
	for fpath, k, linenum in hitfiles:
		print(fpath, "\t{"+", ".join(["%s: %s" % (str(k), HexString(linenum))])+"}" )
	print("> Search Complete!")

# .....................................................................
def GeoLocalizer_GenerateLocalizerFile(srcpath, outpath=""):
	if not outpath:
		outpath = srcpath + ".geolcl"
	
	# Read src file ............................................
	f = open(srcpath, 'rb')
	data = bytes(f.read())
	f.close()
	
	# Parse for strings ..........................................
	jpstrings = [] # [ (offset, size, original) ]
	
	datalen = len(data)
	d1 = bytes(JPBytes("「"))
	d2 = bytes(JPBytes("」"))
	
	i = 0
	hits = 0
	while i < datalen-16:
		if data[i] == 0x81:
			if data[i:i+2] == d1:
				offset = i
				while (i < datalen) and (data[i:i+2] != d2):
					i += 1
				i += 2
				if i-offset < 512:
					if data[i] == 0x6e:
						i += 1
					textbytes = data[offset:i]
					# Handle null characters found between quotes
					while 0 in textbytes:
						inull = textbytes.index(0)
						try:
							text = textbytes[:inull].decode(ENCODING_JP)
							if len(text) > 4:
								jpstrings.append( (offset, inull, text) )
								offset += inull+1
								textbytes = textbytes[inull+1:]
								hits += 1
						except:
							print("Error parsing Shift-JIS at offset 0x%s:" % HexString(offset, 8), " ".join([HexString(x, 2) for x in textbytes[:inull]]))
							textbytes = []
							break
								
					if textbytes:
						text = textbytes.decode(ENCODING_JP)
						if len(text) > 4:
							jpstrings.append( (offset, i-offset, text) )
							hits += 1
		i += 1
	print("Hits:", hits)
	
	# Compose localization file ................................
	outtext = "# %s" % os.path.split(srcpath)[1]
	outtext += LOCALTXT_HEADER
	for offset, size, text in jpstrings:
		outtext += "0x" + HexString(offset) + "\n"
		outtext += "%d" % size + "\n"
		outtext += text.replace("n", "\\n") + "\n\n"
	
	f = open(outpath, 'w')
	f.write(outtext)
	f.close()
	
	print("> Localization file written to: \"%s\"" % outpath)


# ......................................................................
def GeoLocalizer_TranslateLocalizerFile(localizer_filepath, outpath=""):
	if not outpath:
		outpath = localizer_filepath
	
	# Read localization file
	f = open(localizer_filepath, "r")
	flines = [x for x in f]
	f.close()
	
	outlines = []
	linecount = len(flines)
	progress_percent = 0
	progress_step = 5
	
	stringmap = {}
	
	def WritePartofFile(path, currentlines, restoflines):
		f = open(outpath, "w")
		f.write("\n".join(currentlines) + "".join(restoflines))
		f.close()
	
	lastempty = 0
	for lineindex, srcline in enumerate(flines):
		# Print progress
		if 100*lineindex/linecount >= progress_percent:
			print("%3d%% (%d/%d Lines)" % (progress_percent, lineindex, linecount))
			progress_percent += progress_step
			WritePartofFile(outpath, outlines, flines[lineindex:])
		
		srcline = srcline.strip()
		
		# Comment line
		if not srcline or srcline[0] == "#":
			if srcline != "# Original:":
				outlines.append(srcline)
		# JP line
		elif sum([ord(c) >= 255 for c in srcline]) >= len(srcline)//2:
			original = srcline.strip()
			
			# Check if original is used (prevents unnecessary calls to translator)
			if original in stringmap.keys():
				translated = stringmap[original]
			# Use cli translator program to translate string
			else:
				translated = subprocess.check_output(["trans", "-b", "ja:", original]).decode('utf-8')[:-1]
				if "\\n" in original:
					translated += "\\n"
			
			# Add to stringmap and output
			stringmap[original] = translated
			outlines.append("# Original: " + original)
			outlines.append("# Machine Translation: " + translated)
			outlines.append(translated)
		# Data Line
		else:
			outlines.append(srcline)
	
	# Write to file
	f = open(outpath, "w")
	f.write("\n".join(outlines))
	f.close()
	
	print("> Translation Complete!")

# ......................................................................
def GeoLocalizer_ApplyLocalizerFile(localizer_filepath, target_filepath=""):
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
	
	for lineindex, line in enumerate(flines):
		line = line.strip()
		if not line or line[0] == "#":
			continue
		elif line[:2] == "0x":
			offset = HexRead(line)
		elif line.isdigit():
			size = int(line)
		else:
			line = line.replace("\" ", "\"").replace(" \"", "")
			#textbytes = JPLetters(line, lineindex+1).encode(ENCODING_JP)
			#textbytes = bytes([b for c in line for b in ((ord(c)-32) & 0xFF, 18)])
			#textbytes = line.encode(ENCODING_EN)
			#textbytes = "".encode(ENCODING_EN)
			textbytes = LettersToVGBytes(line, lineindex+1)
			#textbytes = b''.join([x for i in range(0x99, 0xFF) for x in (LettersToVGBytes(HexString(i,2)), bytes([i]))])
			
			# Size limit
			if len(textbytes) > size:
				largelist.append((lineindex, offset, size, textbytes, line))
				textbytes = bytes([x for x in textbytes if x != VGCHARMAP["\""]])
				# Ensure newline is present
				if "\n" in line[-4:]:
					textbytes[size-2] = 0xA
			
			data[offset:offset+size] = (textbytes+ZEROPADDING)[:size]
			data[offset+size] = 0
	
	for lineindex, offset, size, textbytes, line in largelist[::-1]:
		print("L%4d 0x%s too large (%2d < %2d):" % (lineindex, HexString(offset), size, len(textbytes)), line)
	
	# Write to target file
	if len(data) != srcsize:
		print("> Error: Size of new file does not match old!: %d -> %d" % (srcsize, len(data)))
	else:
		f = open(target_filepath, "wb")
		f.write(data)
		f.close()
		print("> Localization written to: \"%s\"" % target_filepath)

def GeoLocalizer_PatchVG2(filepath):
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
		[0x80, 0x39, 0x0A], 
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
	argv = list(sys.argv) + [None, None, None, None]
	
	path1 = ""
	path2 = ""
	
	if argc <= 1:
		print(ASCII_ART)
		print("=== GeoLocalizer.py v%s by @GeoXIII ===========" % str(VERSION))
		print(HELP_STR)
	# Help .........................................
	elif argv[1] == "-h":
		print(HELP_STR)
	# Convert .........................................
	elif argv[1] == "-c" or argv[1] == "-cc":
		text = argv[2]
		textbytes = LettersToVGBytes(text)
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
			GeoLocalizer_SearchKeys(fdir, keys)
	# Search Bytes .......................................
	elif argv[1] == "-sb":
		fdir = argv[2]
		if fdir and os.path.exists(fdir):
			GeoLocalizer_SearchBytes(fdir, argv[3])
	# Disassemble ..................................
	elif argv[1] == "-d":
		fpath = argv[2]
		outpath = argv[3]
		GeoLocalizer_GenerateLocalizerFile(fpath, outpath)
	# Translate ..................................
	elif argv[1] == "-t":
		fpath = argv[2]
		outpath = argv[3]
		if '.geolcl' not in fpath:
			if os.path.exists(fpath+".geolcl"):
				fpath += ".geolcl"
		GeoLocalizer_TranslateLocalizerFile(fpath, outpath)
	# Assemble ..................................
	elif argv[1] == "-a":
		lclpath = argv[2]
		outpath = argv[3] if argv[3] and argv[3][0] != "-" else None
		if not outpath:
			if 'lcl' in lclpath:
				outpath = lclpath.replace(".geolcl", "")
			else:
				outpath = lclpath
				lclpath = lclpath + ".geolcl"
		elif 'lcl' in outpath and 'lcl' not in lclpath:
			tmp = outpath
			outpath = lclpath
			lclpath = tmp
		if lclpath == outpath:
			print("> Error: both files are the same")
		else:
			print("In: ", lclpath)
			print("Out:", outpath)
			GeoLocalizer_ApplyLocalizerFile(lclpath, outpath)
	else:
		print("Unknown input (%d Args)" % argc)
	
	# Patch ........................................
	if "-p" in argv:
		for v in argv[1:]:
			if v and v[-4:] == ".hdi":
				GeoLocalizer_PatchVG2(v)
				break
	
	
main()

