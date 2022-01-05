#!/usr/bin/python3
import os
import sys

src = os.path.dirname(os.path.realpath(__file__))
omnet_release=os.getenv('OMNETPP_RELEASE')
if omnet_release is None:
    print('Omnet environment is not set')
    sys.exit(-1)
path=os.getenv('PATH').split(':')
dest = ''
for p in path:
    if omnet_release in p:
        dest=p
files = []
for (dirpath, dirnames, filenames) in os.walk(src):
    files.extend(filenames)
    break

for f in files:
    sourcefile=src + '/' + f
    destfile=dest + '/' + f
    if os.path.islink(destfile):
        print('removing '+ destfile)
        os.unlink(destfile)
    print(sourcefile + ' ->\t' + destfile)
    os.symlink(sourcefile, destfile)
