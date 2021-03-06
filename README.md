# FT-65 codeplug to CSV converter
This program converts between the binary data format for the Yaesu FT-65 software and a CSV file to allow easy editing in a spreadsheet before converting it back to the binary format to be uploaded to your radio. It should also work with the FT-25 as the format seems to be almost identical.
It is written in python and will run on any operating system that python supports.  
The only dependency needed to run ft65convert is [Python 3](https://www.python.org/downloads/).

## This program is obsolete
The FT-65 is supported by CHIRP now.

## Usage:
Start by downloading the data from your radio using the free software provided by Yaesu and save it to a file (my_channels.dat for example). This contains all of the configuration data for your radio as well as all of the channels.  
Run `ft65convert --csv my_channels.dat my_channels.csv` to convert the data from your radio to a CSV file.  
Open the CSV file in your preferred spreadsheet software to edit it.  
The CSV file uses a comma (,) as the separator and double quote (") as the string delimiter. 
When you are finished editing, save the spreadsheet. Make sure it is saved as a CSV file and not as a .ods or .xls file.  
Run `ft65convert --bin my_channels.dat my_channels.csv` to convert it back to the binary code plug format. If there are any invalid values entered in the CSV file, an error will be displayed with the line number that needs to be corrected. The conversion will not be performed until all values are correct in the CSV. After conversion, open the .dat file with the Yaesu software and upload it back to the radio.  
When converting back to the binary format the destination .dat file must already exist as it contains all of the configuration for your radio. You can provide the `--default` option to create the .dat file when converting, but it will reset all of your settings back to stock when uploaded to your radio.  
If a CSV file is not specified when converting to CSV, the output will be named the same as the input with the file extension changed to .csv.  
If ft65convert is run with the .dat file as the only argument, it will display the channels stored in it.  
The `--config` option will display all of the settings in the .dat file.

This program is currently in alpha. I have been using this program with my FT-65 and it has been working correctly. However, make sure to backup your settings before using ft65convert on them in case anything goes wrong.

### Parameters:
    positional arguments:
      datFile        Binary data file from FT-65 Memory Programmer (Required)
      csvFile        CSV file (Required for --bin)
    
    optional arguments:
      -h, --help     show this help message and exit
      -v, --version  show program's version number and exit
      -V, --verbose  Prints warnings during conversion
      -c, --csv      Convert binary data to CSV file
      -b, --bin      Convert CSV file to binary data
      -d, --default  Use default radio settings
      -C, --config   Prints configuration info

### Examples:
    ft65convert --csv input.dat output.csv      # convert input.dat to output.csv
    ft65convert --bin output.dat input.csv      # convert input.csv to output.dat
    ft65convert --config input.dat              # print radio configuration
    ft65convert input.dat                       # print channels


## CSV Format:
The first row in the CSV file is the header.  
Values are not case sensitive.

| Col | Parameter            | Values |
| --- | -------------------- | --- |
|  A  |  Channel number      | 1-200 \| Special Channels
|  B  |  Receive frequency   | 65-108 MHz \| 136-174 MHz \| 400-480 MHz
|  C  |  Offset frequency    | 0.05-99.975 MHz
|  D  |  Auto Offset         | On \| Off
|  E  |  Offset Direction    | + \| - \| Simplex
|  F  |  Receive CTCSS tone  | Off \| Valid CTCSS Frequencies
|  G  |  Transmit CTCSS tone | Off \| Valid CTCSS Frequencies
|  H  |  Receive DCS code    | Off \| Valid DCS Codes
|  I  |  Transmit DCS code   | Off \| Valid DCS Codes
|  J  |  Channel name        | 8 ASCII characters max
|  K  |  Transmit Power      | Low \| Mid \| High
|  L  |  Scan                | Scan \| Skip
|  M  |  Deviation           | Wide \| Narrow
|  N  |  Frequency Step      | Auto \| 5K \| 6.25K \| 10K \| 12.5K \| 15K \| 20K \| 25K \| 50K \| 100K
|  O  |  Squelch Type        | Off \| R-Tone \| T-Tone \| TSQL \| REV TN \| DCS \| PAGER
|  P  |  Bank number         | 1-10

### Special Channels:
| Name     | Description                                   |
|----------|----------------------------------------------|
| VFO-A-V  | VFO A VHF Settings                           |
| VFO-A-U  | VFO B UHF Settings                           |
| VFO-B-V  | VFO B VHF Settings                           |
| VFO-B-U  | VFO B UHF Settings                           |
| VFO-B-FM | VFO B FM broadcast band frequency            |
| H-V      | VHF Home Frequency                           |
| H-U      | UHF Home Frequency                           |
| H-FM     | FM Broadcast Home Frequency                  |
| P1       | Frequency that can be assigned to the P1 key |
| P2       | Frequency that can be assigned to the P2 key | 
| P3       | Frequency that can be assigned to the P3 key |
| P4       | Frequency that can be assigned to the P4 key |
| L1-L10   | Programmable Memory Scan Lower Range         |
| U1-U10   | Programmable Memory Scan Upper Range         |

### Valid CTCSS Frequencies:
|       |       |       |       |       |       |       |       |       |       |
| ----- | ------| ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- |
|  67.0 |  69.3 |  71.9 |  74.4 |  77.0 |  79.7 |  82.5 |  85.4 |  88.5 |  91.5 |
|  94.8 |  97.4 | 100.0 | 103.5 | 107.2 | 110.9 | 114.8 | 118.8 | 123.0 | 127.3 |
| 131.8 | 136.5 | 141.3 | 146.2 | 151.4 | 156.7 | 159.8 | 162.2 | 165.5 | 167.9 |
| 171.3 | 173.8 | 177.3 | 179.9 | 183.5 | 186.2 | 189.9 | 192.8 | 196.6 | 199.5 |
| 203.5 | 206.5 | 210.7 | 218.1 | 225.7 | 229.1 | 233.6 | 241.8 | 250.3 | 254.1 |

### Valid DCS Codes:
|     |     |     |     |     |     |     |     |     |     |
| --- | ----| --- | --- | --- | --- | --- | --- | --- | --- |
| 023 | 025 | 026 | 031 | 032 | 036 | 043 | 047 | 051 | 053 |
| 054 | 065 | 071 | 072 | 073 | 074 | 114 | 115 | 116 | 122 |
| 125 | 131 | 132 | 134 | 143 | 145 | 152 | 155 | 156 | 162 |
| 165 | 172 | 174 | 205 | 212 | 223 | 225 | 226 | 243 | 244 |
| 245 | 246 | 251 | 252 | 255 | 261 | 263 | 265 | 266 | 271 |
| 274 | 306 | 311 | 315 | 325 | 331 | 332 | 343 | 346 | 351 |
| 356 | 364 | 365 | 371 | 411 | 412 | 413 | 423 | 431 | 432 |
| 445 | 446 | 452 | 454 | 455 | 462 | 464 | 465 | 466 | 503 |
| 506 | 516 | 523 | 526 | 532 | 546 | 565 | 606 | 612 | 624 |
| 627 | 631 | 632 | 654 | 662 | 664 | 703 | 712 | 723 | 731 |
| 732 | 734 | 743 | 754 |     |     |     |     |     |     |

