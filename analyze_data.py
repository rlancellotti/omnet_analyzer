#!/usr/bin/python3
# analyze_data V2.0
import argparse
import pathlib
import json
import sqlite3
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', help='.json file, Default config.json')
parser.add_argument('-d', '--db', help='database file, Default test.db')
parser.add_argument('-v', '--verbose', action='store_true', help='verbose operation')

#parser.add_argument('-n', '--no-header', dest='noheader', const=True, default=False, action='store_const', help='do not print header')
args = parser.parse_args()

def load_config(configname):
    with open(configname) as f:
        return json.load(f)

def aggregate_scenarios(sceanrios):
    rv = {}
    for s in sceanrios:
        name=s[1]
        run=s[2]
        scenario_id=s[0]
        if not name in rv:
            rv[name]={'sceanrio_ids': [scenario_id], 'runs': [run], 'params': list(s[3:])}
        else:
            rv[name]['sceanrio_ids'].append(scenario_id)
            rv[name]['runs'].append(run)
    return rv

def get_scenarios(conn, scenarios):
    c = conn.cursor()
    range_params = scenarios.get("range", [])
    fixed_params = scenarios["fixed"]
    where_clause = None
    for p in fixed_params:
        where_clause = "%s AND %s = '%s'" % (where_clause, p, fixed_params[p]) if where_clause is not None else "%s = '%s'" % (p, fixed_params[p])
    extract_clause = None
    for p in range_params:
        extract_clause = "%s, %s" % (extract_clause, p) if extract_clause is not None else "%s" % (p)
    # print(extract_clause)
    if where_clause is not None:
        query = ''' SELECT rowid, name, run%s FROM scenario WHERE %s %s ''' % (', ' + extract_clause if extract_clause is not None else '',
                                                                where_clause, 'ORDER BY ' + extract_clause if extract_clause is not None else '')
    else:
        query = ''' SELECT rowid, name, run%s FROM scenario %s ''' % (', ' + extract_clause if extract_clause is not None else '', 
                                                                'ORDER BY ' + extract_clause if extract_clause is not None else '')
    #print(query)
    c.execute(query)
    rv = aggregate_scenarios(c.fetchall())
    # print(rv)
    return rv

def get_values(conn, scenario_ids, metrics):
    # print(scenario_id)
    c = conn.cursor()
    rv = []
    for m in metrics:
        samples=[]
        for sid in scenario_ids:
            query = ''' SELECT value FROM value WHERE scenarioid = '%s' AND metric = '%s' AND aggregation = '%s' ''' % (sid, m["metric"], m["aggr"])
            #print(query)
            c.execute(query)
            try:
                samples.append(float(c.fetchone()[0]))
            except :
                print('exception when parsing result of this query: '+ query)
        mean=np.mean(samples)
        sigma=np.std(samples)
        rv.append(mean)
        rv.append(sigma)
    return rv

def do_analysis(conn, analysis):
    # print(analysis, type(analysis))
    outfile = analysis.get("outfile")
    pathlib.Path(outfile).parent.mkdir(parents=True, exist_ok=True)
    f = open(outfile, "w")
    scenarios = get_scenarios(conn, analysis["scenarios"])
    header = None
    for p in analysis["scenarios"]["range"]:
        header = "%s\t%s" % (header, p) if header is not None else "# %s" % (p)
    for m in analysis["metrics"]:
        if m["aggr"]!='none':
            header = "%s\t%s(%s)\tsigma(%s(%s))" % (header, m["aggr"], m["metric"], m["aggr"], m["metric"]) 
        else:
            header =  "%s\t%s\tsigma(%s)" % (header, m["metric"], m["metric"])
    f.write("%s\n" % header)
    # print(header)
    for s in scenarios:
        # print(scenarios[s]['sceanrio_ids'])
        val = get_values(conn, scenarios[s]['sceanrio_ids'], analysis["metrics"])
        out = None
        for v in scenarios[s]['params'] + val:
            out = "%s\t%s" % (out, v) if out is not None else "%s" % (v)
        f.write("%s\n" % out)
        # print(out)
    f.close()

def get_bins(conn, sid, histogram_name):
    c = conn.cursor()
    query = ''' SELECT bins FROM histogram WHERE scenarioid = '%s' AND histogram = '%s' ''' % (sid, histogram_name)
    #print(query)
    c.execute(query)
    bins=json.loads(c.fetchone()[0])
    return bins

def do_histogram(conn, analysis):
    #print('histogram: '+ str(analysis))
    outfile = analysis.get("outfile")
    pathlib.Path(outfile).parent.mkdir(parents=True, exist_ok=True)
    scenarios = get_scenarios(conn, {'fixed': analysis['scenario']})
    for s in scenarios:
        sid=scenarios[s]['sceanrio_ids'][0]
        #print(sid)
        bins = get_bins(conn, sid, analysis['histogram'])
        #print(bins)
        with open(outfile, "w") as f:
            f.write('#value\tsamples\n')
            for r in bins:
                f.write('%f\t%f\n' %(r['value'], r['samples']))
    return None


configname = args.config if args.config else "config.json"
dbname = args.db if args.db else "test.db"
config = load_config(configname)
conn = sqlite3.connect(dbname)
analyses = config["analyses"]
if args.verbose:
    print("Analyzing data from %s using config %s" %(dbname, configname))
for a in analyses:
    if args.verbose:
        print(a)
    if analyses[a].get('metrics'):
        do_analysis(conn, analyses[a])
    if analyses[a].get('histogram'):
        do_histogram(conn, analyses[a])    

#"analyses": {
#        "test1": {
#            "outfile": "test1.data",
#            "scenarios": {
#                "fixed": {"NA": "5", "NB": "45", "muA": "1.0", "muB": "1.0", "thetaA": "1"},
#                "range": ["thetaB"]
#            },
#            "metrics": [
#                {"metric": "DropJ", "aggr": "avg"},
#                {"metric": "TotJ", "aggr": "avg"}
#            ]
#        }
#    }