"""Validate image formats, checksums, padding and separate FLASH/EEPROM/fuses."""
from pathlib import Path
import argparse,hashlib,json
p=argparse.ArgumentParser();p.add_argument('directory',type=Path);a=p.parse_args();r=a.directory
def ihex(path):
 data={};base=0;end=False
 for line in path.read_text().splitlines():
  assert line.startswith(':'),'Not Intel HEX'
  b=bytes.fromhex(line[1:]);assert len(b)==b[0]+5 and sum(b)&255==0
  address=(b[1]<<8)|b[2];kind=b[3];payload=b[4:-1]
  if kind==0:
   for i,v in enumerate(payload):
    key=base+address+i;assert key not in data;data[key]=v
  elif kind==1:end=True
  elif kind==2:base=int.from_bytes(payload,'big')<<4
  elif kind==4:base=int.from_bytes(payload,'big')<<16
  else:raise AssertionError('Unexpected HEX record type')
 assert end and data
 assert set(data)==set(range(max(data)+1)),'Non-contiguous/address-shifted image'
 return bytes(data[i] for i in range(max(data)+1))
flash=(r/'flash.bin').read_bytes();ee=(r/'eeprom_raw.bin').read_bytes()
assert ihex(r/'flash.hex')==flash
assert ihex(r/'eeprom.eep')==ee
assert (r/'fuses.bin').read_bytes()==bytes.fromhex('e15dff')
assert (r/'t48_flash_8k.bin').read_bytes()==flash.ljust(8192,b'\xff')
assert (r/'t48_eeprom_512.bin').read_bytes()==ee.ljust(512,b'\xff')
assert len(flash)<=8192 and len(ee)==260
m=json.loads((r/'manifest.json').read_text(encoding='utf-8'))
for n,v in m['files'].items():
 image=(r/n).read_bytes()
 assert len(image)==v['bytes']
 assert hashlib.sha256(image).hexdigest()==v['sha256']
expected=''.join(v['sha256']+'  '+n+'\n' for n,v in m['files'].items())
assert (r/'SHA256SUMS').read_text(encoding='ascii')==expected
print('PASS: FLASH HEX/BIN, EEPROM EEP/BIN, T48 padded images, fuses and SHA256')
