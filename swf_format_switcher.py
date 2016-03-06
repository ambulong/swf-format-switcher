import zlib
import pylzma
import struct
import argparse
import io
import tempfile

"""
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
"""

class SWF:
    def __init__(self, flash):

        self.flash = flash
        self.signature = self.flash.read1(3)

        if self.signature != b'CWS' and self.signature != b'ZWS' and self.signature != b'FWS':
            raise TypeError("Input file is not SWF")

        self.version = struct.unpack("<B",self.flash.read1(1))[0]
        self.file_size = struct.unpack("<I", self.flash.read1(4))[0]
        self.file_factor = self.file_size * 4

    def compress_zlib(self):

        self.flash.seek(8)
        self.zlib_compressed = zlib.compress(self.flash.read1(self.file_factor))

        c_zlib_file = io.BytesIO()
        c_zlib_file.write(b'CWS')
        c_zlib_file.write(struct.pack("<B", self.version))
        c_zlib_file.write(struct.pack("<I", self.file_size))
        c_zlib_file.write(self.zlib_compressed)

        c_zlib_file.seek(0)

        return c_zlib_file


    def decompress_zlib(self):

        self.flash.seek(8)
        self.zlib_decompressed = zlib.decompress(self.flash.read1(self.file_factor))
        zlib_file = io.BytesIO()
        zlib_file.write(b'FWS')
        zlib_file.write(struct.pack("<B", self.version))
        zlib_file.write(struct.pack("<I", self.file_size))
        zlib_file.write(self.zlib_decompressed)

        zlib_file.seek(0)

        return zlib_file

    def compress_lzma(self):

        self.flash.seek(8)
        self.lzma_compressed = pylzma.compress(self.flash.read1(self.file_factor))
        self.compressed_file_size = len(self.lzma_compressed) - 5

        lzma_file = io.BytesIO()
        lzma_file.write(b'ZWS')
        lzma_file.write(struct.pack("<B", self.version))
        lzma_file.write(struct.pack("<I", self.file_size))
        lzma_file.write(struct.pack("<I", self.compressed_file_size))
        lzma_file.write(self.lzma_compressed)

        lzma_file.seek(0)

        return lzma_file

    def decompress_lzma(self):

        self.flash.seek(12)
        self.lzma_decompressed = pylzma.decompress(self.flash.read1(self.file_factor))

        c_lzma_file = io.BytesIO()
        c_lzma_file.write(b'FWS')
        c_lzma_file.write(struct.pack("<B", self.version))
        c_lzma_file.write(struct.pack("<I", self.file_size))
        c_lzma_file.write(self.lzma_decompressed)

        c_lzma_file.seek(0)

        return c_lzma_file

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert flash from one format to other')
    parser.add_argument('--input', dest='input', help='input file')
    parser.add_argument('--output', dest='output', help='output file')
    parser.add_argument('--format', dest='format', help='change to either of CWS FWS or ZWS')
    args = parser.parse_args()

    if not args.input:
        raise ValueError("No input file mentioned, read1 help")
    if not args.output:
        raise ValueError("No output file mentioned, read1 help")
    if not args.format:
        raise ValueError("No output format is given, read1 help")

    _input = open(args.input,'rb')
    _file = io.BytesIO
    _file = _input
    swf = SWF(_file)

    if swf.version < 13 and args.format == "ZWS":
        raise TypeError("Only flash which is version > 12 can be compressed to ZWS")
    if swf.version < 6 and args.format == "CWS":
        raise TypeError("Only flash which is version > 5 can be compressed to CWS")

    if (swf.signature == b"FWS" and args.format == "FWS") or (swf.signature == b"ZWS" and args.format == "ZWS") or (swf.signature == b"CWS" and args.format == "CWS"):
        raise TypeError("Input file and output file cannot have same format")

    temp_file = tempfile.NamedTemporaryFile(delete=False)

    if swf.signature != b'FWS':

        if swf.signature == b"CWS":

            print("[+] Current format is CWS")
            fl_object = swf.decompress_zlib()
            temp_file.write(fl_object.read())
            temp_file.close()
            fl_object.seek(0)

            if args.format == 'FWS':
                print("[+] Decompressing into FWS")

            elif args.format == 'ZWS':

                print("[+] ReCompressing into ZWS")
                _temp = open(temp_file.name,'rb')
                _temp_f = io.BytesIO
                _temp_f = _temp

                swf_temp = SWF(_temp_f)
                fl_object = swf_temp.compress_lzma()

            else:
                raise ValueError("[-] Invalid format for conversion")

        else:

            print("[+] Current format is ZWS")
            fl_object = swf.decompress_lzma()

            temp_file.write(fl_object.read())
            temp_file.close()
            fl_object.seek(0)

            if args.format == 'FWS':
                print("[+] Decompressing into FWS")

            if args.format == 'CWS':

                print("[+] ReCompressing into CWS")

                _temp = open(temp_file.name,'rb')
                _temp_f = io.BytesIO
                _temp_f = _temp

                swf_temp = SWF(_temp_f)
                fl_object = swf_temp.compress_zlib()
                del swf_temp

    else:

        print("[+] Current format is FWS")

        if args.format == 'ZWS':
            print("[+] Compressing into ZWS")
            fl_object = swf.compress_lzma()

        else:
            print("[+] Compressing into CWS")
            fl_object = swf.compress_zlib()

    del swf

    converted_file = fl_object.read()

    with open(args.output,'wb') as j:
        j.write(converted_file)

    print("[+] Wrote to the disc")

    fl_object.close()
    _file.close()

    print("[+] Terminated...")