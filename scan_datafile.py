#!/usr/bin/python3
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('datafiles', metavar='F', nargs='+', help='list of .data files')
args = parser.parse_args()

files = args.datafiles
for fname in files:
    print('working on file: %s' % fname)
    with open(fname) as f:
        # read line and remove initial character '#'
        l = f.readline()[1:]
        for i, t in enumerate(l.split()):
            print('\t%d: %s'%(i+1,t))

