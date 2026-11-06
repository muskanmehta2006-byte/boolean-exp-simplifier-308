def kmap_grid(vars_, values):
    """Return Gray-code ordered K-map labels and values for 2, 3, or 4 vars."""
    n=len(vars_)
    if n not in (2,3,4): return None
    gray=["00","01","11","10"]
    if n==2: row_codes=["0","1"]; col_codes=["0","1"]
    elif n==3: row_codes=["0","1"]; col_codes=gray[:]
    else: row_codes=gray[:]; col_codes=gray[:]
    grid=[]
    for r in row_codes:
        row=[]
        for c in col_codes:
            b=r+c
            row.append(values[int(b,2)])
        grid.append(row)
    return row_codes,col_codes,grid
