# Boolean Expression Simplifier Dashboard

An educational Streamlit application that accepts Boolean expressions, generates minimal SOP and POS forms using a transparent Quine–McCluskey implementation, and shows truth tables, minimization traces and Gray-code K-map values.

## Features
- Operators: AND `*`, `&`, or adjacency; OR `+`, `|`; NOT `'`, `!`, `~`
- Parentheses and nested expressions
- Up to four variables
- Minimal SOP and POS
- Minterm/maxterm listing, binary conversion, combination rounds, prime implicants and minimum cover
- Truth table and 2/3/4-variable K-map grid
- Truth-table equivalence check

## Run locally
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud
1. Create a public GitHub repository and upload all project files.
2. Open https://share.streamlit.io/ and sign in with GitHub.
3. Choose the repository, branch, and `app.py` as the main file.
4. Deploy. Streamlit will install packages from `requirements.txt`.

## Run tests
```bash
pip install pytest
pytest -q
```

## Input examples
- `A'B + AB`
- `~A & (B + C)`
- `A(B+C)`
- `(A+B)(A'+C)`

## Notes and scope
- Variable names are sorted alphabetically for a stable truth-table bit order.
- The Quine–McCluskey search is practical for the supported maximum of four variables.
- K-map cells use Gray-code ordering. The dashboard lists implicant patterns that correspond to groups; it does not draw colored group loops over the cells.
- `sympy` is included as a dependency for future symbolic cross-checking; the primary minimization and teaching trace are implemented directly in `minimizer.py`.
- If multiple equally minimal covers exist, the app uses a deterministic tie-break.
