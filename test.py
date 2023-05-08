#!/usr/bin/python3
import yaml
import re
import subprocess
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', help='file with test specification. Degault test.yaml')
args = parser.parse_args()

testfile=args.file if args.file is not None else 'test.yaml'


(TEST_OK, TEST_FAIL, TEST_ERR)=('OK', 'FAIL', 'ERROR')
output_key={TEST_OK: '.', TEST_FAIL: 'F', TEST_ERR: 'E'}

def expand_env(s, env):
    if type(s) == str:
        for v in env:
            s = re.sub('\$\{%s\}'%v, str(env[v]), s)
    else:
        s=str(s)
    return s

def execute_command(cmd, env, loghandle=None):
    cmd=expand_env(cmd, env)
    rv=subprocess.run(["/bin/bash", "-c", cmd], capture_output=True)
    if loghandle is not None:
        loghandle.write('--- COMMAND\n')
        loghandle.write(f'{cmd} -> {rv.returncode}\n')
        if len(rv.stdout) > 0:
            loghandle.write('--- STDOUT\n')
            loghandle.write(rv.stdout.decode('utf-8'))
        if len(rv.stderr) > 0:
            loghandle.write('--- STDERR\n')
            loghandle.write(rv.stderr.decode('utf-8'))
    return rv.returncode

def execute_assertion(cmd, env, loghandle=None):
    rv=execute_command(cmd, env, loghandle=loghandle)
    if rv==0: return TEST_OK
    if rv==1: return TEST_FAIL
    if rv==255 or rv==2: return TEST_ERR

def test_has_errors(stats):
    return stats[TEST_FAIL] > 0 or stats[TEST_ERR] > 0

def execute_test(tname, tconf, globalenv=None):
    #print(f'executing test {tname}')
    env={'testname': tname} | tconf['env']
    if globalenv is not None:
        env=globalenv | env
    # expand environment in environment itself
    for ek in env.keys():
        env[ek]=expand_env(env[ek], env)
    # setup logging
    if 'log' in tconf.keys():
        if 'name' in tconf['log']:
            logname = expand_env(tconf['log']['name'], env)
        else : logname = f'{tname}.log'
        if 'persist' in tconf['log']:
            logpersist = tconf['log']['persist']
        else: logpersist = False
    else:
        logname = f'{tname}.log'
        logpersist = False
    with open(logname, 'w') as log_handle:
        # Execute commands
        for c in tconf['commands']:
            rv = execute_command(c, env, loghandle=log_handle)
            if rv != 0: 
                return [], {TEST_OK: 0, TEST_FAIL:0, TEST_ERR: 1}
        log=[]
        # Execute assertions
        for ass in tconf['expect']:
            x=execute_assertion(ass, env, loghandle=log_handle)
            log.append(x)
    stats=get_stats(log)
    if not logpersist and not test_has_errors(stats):
        os.remove(logname)
    return log, stats

def get_stats(log: list):
    stats={TEST_OK: 0, TEST_FAIL: 0, TEST_ERR: 0}
    for t in log:
        if t == TEST_ERR: stats[TEST_ERR] += 1
        if t == TEST_FAIL: stats[TEST_FAIL] += 1
        if t == TEST_OK: stats[TEST_OK] += 1
    return stats

def format_test_output(name, log, stats):
    l=''
    for t in log:
        l=f'{l}{output_key[t]}'
    return f'{name}: {l} ({format_stats(stats)})'

def format_stats(stats):
    return f'{TEST_OK}: {stats[TEST_OK]}, {TEST_FAIL}: {stats[TEST_FAIL]}, {TEST_ERR}: {stats[TEST_ERR]}'

with open(testfile, 'r') as f:
    conf=yaml.load(f, Loader=yaml.FullLoader)
    stats={}
    summary=[]
    if 'env' in conf.keys():
        env=conf['env']
        # expand environment in environment itself
        for ek in env.keys():
            env[ek]=expand_env(env[ek], env)
    else: env=None
    for test in conf:
        if test != 'env':
            (log, st)=execute_test(test, conf[test], globalenv=env)
            s=format_test_output(test, log, st)
            print(s)
            summary.append(s)
            for rvk in st.keys():
                if rvk in stats.keys(): stats[rvk] += st[rvk]
                else: stats[rvk] = st[rvk]
    #for s in summary: print(s)
    print(f'Global stats: {format_stats(stats)}')
