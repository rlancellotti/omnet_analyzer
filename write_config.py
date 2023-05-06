#!/usr/bin/python3
import argparse
import yaml
import os
import re
parser = argparse.ArgumentParser()
parser.add_argument('-r', '--reset', action='store_true', help='re-create file')
parser.add_argument('-f', '--file', help='file to work on')
parser.add_argument('-k', '--key', help='key to add')
parser.add_argument('-v', '--value', help='value to associate to the key')
args = parser.parse_args()

fname = args.file
    
if args.reset or not os.path.isfile(fname):
    data={}
else:
    with open(fname, 'r') as f:
        data=yaml.load(f, Loader=yaml.FullLoader)

v=args.value
if re.search('\[.+\]', v):
    v=v.translate({ord('['): None, ord(']'): None, ord(' '): None})
    v=v.split(',')

data[args.key] = v

with open(fname, 'w') as f:
    yaml.dump(data, f)

    

