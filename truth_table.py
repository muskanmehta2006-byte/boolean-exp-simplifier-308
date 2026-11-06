import pandas as pd
from itertools import product
from boolean_parser import evaluate

def make_truth_table(ast, vars_):
    rows=[]
    for combo in product([0,1], repeat=len(vars_)):
        values=dict(zip(vars_,combo))
        rows.append({**values,"F":int(evaluate(ast,values))})
    return pd.DataFrame(rows)
