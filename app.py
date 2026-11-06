
import streamlit as st
import pandas as pd

from boolean_parser import (
    parse_expression,
    variables,
    evaluate,
    BooleanExpressionError
)
from minimizer import qm_minimize, sop_to_pos_from_zeros
from truth_table import make_truth_table
from simplification_steps import build_explanation
from kmap import kmap_grid


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Boolean Expression Simplifier",
    page_icon="⚡",
    layout="wide"
)


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>

.block-container {
    padding-top: 2rem;
    max-width: 1250px;
}

.hero {
    padding: 1.5rem 1.7rem;
    border-radius: 18px;
    background: linear-gradient(120deg, #10243b, #174e63);
    color: white;
    margin-bottom: 1rem;
}

.hero h1 {
    color: white;
    margin: 0;
}

.hero p {
    color: #d9e8ef;
    margin-top: 0.4rem;
}

.metric-card {
    padding: 1rem;
    border: 1px solid rgba(128,128,128,0.3);
    border-radius: 14px;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown("""
<div class="hero">
    <h1>⚡ Boolean Expression Simplifier</h1>
    <p>
        An interactive educational tool for Boolean minimization
        using the Quine-McCluskey algorithm.
    </p>
</div>
""", unsafe_allow_html=True)

st.caption(
    "Digital Electronics | Boolean Algebra | Logic Circuit Design"
)


# --------------------------------------------------
# INSTRUCTIONS
# --------------------------------------------------

with st.expander("How to enter a Boolean Expression", expanded=True):

    st.markdown("""
    **Supported Boolean operators:**

    | Operation | Symbols | Example |
    |---|---|---|
    | AND | `*`, `&`, adjacency | `A*B`, `AB` |
    | OR | `+`, `|` | `A+B` |
    | NOT | `'`, `!`, `~` | `A'`, `!A` |

    Parentheses and nested expressions are supported.

    **Examples:**

    - `A'B + AB`
    - `~A & (B + C)`
    - `A*(B+C)`
    - `(A+B)(A'+C)`

    This version supports a maximum of four variables.
    """)


# --------------------------------------------------
# INPUT
# --------------------------------------------------

expression = st.text_input(
    "Enter your Boolean Expression",
    value="A'B + AB",
    placeholder="Example: A'B + AB"
)

simplify_button = st.button(
    "⚡ Simplify Expression",
    type="primary",
    use_container_width=True
)


# --------------------------------------------------
# HELPER: VERIFY SOP EQUIVALENCE
# --------------------------------------------------

def verify_equivalence(ast, selected, var_names):

    from itertools import product

    for combination in product([0, 1], repeat=len(var_names)):

        values = dict(zip(var_names, combination))

        original_output = int(evaluate(ast, values))

        binary = format(
            sum(
                values[var] << (len(var_names) - 1 - i)
                for i, var in enumerate(var_names)
            ),
            f"0{len(var_names)}b"
        ) if var_names else ""

        simplified_output = int(
            any(
                all(
                    pattern[j] == "-" or pattern[j] == binary[j]
                    for j in range(len(var_names))
                )
                for pattern in selected
            )
        ) if selected else 0

        if original_output != simplified_output:
            return False

    return True


# --------------------------------------------------
# HELPER: CONVERT SOP TO LATEX
# --------------------------------------------------

def format_boolean(expression):

    if expression in ("0", "1"):
        return expression

    result = ""

    for char in expression:

        if char == "'":
            result += r"^{\prime}"

        elif char == "+":
            result += r" + "

        elif char == "(":
            result += r"\left("

        elif char == ")":
            result += r"\right)"

        else:
            result += char

    return result


# --------------------------------------------------
# MAIN SIMPLIFICATION
# --------------------------------------------------

if simplify_button:

    try:

        # Parse expression
        ast = parse_expression(expression)

        # Identify variables
        var_names = sorted(variables(ast))

        if len(var_names) > 4:

            raise BooleanExpressionError(
                "Maximum four variables are supported."
            )

        # Generate truth table
        if var_names:

            table = make_truth_table(ast, var_names)

            ones = [
                i for i, value in enumerate(table["F"])
                if value == 1
            ]

            zeros = [
                i for i, value in enumerate(table["F"])
                if value == 0
            ]

            # Quine-McCluskey SOP
            sop, sop_selected, sop_trace = qm_minimize(
                ones,
                len(var_names),
                var_names
            )

            # Quine-McCluskey POS
            pos, pos_selected, pos_trace = sop_to_pos_from_zeros(
                zeros,
                len(var_names),
                var_names
            )

        else:

            # Constant expression
            result = int(evaluate(ast, {}))

            table = pd.DataFrame([{"F": result}])

            ones = [0] if result else []
            zeros = [] if result else [0]

            sop = str(result)
            pos = str(result)

            sop_selected = []
            pos_selected = []

            sop_trace = [{
                "title": "Constant function",
                "detail": f"The expression evaluates to {result}."
            }]

            pos_trace = sop_trace

        # Verify mathematical equivalence
        equivalent = verify_equivalence(
            ast,
            sop_selected,
            var_names
        ) if var_names else True

        # Save results
        st.session_state["result"] = {

            "expression": expression,
            "variables": var_names,
            "table": table,

            "ones": ones,
            "zeros": zeros,

            "sop": sop,
            "pos": pos,

            "sop_selected": sop_selected,
            "pos_selected": pos_selected,

            "sop_trace": sop_trace,
            "pos_trace": pos_trace,

            "ast": ast,
            "equivalent": equivalent
        }

    except BooleanExpressionError as error:

        st.error(f"Invalid Boolean Expression: {error}")

        st.session_state.pop("result", None)

    except Exception as error:

        st.error(f"An unexpected error occurred: {error}")

        st.session_state.pop("result", None)


# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

if "result" in st.session_state:

    data = st.session_state["result"]

    st.divider()

    st.header("Simplification Results")

    # SOP AND POS CARDS

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### Minimal SOP")

        st.success(data["sop"])

        st.caption("Sum of Products")

    with col2:

        st.markdown("### Minimal POS")

        st.success(data["pos"])

        st.caption("Product of Sums")

    # Verification

    if data["equivalent"]:

        st.success(
            "✓ Verification Passed: Original and simplified expressions "
            "produce identical outputs for every input combination."
        )

    else:

        st.error(
            "Verification failed. Please inspect the minimization result."
        )

    st.info(
        f"Variables: {len(data['variables'])} | "
        f"Minterms: {len(data['ones'])} | "
        f"Maxterms: {len(data['zeros'])}"
    )

    # --------------------------------------------------
    # TABS
    # --------------------------------------------------

    tab1, tab2, tab3, tab4, tab5 = st.tabs([

        "Simplified Expression",
        "Step-by-Step Explanation",
        "Truth Table",
        "Karnaugh Map",
        "Algorithm Details"

    ])


    # ==================================================
    # TAB 1: SIMPLIFIED EXPRESSION
    # ==================================================

    with tab1:

        st.subheader("Minimal Boolean Expressions")

        st.markdown("#### Sum of Products (SOP)")

        st.latex(
            "F = " + format_boolean(data["sop"])
        )

        st.write(
            "**Selected SOP implicants:**",
            ", ".join(data["sop_selected"]) or "None"
        )

        st.divider()

        st.markdown("#### Product of Sums (POS)")

        st.latex(
            "F = " + format_boolean(data["pos"])
        )

        st.write(
            "**Selected POS implicants:**",
            ", ".join(data["pos_selected"]) or "None"
        )

        st.divider()

        st.markdown("#### Original Expression")

        st.code(data["expression"])

        st.markdown("#### Summary")

        st.write(
            f"Number of variables: {len(data['variables'])}"
        )

        st.write(
            f"Minterms: {data['ones']}"
        )

        st.write(
            f"Maxterms: {data['zeros']}"
        )


    # ==================================================
    # TAB 2: STEP BY STEP EXPLANATION
    # ==================================================

    with tab2:

        st.subheader("How Was The Expression Simplified?")

        steps = build_explanation(
            data["variables"],
            data["ones"],
            data["zeros"],
            data["sop_trace"],
            data["pos_trace"]
        )

        for title, explanation in steps:

            with st.expander(title, expanded=True):

                st.text(explanation)

        st.divider()

        st.subheader("Important Boolean Algebra Laws")

        laws = {

            "Complement Law":
                "A + A' = 1 and A · A' = 0",

            "Identity Law":
                "A + 0 = A and A · 1 = A",

            "Null Law":
                "A + 1 = 1 and A · 0 = 0",

            "Idempotent Law":
                "A + A = A and A · A = A",

            "Absorption Law":
                "A + AB = A",

            "Distributive Law":
                "A(B+C) = AB+AC",

            "De Morgan's Theorem":
                "(AB)' = A' + B'"

        }

        for law, formula in laws.items():

            st.markdown(f"**{law}**")

            st.latex(formula)


    # ==================================================
    # TAB 3: TRUTH TABLE
    # ==================================================

    with tab3:

        st.subheader("Truth Table")

        st.write(
            "The truth table shows the output for every possible "
            "combination of input variables."
        )

        # FIXED PANDAS STYLING
        # Using Styler.apply instead of deprecated applymap.

        def highlight_output(column):

            return [
                (
                    "background-color: #d9f2df; color: #14532d"
                    if value == 1
                    else "background-color: #fde2e2; color: #7f1d1d"
                )
                for value in column
            ]

        styled_table = (
            data["table"]
            .style
            .apply(highlight_output, subset=["F"])
        )

        st.dataframe(
            styled_table,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        col1, col2 = st.columns(2)

        with col1:

            st.markdown("### Minterms")

            st.write(
                ", ".join(map(str, data["ones"])) or "None"
            )

            st.caption("Rows where output F = 1")

        with col2:

            st.markdown("### Maxterms")

            st.write(
                ", ".join(map(str, data["zeros"])) or "None"
            )

            st.caption("Rows where output F = 0")


    # ==================================================
    # TAB 4: KARNAUGH MAP
    # ==================================================

    with tab4:

        st.subheader("Karnaugh Map Visualization")

        n = len(data["variables"])

        if n in (2, 3, 4):

            st.write(
                "K-map cells are arranged in Gray-code order. "
                "Adjacent cells differ in exactly one variable."
            )

            row_codes, col_codes, grid = kmap_grid(
                data["variables"],
                [int(value) for value in data["table"]["F"]]
            )

            if n == 2:

                row_labels = ["0", "1"]

            elif n == 3:

                row_labels = ["0", "1"]

            else:

                row_labels = ["00", "01", "11", "10"]

            col_labels = (
                ["0", "1"] if n == 2
                else ["00", "01", "11", "10"]
            )

            kmap_df = pd.DataFrame(
                grid,
                index=row_labels,
                columns=col_labels
            )

            st.markdown("#### K-map Values")

            st.dataframe(
                kmap_df,
                use_container_width=True
            )

            st.divider()

            st.markdown("#### SOP Groups (1-groups)")

            st.write(
                ", ".join(data["sop_selected"]) or "No 1-groups"
            )

            st.markdown("#### POS Groups (0-groups)")

            st.write(
                ", ".join(data["pos_selected"]) or "No 0-groups"
            )

            st.info(
                "A dash (-) in an implicant means that the "
                "corresponding variable is eliminated because "
                "it changes within that group."
            )

        else:

            st.info(
                "Karnaugh maps are available for expressions "
                "containing 2, 3 or 4 variables."
            )


    # ==================================================
    # TAB 5: ALGORITHM DETAILS
    # ==================================================

    with tab5:

        st.subheader("Quine-McCluskey Minimization Algorithm")

        st.write(
            "The Quine-McCluskey algorithm is a systematic "
            "tabular method used to minimize Boolean expressions."
        )

        algorithm_steps = [

            (
                "Step 1: Identify Minterms",
                "Find all truth table rows where the output is 1."
            ),

            (
                "Step 2: Binary Conversion",
                "Convert every minterm index into binary representation."
            ),

            (
                "Step 3: Grouping",
                "Group binary terms according to the number of 1s."
            ),

            (
                "Step 4: Combination",
                "Combine terms differing in exactly one bit position."
            ),

            (
                "Step 5: Prime Implicants",
                "Terms that cannot be combined further are prime implicants."
            ),

            (
                "Step 6: Prime Implicant Chart",
                "Identify which prime implicants cover each minterm."
            ),

            (
                "Step 7: Essential Prime Implicants",
                "Select implicants that uniquely cover at least one minterm."
            ),

            (
                "Step 8: Minimum Cover",
                "Select a minimum collection of implicants covering all minterms."
            ),

            (
                "Step 9: Final Expression",
                "Convert the selected binary patterns into Boolean literals."
            )

        ]

        for heading, description in algorithm_steps:

            with st.expander(heading):

                st.write(description)

        st.divider()

        st.subheader("Complexity and Scope")

        st.write("""
        - The implementation supports up to four variables.
        - The Quine-McCluskey method systematically generates
          prime implicants.
        - A minimum cover is selected by comparing term and
          literal counts.
        - Multiple equally minimal solutions may exist.
        """)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.markdown("""
<center>

**Boolean Expression Simplifier Dashboard**

Built using Python | Streamlit | Pandas | SymPy

Digital Electronics Mini Project

</center>
""", unsafe_allow_html=True)
