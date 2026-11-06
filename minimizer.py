"""Quine-McCluskey minimizer for up to four variables."""
from itertools import combinations

def bits(n, width): return format(n, f"0{width}b")

def combine(a,b):
    diff=[i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
    if len(diff)==1 and a[diff[0]]!="-" and b[diff[0]]!="-":
        i=diff[0]
        return a[:i]+"-"+a[i+1:]
    return None

def covers(pattern, n):
    s=bits(n,len(pattern))
    return all(p=="-" or p==x for p,x in zip(pattern,s))

def qm_minimize(minterms, nvars, variable_names):
    """Return minimum SOP text, selected implicants, and an auditable trace."""
    minterms=sorted(set(minterms))
    width=nvars
    trace=[]
    if not minterms:
        return "0", [], [{"title":"No minterms","detail":"The function is 0 for every input."}]
    if len(minterms)==2**width:
        return "1", ["-"*width], [{"title":"All minterms are present","detail":"Every input combination produces 1, so the function is constant 1."}]
    current={bits(m,width):{m} for m in minterms}
    prime=set()
    round_no=1
    while current:
        groups={}
        for pat, covered in current.items():
            groups.setdefault(pat.count("1"),[]).append((pat,covered))
        combined={}
        used=set()
        pair_lines=[]
        keys=sorted(groups)
        for k in keys:
            for pa,ca in groups.get(k,[]):
                for pb,cb in groups.get(k+1,[]):
                    merged=combine(pa,pb)
                    if merged is not None:
                        used.add(pa); used.add(pb)
                        combined.setdefault(merged,set()).update(ca|cb)
                        pair_lines.append(f"{pa} + {pb} → {merged}")
        for pat in current:
            if pat not in used: prime.add(pat)
        trace.append({"title":f"Combination round {round_no}",
                      "detail":("Terms combined:\n"+"\n".join(pair_lines)) if pair_lines else "No further pair differs in exactly one bit; remaining terms are prime implicants.",
                      "groups":{str(k):[p for p,_ in v] for k,v in groups.items()}})
        current=combined
        round_no+=1
    # Prime implicant chart: each prime covers a subset of ON-set.
    primes=sorted(prime)
    chart={m:[p for p in primes if covers(p,m)] for m in minterms}
    essential={ps[0] for m,ps in chart.items() if len(ps)==1}
    # Exact minimum cover: enumerate subsets; 4 variables means at most 16 minterms.
    remaining=set(minterms)
    best=None
    candidates=[p for p in primes if p not in essential]
    for r in range(len(candidates)+1):
        for subset in combinations(candidates,r):
            chosen=set(essential)|set(subset)
            covered={m for m in minterms if any(covers(p,m) for p in chosen)}
            if covered==remaining:
                # Prefer fewer terms, then fewer literals, then stable lexical order.
                score=(len(chosen),sum(p.count("0")+p.count("1") for p in chosen),tuple(sorted(chosen)))
                if best is None or score<best[0]: best=(score,chosen)
        if best is not None: break
    selected=sorted(best[1] if best else essential)
    trace.append({"title":"Prime implicant chart",
                  "detail":"Coverage by prime implicants:\n"+"\n".join(f"m{m}: {', '.join(chart[m])}" for m in minterms)})
    trace.append({"title":"Essential prime implicants and minimum cover",
                  "detail":f"Essential implicants: {', '.join(sorted(essential)) if essential else 'None'}\nSelected minimum cover: {', '.join(selected)}"})
    def term(p):
        lits=[]
        for bit,var in zip(p,variable_names):
            if bit=="1": lits.append(var)
            elif bit=="0": lits.append(var+"'")
        return "".join(lits) if lits else "1"
    expression=" + ".join(term(p) for p in selected) or "0"
    return expression, selected, trace

def implicant_to_sop(pattern, variable_names):
    lits=[]
    for bit,var in zip(pattern,variable_names):
        if bit=="1": lits.append(var)
        elif bit=="0": lits.append(var+"'")
    return "".join(lits) if lits else "1"

def sop_to_pos_from_zeros(zero_indices, nvars, variable_names):
    expr, selected, trace=qm_minimize(zero_indices,nvars,variable_names)
    if expr=="0": return "1", selected, trace
    if expr=="1": return "0", selected, trace
    # Complement of minimized SOP of F' gives POS of F.
    clauses=[]
    for p in selected:
        lits=[]
        for bit,var in zip(p,variable_names):
            if bit=="1": lits.append(var+"'")
            elif bit=="0": lits.append(var)
        clauses.append("("+" + ".join(lits)+")")
    return "".join(clauses), selected, trace
