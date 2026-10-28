"""Run protocol tests on the host; does not access a programmer or motherboard."""
from pathlib import Path
import argparse,os,shutil,subprocess,tempfile
p=argparse.ArgumentParser();p.add_argument('--cc',default=os.environ.get('CC') or shutil.which('gcc') or shutil.which('cc'));a=p.parse_args()
if not a.cc:p.error('Native GCC required; install it or use --cc')
r=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='iigs-rtc-test-') as d:
 out=Path(d)/('test.exe' if os.name=='nt' else 'test')
 subprocess.run([a.cc,'-std=c99','-O2','-Wall','-Wextra','-Werror','-I'+str(r/'tests/stubs'),str(r/'tests/protocol_test.c'),'-o',str(out)],check=True)
 subprocess.run([str(out)],check=True)
