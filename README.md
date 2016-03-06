# SWF Format Switcher

This script can be used to change one flash format to other format.
for example, flash (swf) have three signatures such as FWS, CWS and ZWS

FWS means there is no compression used in the flash file
CWS is for zlib compressed flash file
ZWS is for LZMA compressed flash file

ZWS can only be used for swf files with version > 12
CWS can only be used for swf files with version > 5
FWS - no such limit

Specifications:

FWS:
    signature       : 3 bytes
    version         : 1 byte
    fileSize        : 4 bytes
    RECT Structure  : 9 bytes
    frame Rate      : 2 bytes
    frame Count     : 2 bytes
    Tags            : n bytes
    
CWS:
    signature       : 3 bytes
    version         : 1 byte
    fileSize        : 4 bytes
    Zlib Data       : n bytes
    
ZWS:
    signature       : 3 bytes
    version         : 1 byte
    fileSize        : 4 bytes
    compressed len  : 4 bytes
    LZMA Props      : 5 bytes
    LZMA Data       : n bytes
    LZMA end marker : 6 bytes
    
this script is capable of giving you file in different format
You will be able to switch from ZWS to FWS or CWS, FWS to CWS or ZWS and CWS to FWS or ZWS.

Requirements:
- Written for Python 3
- Makes use of standard libraries except pylzma which can be installed from pip3

Usage:
$python3 flash-format-switcher.py --input /tmp/outFolder/tc6.swf --output /tmp/outFolder/tc7.swf --format CWS
