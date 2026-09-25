from pathlib import Path
import hashlib, argparse

NINTENDO_LOGO=bytes.fromhex("24ffae51699aa2213d84820a84e409ad11248b98c0817f21a352be199309ce2010464a4af82731ec58c7e83382e3cebf85f4df94ce4b09c194568ac01372a7fc9f844d73a3ca9a615897a327fc039876231dc7610304ae56bf38840040a70efdff52fe036f9530f197fbc08560d68025a963be03014e38e2f9a234ffbb3e0344780090cb88113a9465c07c6387f03cafd625e48b380aac7221d4f807")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--payload',default='payload.bin')
    ap.add_argument('--output',default='SIM_EARTH_PIXEL_UNIVERSE_LOST_COSMOS_V2.gba')
    args=ap.parse_args()
    root=Path(__file__).resolve().parent
    payload=(root/args.payload).read_bytes()
    header=bytearray(0xC0)
    header[0:4]=bytes.fromhex('2e0000ea')
    header[4:0xA0]=NINTENDO_LOGO
    header[0xA0:0xAC]=b'LOSTCOSMOSV2'
    header[0xAC:0xB0]=b'LCV2'
    header[0xB0:0xB2]=b'01'
    header[0xB2]=0x96
    header[0xBC]=2
    header[0xBD]=(-sum(header[0xA0:0xBD])-0x19)&0xFF
    rom=bytes(header)+payload
    size=1
    while size<len(rom): size<<=1
    if size<65536: size=65536
    rom+=b'\xFF'*(size-len(rom))
    out=root/args.output
    out.write_bytes(rom)
    print('ROM',out)
    print('size',len(rom))
    print('sha256',hashlib.sha256(rom).hexdigest())
    print('header_checksum',hex(header[0xBD]))
if __name__=='__main__': main()
