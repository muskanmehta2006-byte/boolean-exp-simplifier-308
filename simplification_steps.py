from minimizer import bits

def build_explanation(vars_, ones, zeros, sop_trace, pos_trace):
    out=[]
    out.append(("1. Variable order",f"Variables are ordered as {', '.join(vars_)}. The leftmost variable is the most significant bit when indexing rows."))
    out.append(("2. Minterms and maxterms",f"Rows where F=1 are minterms: {', '.join('m'+str(x) for x in ones) if ones else 'none'}. Rows where F=0 are maxterms: {', '.join('M'+str(x) for x in zeros) if zeros else 'none'}."))
    out.append(("3. Binary representation","Each decimal row index is written in binary using the variable order above:\n"+("\n".join(f"m{x}: {bits(x,len(vars_))}" for x in ones) if ones else "There are no minterms.")))
    out.append(("4. SOP Quine–McCluskey rounds","The algorithm groups terms by the number of 1s, then combines terms differing in exactly one bit. A dash represents a bit that can be either 0 or 1.\n\n"+"\n\n".join(x["title"]+":\n"+x["detail"] for x in sop_trace)))
    out.append(("5. POS minimization","POS is obtained by minimizing the zero rows (the complement function) and complementing each selected implicant into a sum clause.\n\n"+"\n\n".join(x["title"]+":\n"+x["detail"] for x in pos_trace)))
    out.append(("6. Boolean laws used","The binary-combination step uses the complement/distributive identity: X·Y + X·Y' = X. In a combined implicant, the changing variable disappears. The resulting cover removes redundant terms. Equivalent familiar laws include idempotent law (X+X=X), absorption (X+XY=X), identity (X+0=X, X·1=X), null law (X+1=1, X·0=0), and De Morgan's theorem for complements."))
    return out
