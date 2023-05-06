#!/usr/bin/python3
import argparse
import sqlite3

def print_output(v):
    print('\t'.join([str(x) for x in v]))

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--db', help='database file, Default iot.db')
parser.add_argument('-s', '--scenario', help='default scenario, Default fog_polimi')
parser.add_argument('-m', '--nometrics', action='store_true', help='do not print metric names')
args = parser.parse_args()
dbname = args.db if args.db else "iot.db"
scenario = args.sceanrio if args.scenario else 'fog_polimi'
conn = sqlite3.connect(dbname)
# get list of sceanrios
cursor = conn.execute(f'select rowid from scenario where name="{scenario}"')
scenario_ids=[s[0] for s in cursor.fetchall()]
#print(scenario_ids) 
first=not args.nometrics
for sid in scenario_ids:
    cursor = conn.execute(f'select metric, value from value where scenarioid="{sid}" and aggregation="none" and metric like "FogTSrv-%"')
    res=[v for v in cursor.fetchall()]
    if first:
        print_output(['scenario'] + [v[0] for v in res])
        first=False
    values=[sid] + [v[1] for v in res]
    print_output(values)


