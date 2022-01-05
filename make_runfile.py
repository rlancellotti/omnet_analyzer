#!/usr/bin/python3
import configparser
import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('-z', '--zip', action='store_true', help='compress output with gzip')
parser.add_argument('-o', '--output', help='oputput file, Default Runfile')
parser.add_argument('-f', '--file', help='input file default omnetpp.ini')

args = parser.parse_args()

def get_scaname(config, run, zip=False):
    ext= 'sca.gz' if zip else 'sca'
    return 'results/%s-\#%d.%s'%(config, run, ext)

def from_scaname(scaname):
    basename=Path(scaname).name.split('.')[0]
    r=basename.split('-\#')
    return (basename, r[0], r[1])

def write_target(f, scaname, inifile='omnetpp.ini', sleeptime=1):
    compression = scaname.endswith('.gz')
    (basename, conf, run)=from_scaname(scaname)
    f.write('%s: %s\n' % (scaname, inifile))
    f.write('\trm -f results/%s.sca results/%s.sca.gz results/%s.vec results/%s.vci\n'%(basename, basename, basename, basename))
    f.write('\t./run -u Cmdenv -c %s -r %s -f %s --cmdenv-performance-display=false --cmdenv-status-frequency=60s -s\n'%(conf, run, inifile))
    f.write('\tsleep %d\n'%sleeptime)
    if compression:
        f.write('\tgzip %s\n'%scaname.replace('.gz',''))
    return scaname

def write_clean(f):
    f.write('clean:\n')
    f.write('\trm -f results/*.sca results/*.sca.gz results/*.vec results/*.vci\n')

def write_all(f, targetlist):
    f.write('all: %s\n' % ' '.join(targetlist))

inifile=args.file if args.file else 'omnetpp.ini'
outfile=args.output if args.output else 'Runfile'

cp = configparser.ConfigParser(strict=False)
cp.read(inifile)
nrun=int(cp['General']['repeat'])
configs=[]
for c in cp.sections():
    if (c.startswith('Config ') and 'Base' not in c):
        configs.append(c.split()[1])
targetlist=[]
print('writing %d configurations with %d runs each' %(len(configs), nrun))
with open(outfile, 'w+') as f:
    for c in configs:
        for r in range(0, nrun):
            targetlist.append(get_scaname(c, r, zip=args.zip))
    #print(targetlist)
    write_all(f, targetlist)
    for t in targetlist:
        write_target(f, t, inifile=inifile)
    write_clean(f)
