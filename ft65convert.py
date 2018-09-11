#!/usr/bin/python3

# ft65convert - Converts between binary code plug and CSV format for Yaesu FT-65
# Copyright (C) 2018 Cody Nybo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import argparse, os, sys, csv, struct

channels = []
banks = [[],[],[],[],[],[],[],[],[],[]]
verbose = False

# field text mapping
fields = {
	"skip":		["Skip", "Scan"],
	"txPower":	["Low", "Mid", "High"],
	"ctcss":	["Off","67.0","69.3","71.9","74.4","77.0","79.7","82.5","85.4","88.5","91.5","94.8","97.4",
				 "100.0","103.5","107.2","110.9","114.8","118.8","123.0","127.3","131.8","136.5","141.3",
				 "146.2","151.4","156.7","159.8","162.2","165.5","167.9","171.3","173.8","177.3","179.9",
				 "183.5","186.2","189.9","192.8","196.6","199.5","203.5","206.5","210.7","218.1","225.7",
				 "229.1","233.6","241.8","250.3","254.1"],
	"dcs":		["Off","023","025","026","031","032","036","043","047","051","053","054","065","071","072",
				 "073","074","114","115","116","122","125","131","132","134","143","145","152","155","156",
				 "162","165","172","174","205","212","223","225","226","243","244","245","246","251","252",
				 "255","261","263","265","266","271","274","306","311","315","325","331","332","343","346",
				 "351","356","364","365","371","411","412","413","423","431","432","445","446","452","454",
				 "455","462","464","465","466","503","506","516","523","526","532","546","565","606","612",
				 "624","627","631","632","654","662","664","703","712","723","731","732","734","743","754"],
	"autoOfs":	["Off", "On"],
	"ofsDir":	["+","-","Simplex"],
	"narrow":	["Wide","Narrow"],
	"step":		["Auto", "5K", "6.25K", "10K", "12.5K", "15K", "20K", "25K", "50K", "100K"],
	"sqlType":	["Off", "R-Tone", "T-Tone", "TSQL", "REV TN", "DCS", "PAGER"],
	"ch":		['"L1"','"U1"','"L2"','"U2"','"L3"','"U3"','"L4"','"U4"','"L5"','"U5"','"L6"','"U6"','"L7"',
				 '"U7"','"L8"','"U8"','"L9"','"U9"','"L10"','"U10"','"VFO-A-U"','"VFO-A-V"','"VFO-B-FM"',
				 '"VFO-B-V"','"VFO-B-U"','"H-FM"','"H-V"','"H-U"','"P1"','"P2"','"P3"','"P4"']}

# default header data for ft-65
defaultHeader = bytes([
	0x48, 0x2d, 0x34, 0x32, 0x30, 0x20, 0x20, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x00, 0x00, 0x02, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x03, 0x00, 0x04, 0x00,
	0x2e, 0x00, 0x04, 0x00, 0x2e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x20, 0x20, 0x20, 0x20, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d,
	0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d,
	0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d,
	0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d,
	0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d,
	0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d,
	0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d,
	0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d,
	0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x2d, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
])

def main():
	# parse arguments
	parser = argparse.ArgumentParser(
	prog="ft65convert",
	formatter_class=argparse.RawDescriptionHelpFormatter,
	description="""FT-65 codeplug to CSV converter
This program converts between the binary data format for the Yaesu FT-65
software and a CSV file to allow easy editing in a spreadsheet before
converting it back to binary and uploading it to your radio.

Download the configuration from your radio and save it to a .dat file
with the Yaesu software before converting your CSV file back to binary.
It contains the settings for your radio which is required to convert
the CSV data back to binary. 
	""",
	epilog="""examples:
ft65convert --csv input.dat output.csv  # convert input.dat to output.csv
ft65convert --bin output.dat input.csv  # convert input.csv to output.dat
ft65convert --config input.dat              # print radio configuration
ft65convert input.dat                       # print channels

This program is experimental!
Backup your files before using ft65convert on them.
	"""
	)	
	parser.add_argument("datFile",                        help="Binary data file from FT-65 Memory Programmer")
	parser.add_argument("csvFile", nargs="?", default="", help="CSV file (required for --bin)")
	parser.add_argument("-v", '--version', version='%(prog)s 0.1.0 (Alpha)',         action='version')
	parser.add_argument("-V", "--verbose", help="Prints warnings during conversion", action="store_true")
	parser.add_argument("-c", "--csv",     help="Convert binary data to CSV file",   action="store_true")
	parser.add_argument("-b", "--bin",     help="Convert CSV file to binary data",   action="store_true")
	parser.add_argument("-d", "--default", help="Use default radio settings",        action="store_true")
	parser.add_argument("-C", "--config",  help="Prints configuration info",         action="store_true")
	args = parser.parse_args()

	if (args.verbose):
		verbose = True
	# convert csv to binary	
	elif (args.bin):
		# make sure files exists
		if (not os.path.exists(args.datFile) and not args.default):
			sys.stderr.write("File does not exist: " + args.datFile + "\n")
			sys.exit(1)
		elif (args.csvFile == ""):
			sys.stderr.write("A CSV file must be provided\n")
			sys.exit(1)
		elif (not os.path.exists(args.csvFile)):
			sys.stderr.write("File does not exist: " + args.csvFile + "\n")
			sys.exit(1)
		
		print("Converting {} to {}".format(args.csvFile, args.datFile))
		
		# convert csv file to .dat
		readCsvFile(args.csvFile)
		writeDatFile(args.datFile, args.default)
	# convert binary to csv
	elif (args.csv):
		# make sure file exists
		if (not os.path.exists(args.datFile)):
			sys.stderr.write("File does not exist: " + args.datFile + "\n")
			sys.exit(1)
			
		if (args.csvFile == ""): args.csvFile = os.path.splitext(args.datFile)[0] + ".csv"
		print("Converting {} to {}".format(args.datFile, args.csvFile)) 
		
		# convert .dat to csv
		readDatFile(args.datFile)
		writeCSVFile(args.csvFile)
	# print configuration info
	elif (args.config):
		# make sure file exists
		if (not os.path.exists(args.datFile)):
			sys.stderr.write("File does not exist: " + args.datFile + "\n")
			sys.exit(1)
		
		printConfig(args.datFile)
	# print channels
	else:
		# make sure file exists
		if (not os.path.exists(args.datFile)):
			sys.stderr.write("File does not exist: " + args.datFile + "\n")
			sys.exit(1)
		
		printChannels(args.datFile)

# read the header from the .dat file
def getHeader(f):
	# Read the radio configuration from the source file.
	with open(f, "rb") as f:
		f.seek(0)
		header = f.read(0x128)
		model = header[0:5].decode("ascii")
		
		if (len(header) != 0x128 or (model != "H-420" and model != "FT-25")):
			sys.stderr.write("Error: unable to get header. Wrong file format?\n")
			sys.exit(1)
		else:
			return header

# convert banks array to string for the specified channel
def getBanks(ch):
	foundBank = False
	results = ""
	
	if (ch <= 220):										# loop through channels
		for b in range(0,10):							# loop through banks
			if (ch in banks[b]):						# check if channel is in the current bank
				if (foundBank):
					results += ", {:g}".format(b+1)		# add additional bank to string with comma seperator
				else:
					results = "{:g}".format(b+1)		# add first bank to string
					foundBank = True
	
	return results

# read the .dat file and save in the channels array
def readDatFile(f):
	numCh = 0	
	
	if (verbose): print("Reading: " + f)
	
	# open the data file
	with open(f, "rb") as f:
		# seek to beginning of bank 1
		f.seek(0x12A)
		
		# loop through banks
		for b in range(0,10):
			# loop throgh channels in each bank
			for i in range(0,220):
				# read channel number
				chNum = ord(f.read(2)[0:1])
				# add channel to array if it's not empty
				if (chNum > 0): banks[b].append(chNum)
		
		# seek to beginning of channel data
		f.seek(0x125A)

		while (True):
			# read channel data
			line = bytes(f.read(0x40))
			# count number of channels
			numCh += 1
			# check for end of file
			if (len(line) == 64 and numCh <=234):
				# unpack the channel data
				ch = struct.unpack("<B3x?xddBxBxBxBxBx?xBx?xBxBx8s14x", line)
				# add channel to array
				channels.append(ch)
			
			# stop from running if file is too large
			elif (numCh > 234):
				sys.stderr.write("Error: too many channels found. Wrong file format?\n")
				sys.exit(1)
			else:
				# reached end of file
				break
		
		# sort array by channel number
		channels.sort(key=lambda t: t[0])

# convert the channels array to CSV and write to file
def writeCSVFile(f):
	# CSV header text
	header = '"CH","RX Freq","Offset","Auto Offset","Offset Dir","RX CTCSS","TX CTCSS","RX DCS","TX DCS","Name","TX Power","Scan","Width","Step","SQL Type","Banks"\n'
	# CSV row format
	fmt = '{:s},{:g},{:g},"{:s}","{:s}","{:s}","{:s}","{:s}","{:s}","{:s}","{:s}","{:s}","{:s}","{:s}","{:s}","{:s}"\n'

	if (verbose): print("Writing: " + f)
	
	# open CSV file for writing
	with open(f, "w") as f:
		# write the header text
		f.write(header)
		# loop through channels
		for ch in channels:
			# get channel number or name for special channels
			if (ch[0] <= 200): num = str(ch[0])
			else:              num = fields["ch"][ch[0]-201]
			
			# format the channel data	
			line = fmt.format(
				num,							# Channel Number
				ch[2],							# RX Freq
				ch[3],							# Offset
				fields["autoOfs"][ch[9]],		# Auto Offset
				fields["ofsDir"][ch[10]],		# Offset Direction
				fields["ctcss"][ch[6]],			# RX CTCSS
				fields["ctcss"][ch[5]],			# TX CTCSS
				fields["dcs"][ch[8]],			# RX DCS
				fields["dcs"][ch[7]],			# TX DCS
				ch[14].decode("ascii"),			# CH Name
				fields["txPower"][ch[4]],		# Transmit Power
				fields["skip"][ch[1]],			# Scan / Skip
				fields["narrow"][ch[11]],		# Wide / Narrow
				fields["step"][ch[12]],			# CH Step
				fields["sqlType"][ch[13]],		# Squelch Type
				getBanks(ch[0]))				# Banks
			
			# write channel data to CSV file
			f.write(line)

# read and parse the CSV file and convert to binary
def readCsvFile(f):
	# field text mapping for csv parsing
	fields = {
		"skip":		["skip", "scan"],
		"txPower":	["low", "mid", "high"],
		"ctcss":	[ 67.0, 69.3, 71.9, 74.4, 77.0, 79.7, 82.5, 85.4, 88.5, 91.5, 94.8,
					  97.4,100.0,103.5,107.2,110.9,114.8,118.8,123.0,127.3,131.8,136.5,
					 141.3,146.2,151.4,156.7,159.8,162.2,165.5,167.9,171.3,173.8,177.3,
					 179.9,183.5,186.2,189.9,192.8,196.6,199.5,203.5,206.5,210.7,218.1,
					 225.7,229.1,233.6,241.8,250.3,254.1],

		"dcs":		[ 23, 25, 26, 31, 32, 36, 43, 47, 51, 53, 54, 65, 71, 72, 73,
					  74,114,115,116,122,125,131,132,134,143,145,152,155,156,162,
					 165,172,174,205,212,223,225,226,243,244,245,246,251,252,255,
					 261,263,265,266,271,274,306,311,315,325,331,332,343,346,351,
					 356,364,365,371,411,412,413,423,431,432,445,446,452,454,455,
					 462,464,465,466,503,506,516,523,526,532,546,565,606,612,624,
					 627,631,632,654,662,664,703,712,723,731,732,734,743,754],
		"autoOfs":	["off", "on"],
		"ofsDir":	["+","-","simplex"],
		"narrow":	["wide","narrow"],
		"step":		["auto", "5k", "6.25k", "10k", "12.5k", "15k", "20k", "25k", "50k", "100k"],
		"sqlType":	["off", "r-tone", "t-tone", "tsql", "rev tn", "dcs", "pager"],
		"ch":		["l1","u1","l2","u2","l3","u3","l4","u4","l5","u5","l6","u6","l7",
					 "u7","l8","u8","l9","u9","l10","u10","vfo-a-u","vfo-a-v","vfo-b-fm",
					 "vfo-b-v","vfo-b-u","h-fm","h-v","h-u","p1","p2","p3","p4"]}
	
	if (verbose): print("Reading: " + f)
	
	with open(f, "r") as f:	
		dialect = csv.Sniffer().sniff(f.read(1024))	# get the CSV dialect
		f.seek(0)									# seek to the beginning of the file
		reader = csv.reader(f, dialect)				# create a CSV reader
		next(reader)								# read and discard the CSV header
		
		for row in reader:
			r = []
			
			# skip blank lines
			if (row[0] == "" and row[1] == ""):
				continue
			
			# get channel number
			if (row[0].isdigit() and int(row[0]) >= 1 and int(row[0]) <= 200):
				ch = int(row[0])
			elif(row[0].lower() in fields["ch"]):
				ch = fields["ch"].index(row[0].lower())+201
			else:
				sys.stderr.write("Invalid Row Number: " + row[0] + "\n")
				sys.exit(1)
			
			# check for duplicate channels
			if (ch in [c[0] for c in channels]):
				sys.stderr.write("Error Duplicate Channel: " + row[0] + "\n")
				sys.exit(1)
			
			# add channel number
			r.append(ch)
			
			# this field is always 1
			r.append(int(1))
			
			# get skip
			if (row[11].lower() in fields["skip"]):
				r.append(fields["skip"].index(row[11].lower()))
			elif (len(row[11]) == 0):
				r.append(0)
				if (verbose):
					print("Warning Channel: " + row[0] + " Scan is blank, defaulting to \"Skip\"")
			else:
				sys.stderr.write("Error Channel " + row[0] + ": Scan must contain \"Scan\" or \"Skip\"\n")
				sys.exit(1)
			
			# get frequency
			try:
				freq = float(row[1])
				if ((freq >= 136.0 and freq <= 174) or (freq >= 400.0 and freq <= 480) or (freq >= 65.0 and freq <= 108)):
					r.append(freq)
				else:
					sys.stderr.write("Error Channel " + row[0] + ": Frequency out of range\n")
					sys.stderr.write("Must be 65-108MHz, 136-174MHz, or 400-480MHz\n")
					sys.exit(1)
			except ValueError as e:
				sys.stderr.write("Error Channel " + row[0] + ": Frequency out of range\n")
				sys.stderr.write("Must be 65-108MHz, 136-174MHz, or 400-480MHz\n")
				sys.exit(1)
			
			# get offset
			try:
				if (len(row[2]) == 0):
					ofs = 0
				else:
					ofs = float(row[2])
				r.append(ofs)
			except ValueError as e:
				sys.stderr.write("Error Channel " + row[0] + ": Invalid offset\n")
				sys.exit(1)
			
			# get tx power
			if (row[10].lower() in fields["txPower"]):
				r.append(fields["txPower"].index(row[10].lower()))
			elif (len(row[10]) == 0):
				r.append(2)
				if (verbose):
					print("Warning Channel: " + row[0] + " TX Power is blank, defaulting to \"High\"")
			else:
				sys.stderr.write("Error Channel " + row[0] + ": TX Power must contain \"Low\",\"Mid\", or \"High\"\n")
				sys.exit(1)
				
			# get tx ctcss
			if (row[6].lower() == "off"):
				r.append(0)
			elif (row[6].replace('.','',1).isdigit() and float(row[6]) in fields["ctcss"]):
				r.append(fields["ctcss"].index(float(row[6]))+1)
			elif (len(row[6]) == 0):
				r.append(0)
				if (verbose):
					print("Warning Channel: " + row[0] + " TX CTCSS is blank, defaulting to \"Off\"")
			else:
				sys.stderr.write("Error Channel " + row[0] + ": TX CTCSS must contain \"Off\" or a valid CTCSS frequency\n")
				sys.exit(1)
				
			# get rx ctcss
			if (row[5].lower() == "off"):
				r.append(0)
			elif (row[5].replace('.','',1).isdigit() and float(row[5]) in fields["ctcss"]):
				r.append(fields["ctcss"].index(float(row[5]))+1)
			elif (len(row[5]) == 0):
				r.append(0)
				if (verbose):
					print("Warning Channel: " + row[0] + " RX CTCSS is blank, defaulting to \"Off\"")
			else:
				sys.stderr.write("Error Channel " + row[0] + ": RX CTCSS must contain \"Off\" or a valid CTCSS frequency\n")
				sys.exit(1)
				
			# get tx dcs
			if (row[8].lower() == "off"):
				r.append(0)
			elif (row[8].isdigit() and int(row[8]) in fields["dcs"]):
				r.append(fields["dcs"].index(int(row[8]))+1)
			elif (len(row[8]) == 0):
				r.append(0)
				if (verbose):
					print("Warning Channel: " + row[0] + " TX DCS is blank, defaulting to \"Off\"")
			else:
				sys.stderr.write("Error Channel " + row[0] + ": TX DCS must contain \"Off\" or a valid DCS code\n")
				sys.exit(1)
				
			# get rx dcs
			if (row[7].lower() == "off"):
				r.append(0)
			elif (row[7].isdigit() and int(row[7]) in fields["dcs"]):
				r.append(fields["dcs"].index(int(row[7]))+1)
			elif (len(row[7]) == 0):
				r.append(0)
				if (verbose):
					print("Warning Channel: " + row[0] + " RX CTCSS is blank, defaulting to \"Off\"")
			else:
				sys.stderr.write("Error Channel " + row[0] + ": RX CTCSS must contain \"Off\" or a valid DCS code\n")
				sys.exit(1)
			
			# get auto offset
			if (row[3].lower() in fields["autoOfs"]):
				r.append(fields["autoOfs"].index(row[3].lower()))
			elif (len(row[3]) == 0):
				r.append(0)
				if (verbose):
					print("Warning Channel: " + row[0] + " Auto Offset is blank, defaulting to \"Off\"")
			else:
				sys.stderr.write("Error Channel " + row[0] + ": Auto Offset must contain \"On\" or \"Off\"\n")
				sys.exit(1)
			
			# get offset dir
			if (row[4].lower() in fields["ofsDir"]):
				r.append(fields["ofsDir"].index(row[4].lower()))
			elif (len(row[4]) == 0):
				r.append(2)
				if (verbose):
					print("Warning Channel: " + row[0] + " Offset Dir is blank, defaulting to \"Simplex\"")
			else:
				sys.stderr.write("Error Channel " + row[0] + ": Offset Dir must contain \"+\",\"-\", or \"Simplex\"\n")
				sys.exit(1)
			
			# get wide/narrow
			if (row[12].lower() in fields["narrow"]):
				r.append(fields["narrow"].index(row[12].lower()))
			elif (len(row[12]) == 0):
				r.append(0)
				if (verbose):
					print("Warning Channel: " + row[0] + " Width is blank, defaulting to \"Wide\"")
			else:
				sys.stderr.write("Error Channel " + row[0] + ": Width must contain \"Wide\" or \"Narrow\"\n")
				sys.exit(1)
				
			# get step
			if (row[13].lower() in fields["step"]):
				r.append(fields["step"].index(row[13].lower()))
			elif (len(row[13]) == 0):
				r.append(0)
				if (verbose):
					print("Warning Channel: " + row[0] + " Step is blank, defaulting to \"Auto\"")
			else:
				sys.stderr.write("Error Channel " + row[0] + ": Step must contain \"Auto\" or a valid step width:\n")
				sys.stderr.write("5K, 6.25K, 10K, 12.5K, 15K, 20K, 25K, 50K, 100K")
				sys.exit(1)
				
			# get sql type
			if (row[14].lower() in fields["sqlType"]):
				r.append(fields["sqlType"].index(row[14].lower()))
			elif (len(row[14]) == 0):
				r.append(0)
				if (verbose):
					print("Warning Channel: " + row[0] + " SQL Type is blank, defaulting to \"Off\"")
			else:
				sys.stderr.write("Error Channel " + row[0] + ": SQL Type must contain \"Off\" or a valid squelch type:\n")
				sys.stderr.write("R-Tone, T-Tone, TSQL, REV TN, DCS, PAGER")
				sys.exit(1)
			
			# get label
			if (len(row[9]) > 8):
				r.append(bytes(row[9][0:8].encode("ascii")))
				if (verbose):
					print("Warning Channel: " + row[0] + " Name truncated to 8 characters")
			else:
				r.append(bytes(row[9].ljust(8).encode("ascii")))
			
			# pack data into struct format and store in array
			rowData = struct.pack("<BxBx?xddBxBxBxBxBx?xBx?xBxBx8s14x", *r)
			channels.append(rowData)
			
			# get list of banks for this channel
			chBanks = row[15].replace(" ", "").split(",")
			# add banks to the array
			for bank in chBanks:
				if (bank.isdigit() and (ch <= 220) and (int(bank) >=1) and (int(bank) <= 10)):
					banks[int(bank)-1].append(ch)

# write the data to the .dat file
def writeDatFile(f, useDefault):
	# get the file header
	if (useDefault):
		print("Warning: Using default settings for the radio")
		header = defaultHeader
	else:
		header = getHeader(f)
	
	if (verbose): print("Writing: " + f)
	
	with open(f, "wb") as f:
		#write the header
		f.write(header)
		
		# write the number of channels
		f.write(bytes((len(channels), 0)))
		
		# seek to beginning of bank 1
		f.seek(0x12A)
		for b in banks:
			for ch in b:
				f.write(bytes((ch,0)))
			for i in range(0, 220-len(b)):
				f.write(bytes((0,0)))
		
		# seek to beginning of channel data
		f.seek(0x125A)
		
		# write channels to file
		for ch in channels:
			f.write(ch)

# print configuration info to the terminal
def printConfig(f):
	cfg = {
		"rfSql":	["Off", "S1", "S2", "S3", "S4", "S5", "S6", "S8", "Full"],
		"batSave":	["Off", "0.2 Seconds", "0.3 Seconds", "0.5 Seconds", "1 Seconds", "2 Seconds"],
		"lamp":		["5 Seconds", "10 Seconds", "30 Seconds", "Continuous", "Off"],
		"mon":		["Monitor", "1750 Hz", "2100 Hz", "1000 Hz", "1450 Hz"],
		"beep":		["Keypad & Scan Stop", "Keypad", "Off"],
		"keyLock":	["Keypad", "PTT", "Keypad & PTT"],
		"vfoScan":	["Band", "1 MHz", "2 MHz", "5 MHz", "All", "PMS1", "PMS2", "PMS3", "PMS4", "PMS5", "PMS6", "PMS7", "PMS8", "PMS9", "PMS10"],
		"scanRes":	["Busy", "Hold", "Time"],
		"artsMode":	["Off", "In Range", "Always"],
		"artsInt":	["15 Seconds", "25 Seconds"],
		"bell":		["Off", "1 Time", "3 Times", "5 Times", "8 Times", "Continuous"],
		"dtmfMod":	["Manual", "Auto"],
		"dtmfDel":	["50ms", "250ms", "450ms", "750ms", "1000ms"],
		"dtmfSpd":	["50ms", "100ms"],
		"pMode":	["Menu", "Frequency", "Channel"],
		"pMenu":	{0:"None", 1:"APO", 2:"ARTS", 3:"BATTSAVE", 4:"B-CH.L/O", 5:"BEEP", 6:"BELL", 7:"COMPANDER", 
					 8:"CTCSS", 9:"CW ID", 10:"DC VOLT", 11:"DCS CODE", 12:"DTMF SET", 13:"DTMF WRT", 14:"EDG.BEEP", 
					 15:"KEY LOCK", 16:"LAMP", 17:"LED", 18:"MEM-DEL", 19:"MON/T-CL", 20:"NAME TAG", 21:"PAGER", 
					 22:"PASSWORD", 23:"PRI.RVT", 24:"REPEATER", 25:"RESUME", 26:"RF SQL", 27:"SCN.LAMP", 28:"SKIP", 
					 29:"SQL TYPE", 30:"STEP", 31:"TOT", 32:"TX PWR", 33:"TX SAVE", 34:"VFO.SPL", 35:"VOX", 36:"WFM.RCV",
					 37:"WIDE/NAR", 38:"WX ALERT", 66:"ARTS-BEEP", 72:"CTCSS-TX", 73:"CW ID-TX", 76:"DTMF SET-MODE", 
					 81:"LED-TX", 85:"PAGER-TX", 88:"REPEATER-ARS", 130:"ARTS-INTV", 136:"CTCSS-RX", 137:"CW ID-ID", 
					 140:"DTMF SET-DELAY", 145:"LED-BUSY", 149:"PAGER-RX", 152:"REPEATER-MODE", 204:"DTMF SET-SPEED",
					 213:"PAGER-ACK", 216:"REPEATER-SHIFT"}
	}
			
	header = getHeader(f)
	model = header[0:5].decode("ascii")
	if (model != "H-420" and model != "FT-25"):
		sys.stderr.write("Error: unable to get header. Wrong file format?\n")
		sys.exit(1)
	
	# unpack the header data
	hdr = struct.unpack("<4H?x2H?x?x6s3H?x2H?x?xH?x2H?x?x?x?x?x?x?x5H?x?x4s16s16s16s16s16s16s16s16s16s14H", header[0x00A:0x106]);
	
	# print out all of the values
	print("Squelch:              {}".format(hdr[46]))
	print("RF SQL:               {}".format(cfg["rfSql"][hdr[21]]))
	print("Time Out Timer:       {}".format((lambda x: "Off" if x==0 else "{} Minutes".format(x))(hdr[29])))
	print("VOX:                  {}".format(hdr[26]))
	print("VFO Split:            {}".format(hdr[25]))
	print("Battery Save:         {}".format(cfg["batSave"][hdr[3]]))
	print("TX Save:              {}".format(hdr[24]))
	print("Auto Power Off:       {}".format((lambda x: "Off" if x==0 else "{:3.1f} Hours".format(x/2))(hdr[0])))
	print("LCD Backlight:        {}".format(cfg["lamp"][hdr[15]]))
	print("Monitor / Tcall:      {}".format(cfg["mon"][hdr[18]]))
	print("Key Lockout:          {}".format(cfg["keyLock"][hdr[14]]))
	
	print("")
	if (hdr[35]): print("Password:             {}".format(hdr[36].decode("ascii")))
	else:         print("Password:             Disabled")
	
	print("TX LED:               {}".format(hdr[16]))
	print("Busy LED:             {}".format(hdr[17]))
	print("Busy Channel Lockout: {}".format(hdr[4]))
	print("Weather Alert:        {}".format(hdr[28]))
	print("Wide FM Receive:      {}".format(hdr[27]))
	print("Band Edge Beep:       {}".format(hdr[13]))
	print("Scramble:             {}".format(hdr[23]))
	print("Beep:                 {}".format(cfg["beep"][hdr[5]]))
	print("Voice Compander:      {}".format(hdr[7]))
	print("Priority Revert:      {}".format(hdr[19]))
	
	print("\nProgramable Keys:")
	if   (hdr[48] == 0): print("P1 Key:               Menu:    {}".format(cfg["pMenu"][hdr[49]]))
	elif (hdr[48] == 2): print("P1 Key:               {}".format(cfg["pMode"][hdr[48]]))
	elif (hdr[48] == 2): print("P1 Key:               Channel: {}".format(hdr[56]+1))
	
	if   (hdr[50] == 0): print("P2 Key:               Menu:    {}".format(cfg["pMenu"][hdr[51]]))
	elif (hdr[50] == 1): print("P2 Key:               {}".format(cfg["pMode"][hdr[50]]))
	elif (hdr[50] == 2): print("P2 Key:               Channel: {}".format(hdr[57]+1))
	
	if   (hdr[52] == 0): print("P3 Key:               Menu:    {}".format(cfg["pMenu"][hdr[53]]))
	elif (hdr[52] == 1): print("P3 Key:               {}".format(cfg["pMode"][hdr[52]]))
	elif (hdr[52] == 2): print("P3 Key:               Channel: {}".format(hdr[58]+1))
		
	if   (hdr[54] == 0): print("P4 Key:               Menu:    {}".format(cfg["pMenu"][hdr[55]]))
	elif (hdr[54] == 1): print("P4 Key:               {}".format(cfg["pMode"][hdr[54]]))
	elif (hdr[54] == 2): print("P4 Key:               Channel: {}".format(hdr[59]+1))
	
	print("\nScan:")
	print("VFO Scan:             {}".format(cfg["vfoScan"][hdr[47]]))
	print("Scan Resume:          {}".format(cfg["scanRes"][hdr[20]]))
	print("Scan Lamp:            {}".format(hdr[22]))
	
	print("\nDTMF Dialer:")
	print("DTMF Mode:            {}".format(cfg["dtmfMod"][hdr[10]]))
	if (hdr[10]):
		print("DTMF Delay:           {}".format(cfg["dtmfDel"][hdr[11]]))
		print("DTMF Speed:           {}".format(cfg["dtmfSpd"][hdr[12]]))
		print("DTMF Memory 1:        {}".format(hdr[37].decode("ascii")))
		print("DTMF Memory 2:        {}".format(hdr[38].decode("ascii")))
		print("DTMF Memory 3:        {}".format(hdr[39].decode("ascii")))
		print("DTMF Memory 4:        {}".format(hdr[40].decode("ascii")))
		print("DTMF Memory 5:        {}".format(hdr[41].decode("ascii")))
		print("DTMF Memory 6:        {}".format(hdr[42].decode("ascii")))
		print("DTMF Memory 7:        {}".format(hdr[43].decode("ascii")))
		print("DTMF Memory 8:        {}".format(hdr[44].decode("ascii")))
		print("DTMF Memory 9:        {}".format(hdr[45].decode("ascii")))
	
	print("\nARTS:")
	print("ARTS Mode:            {}".format(cfg["artsMode"][hdr[1]]))
	if (hdr[1]):
		print("ARTS Interval:        {}".format(cfg["artsInt"][hdr[2]]))
		print("ARTS CW ID:           {}".format(hdr[8]))
		print("ARTS Callsign:        {}".format(hdr[9].decode("ascii")))
	
	print("\nPager:")
	print("Answer Back:          {}".format(hdr[34]))
	print("Bell:                 {}".format(cfg["bell"][hdr[6]]))
	print("Pager TX:             {:5s} Hz {:5s} Hz".format(fields["ctcss"][hdr[30]+1], fields["ctcss"][hdr[31]+1]))
	print("Pager RX:             {:5s} Hz {:5s} Hz".format(fields["ctcss"][hdr[32]+1], fields["ctcss"][hdr[33]+1]))

# print the channels
def printChannels(f):
	readDatFile(f)
	
	print("Channel Listing:")
	for ch in channels:
		if (ch[0] <= 200):
			# offset
			if   (ch[10] == 0): ofs = "+{:3.1f}MHz".format(ch[3])
			elif (ch[10] == 1): ofs = "-{:3.1f}MHz".format(ch[3])
			else:               ofs = "Simplex"
			
			# squelch mode
			if   (ch[13] >= 1 and ch[13] <= 4): sql = "T {:5s}, R {:5s}".format(fields["ctcss"][ch[5]],fields["ctcss"][ch[6]],)
			elif (ch[13] == 5):                 sql = "T {:5s}, R {:5s}".format(fields["dcs"][ch[7]],fields["dcs"][ch[8]])
			else:                               sql = ""
			
			# print channel
			print("CH: {:03d}  Freq: {:7.3f} MHz {:7s}  Name: {:8s}  SQL: {:6s} {}".format(ch[0], ch[2], ofs, ch[14].decode("ascii"), fields["sqlType"][ch[13]], sql))

main()
