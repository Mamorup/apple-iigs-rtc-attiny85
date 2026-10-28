"""Cycle model of serial_edgefix_v3.S against captured input (not hardware proof)."""
import argparse
from collections import Counter
import numpy as np
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('capture', help='Little-endian uint16 samples: bit0=/EN, bit1=CLK, bit2=DATA')
parser.add_argument('--sample-rate', type=float, required=True, help='Analyzer samples/second, not RTC clock')
args=parser.parse_args()
if args.sample_rate<=0:parser.error('sample rate must be positive')
sample_ns=1e9/args.sample_rate
a=np.memmap(args.capture,dtype='<u2',mode='r')
en=(a&1)!=0
starts=np.flatnonzero(en[:-1]&~en[1:])+1
ends=np.flatnonzero(~en[:-1]&en[1:])+1
transactions=[]
for st in starts:
 j=np.searchsorted(ends,st)
 if j==len(ends):continue
 end=int(ends[j]); st=int(st); v=a[st:end]
 c=(v&2)!=0
 falls=(np.flatnonzero(c[:-1]&~c[1:])+1)*sample_ns
 rises=(np.flatnonzero(~c[:-1]&c[1:])+1)*sample_ns
 if len(falls)!=16 or len(rises)!=16:continue
 de=np.flatnonzero(((v[:-1]^v[1:])&4)!=0)+1
 dt=de*sample_ns; dl=np.r_[int(bool(v[0]&4)),((v[de]&4)!=0).astype(int)]
 def byte(k):
  z=0
  for t in rises[k:k+8]:z=z*2+int(dl[np.searchsorted(dt,t,side='right')])
  return z
 transactions.append((falls,rises,dt,dl,byte(0),byte(8),len(v)*sample_ns))
if not transactions:raise SystemExit('No complete 16-clock transactions found; check rate/channel mapping/file format')
errors=[]; tested=0; min_setup=1e9
for mhz in (14.,16.,18.):
 C=1000./mhz
 for f,r,dt,dl,cmd,data,end in transactions:
  def wait(t,edges):
   # Poll checks at t + n*3 cycles; successful SBIC/SBIS takes 2 cycles.
   # Called before the requested edge; all waits must finish in its phase.
   edge=edges[0]
   return t+max(0,np.ceil((edge-t)/(3*C)))*3*C+2*C
  for phase in np.arange(0,625,39.):
   t=phase+4*C; vals=[]
   for k in range(8):
    t=wait(t,f[k:k+1]); t=wait(t,r[k:k+1])
    vals.append(int(dl[np.searchsorted(dt,t,side='right')])); t+=C
    if k<7 and t>=f[k+1]:errors.append('RX overrun')
   got=0
   for b in vals:got=got*2+b
   if got!=cmd:errors.append(('command',got,cmd))
   # 31 assembly/RET cycles + conservative 100 C dispatch/call + 29 C TX setup.
   t+=(31+100+29)*C
   if cmd&128:
    for k in range(8):
     if k:t=wait(t,r[8+k-1:8+k])
     t=wait(t,f[8+k:9+k]);t+=C
     min_setup=min(min_setup,r[8+k]-t)
     if t>=r[8+k]:errors.append('TX setup')
    if end<=r[15]:errors.append('EN hold')
   else:
    got=0
    # RX next-byte starts after command assembly and C dispatch, not TX setup.
    t-=29*C
    for k in range(8,16):
     t=wait(t,f[k:k+1]);t=wait(t,r[k:k+1])
     got=got*2+int(dl[np.searchsorted(dt,t,side='right')]);t+=C
    if got!=data:errors.append(('write',got,data))
   tested+=1
print('Capture transactions:',len(transactions))
print('Commands:',{hex(k):v for k,v in Counter(t[4] for t in transactions).items()})
print('Clock/phase cases:',tested,'frequencies MHz: 14,16,18')
print('Minimum modeled TX setup ns:',round(min_setup,2))
print('Failures:',len(errors))
if errors:print(errors[:10]);raise SystemExit(1)
