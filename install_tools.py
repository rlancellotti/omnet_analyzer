#!/usr/bin/python3
import os
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--force', action='store_true', help='force install using ~/bin directory if omnet is not found')
args = parser.parse_args()

src = os.path.dirname(os.path.realpath(__file__))
omnet_release=os.getenv('OMNETPP_RELEASE')
path=os.getenv('PATH').split(':')
dest = '%s/bin' % os.path.expanduser('~')
if omnet_release is None:
    print('Omnet environment is not set')
    if args.force:
        print('\tcontinuing because force is set')
    else:
        sys.exit(-1)
if omnet_release is not None:
    for p in path:
        if omnet_release in p:
            dest=p
files = []
for (dirpath, dirnames, filenames) in os.walk(src):
    files.extend(filenames)
    break

if not os.path.exists(dest):
    print('reating directory %s' % dest)
    os.makedirs(dest)

for f in files:
    sourcefile=src + '/' + f
    destfile=dest + '/' + f
    if os.path.islink(destfile) or (os.path.exists(destfile) and args.force):
        print('removing '+ destfile)
        os.unlink(destfile)
    print(sourcefile + ' ->\t' + destfile)
    os.symlink(sourcefile, destfile)
