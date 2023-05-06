#!/usr/bin/python3
import argparse
import pandas as pd
import numpy as np
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', help='tabular file to work on')
parser.add_argument('-a', '--aoperand', help='first opearand')
parser.add_argument('-b', '--boperand', help='second opearand')
parser.add_argument('-o', '--operation', help='operation')
parser.add_argument('-e', '--epsilon', help='tolerance, deault=0.05% of avg(a, b)')
args = parser.parse_args()

def get_operand(df, name):
    try:
        return float(name)
    except:
        if name in df.columns:
            return df.iloc[0][name]
        else: return None

def assertion_equal(a, b, eps):
    return abs(a-b)<eps

def assertion_a_less_than_b(a, b, eps):
    return a-b<eps

def assertion_result(a, b, op, eps):
    if op == 'eq':
        return assertion_equal(a, b, eps)
    if op == 'lt':
        return assertion_a_less_than_b(a, b, eps)
    if op == 'gt':
        return assertion_a_less_than_b(b, a, eps)

df = pd.read_csv(args.file, delim_whitespace=True)
a = get_operand(df, args.aoperand)
b = get_operand(df, args.boperand)
op = args.operation
if a is None or b is None or op is None:
    sys.exit(-1)
eps = float(args.epsilon) if args.epsilon is not None else 0.05
eps=np.mean([a, b])*eps
res=assertion_result(a, b, op, eps)
print(f'Assertion {a:.3f} {op} {b:.3f} +/-${eps:.3f} is {res}')
if res: sys.exit(0)
else: sys.exit(1)

