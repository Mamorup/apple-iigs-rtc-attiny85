"""Portable AVR build/export. Does not connect to a programmer or set fuses."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--toolchain', type=Path, default=os.environ.get('AVR_TOOLCHAIN_PATH'),
                    help='Folder containing avr-gcc/avr-objcopy/avr-size; otherwise use PATH')
parser.add_argument('--output', type=Path, default=root / 'build')
args = parser.parse_args()
out = args.output.resolve(); out.mkdir(parents=True, exist_ok=True)

def tool(name):
    suffix = '.exe' if os.name == 'nt' else ''
    found = str(args.toolchain / (name + suffix)) if args.toolchain else shutil.which(name)
    if not found or not Path(found).is_file():
        raise SystemExit(name + ' missing; install AVR GCC/binutils or set --toolchain')
    return found

gcc, objcopy, size = [tool(x) for x in ['avr-gcc', 'avr-objcopy', 'avr-size']]
def run(*cmd):
    subprocess.run([str(x) for x in cmd], check=True)

elf = out / 'rtc.elf'
run(gcc, '-mmcu=attiny85', '-std=gnu11', '-Os', '-Wall', '-Wextra', '-Werror',
    '-ffunction-sections', '-fdata-sections', '-Wl,--gc-sections',
    root/'firmware/main_edgefix_v3.c', root/'firmware/serial_edgefix_v3.S', '-o', elf)
for fmt, sections, name in [
    ('binary', ['.text', '.data'], 'flash.bin'),
    ('ihex', ['.text', '.data'], 'flash.hex'),
    ('binary', ['.eeprom'], 'eeprom_raw.bin'),
    ('ihex', ['.eeprom'], 'eeprom.eep'),
    ('binary', ['.fuse'], 'fuses.bin')]:
    command = [objcopy, '-O', fmt]
    for section in sections:command += ['-j', section]
    if sections == ['.eeprom']:command += ['--change-section-lma=.eeprom=0']
    command += [elf, out/name]
    run(*command)
flash = (out/'flash.bin').read_bytes(); ee = (out/'eeprom_raw.bin').read_bytes()
assert len(flash) <= 8192 and len(ee) <= 512
(out/'t48_flash_8k.bin').write_bytes(flash.ljust(8192, b'\xff'))
(out/'t48_eeprom_512.bin').write_bytes(ee.ljust(512, b'\xff'))
assert (out/'fuses.bin').read_bytes() == bytes.fromhex('e15dff')
names = ['flash.bin', 'flash.hex', 'eeprom_raw.bin', 'eeprom.eep', 'fuses.bin',
         't48_flash_8k.bin', 't48_eeprom_512.bin']
manifest = {'variant':'edgefix_v3', 'mcu':'ATtiny85', 'clock_hz':16000000,
            'compiler':subprocess.check_output([gcc,'--version'],text=True).splitlines()[0],
            'fuses':{'low':'E1','high':'5D','extended':'FF','lock':'FF (unlocked)'},
            'files':{n:{'bytes':(out/n).stat().st_size,
                        'sha256':hashlib.sha256((out/n).read_bytes()).hexdigest()} for n in names}}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
(out/'SHA256SUMS').write_text(''.join(manifest['files'][n]['sha256']+'  '+n+'\n' for n in names),encoding='ascii')
run(size, '-A', elf)
print('Built edgefix_v3; outputs:', out)
