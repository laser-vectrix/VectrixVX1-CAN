# Vectrix VX-1 CAN bus parser

Run as:
$ python VX1Parser.py <datafile>


<datafile> is the file with the CAN BUS messages recording and can assume 3 formats:
1) plain (the default format) in which messages are recorded one per line with the following structure: `<timestamp> | <ID> | <length> | <space separated bytes in hex> |`
e.g.: `0:00:21.000658 | 000000 | 8 | 00 00 00 00 00 00 00 00 | `

2) PEAK PCANView recording older versions (don't know which)
3) PEAK PCANView recording newwer versions (don't know which) - this is beta, please report any issues

The Parser will process all the messages in the file and terminate with a summary of what was parsed and what are the unknown PGNs.  All parsing is performed based on PGN.xml file, which can be updated to include new messages (there are some hardcoded values in the parser, such as BMS readings to be fixed in the future).
A runtime presentation of values can be obtained with options: -o, -v, -vv or -vvv

This parser and PGN file was built based on data from different VX1 found online. It may have some inconsistencies for a given model and specific VX1 configuration. Hopefully inconsistencies can be addressed in the PGN XML file.

```
Usage: 
usage: VX1Parser.py [-h] [-p PGNfilename] [-pcan] [-pcan2] [-v] [-vv] [-vvv] [-f] [-d] [-o] [-q] [-unusedPGN] [-unlistedPGN]
                    [-e] [-c C] [-s S] [-sa SA] [-id ID] [-m]
                    [filename]

Parse CAN BUS messages according with PGN XML file.

positional arguments:
  filename        the log file with CAN BUS messages to be processed (default data.log)

options:
  -h, --help      show this help message and exit
  -p PGNfilename  the XML file with the PGN specification (default PGN.xml)
  -pcan           the log fils is according with PEAK PCAN View dump format.
  -pcan2          the log fils is according with PEAK PCAN View dump format newer version.
  -v              verbose
  -vv             verbose with hex
  -vvv            verbose with bin
  -f              follow the file
  -d              for debugging print the original line
  -o              outputs a list separated by pipes good for being imported into Excel (it overrides -v -vv -vvv and does not
                  print the summary (-q))
  -q              no summary
  -unusedPGN      show PGNs which are not used in the processed (and filtered) log
  -unlistedPGN    show only PGNs which are used but not in PGN.xml
  -e              print timestamps for which messages are separated by more than 1 second
  -c C            the number of lines (inclusive invalid ones) to process (default 0). If c equals 0 all the log will be
                  processed.
  -s S            the number of lines (inclusive invalid ones) to skip before processing (default 0). If greater than -c no
                  lines will be processed.
  -sa SA          filter and only process this Source Address
  -id ID          filter and only process this ID + SA
  -m              monitor a given ID (use with -id and one of -v, -vv, -vvv or -o)
```
