import sys, os, itertools
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
from boolean_parser import parse_expression, variables, evaluate
from minimizer import qm_minimize, sop_to_pos_from_zeros

def test_cases():
    samples=["A'B + AB","A + A'","AB + AB'","(A+B)(A'+B)","A+A","A*0","A+1","A'B'C + AB'C"]
    for source in samples:
        ast=parse_expression(source)
        vs=sorted(variables(ast))
        assert len(vs)<=4
        ones=[]; zeros=[]
        for i,combo in enumerate(itertools.product([0,1],repeat=len(vs))):
            if evaluate(ast,dict(zip(vs,combo))): ones.append(i)
            else: zeros.append(i)
        sop, selected, _=qm_minimize(ones,len(vs),vs)
        pos, psel, _=sop_to_pos_from_zeros(zeros,len(vs),vs)
        for i,combo in enumerate(itertools.product([0,1],repeat=len(vs))):
            b=format(i,f"0{len(vs)}b")
            got=int(any(all(p[j]=="-" or p[j]==b[j] for j in range(len(vs))) for p in selected))
            assert got==int(evaluate(ast,dict(zip(vs,combo)))), (source,sop,i)


def test_constants_and_kmap():
    from kmap import kmap_grid
    for source, expected in [("A*0",0),("A+1",1),("0",0),("1",1)]:
        ast=parse_expression(source)
        assert int(evaluate(ast,{"A":0} if variables(ast) else {}))==expected
    _,_,g=kmap_grid(["A","B"],[0,1,1,0])
    assert len(g)==2 and len(g[0])==2
