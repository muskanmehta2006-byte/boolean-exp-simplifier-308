"""Tokenizer and recursive-descent parser for Boolean expressions.

Supported: A-Z identifiers, 0/1 constants, AND (*, &, adjacency),
OR (+, |), NOT (!, ~, postfix apostrophe), and parentheses.
Precedence: NOT > AND > OR.
"""
import re

class BooleanExpressionError(ValueError):
    pass

TOKEN_RE = re.compile(r"\s*([A-Za-z][A-Za-z0-9_]*|[01]|[()+*&|!'~])")

def tokenize(source):
    if not isinstance(source, str) or not source.strip():
        raise BooleanExpressionError("Enter a Boolean expression first.")
    tokens, pos = [], 0
    while pos < len(source):
        m = TOKEN_RE.match(source, pos)
        if not m:
            raise BooleanExpressionError(f"Unexpected character {source[pos]!r} at position {pos+1}.")
        tokens.append(m.group(1))
        pos = m.end()
    # Insert implicit AND between a completed operand and a new operand.
    out=[]
    ends_operand=lambda t: bool(re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*|[01]|\)",t)) or t=="'"
    starts_operand=lambda t: bool(re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*|[01]|\(",t)) or t in ("!","~")
    for i,t in enumerate(tokens):
        if out and ends_operand(out[-1]) and starts_operand(t):
            out.append("*")
        out.append(t)
    return out

class Parser:
    def __init__(self, tokens):
        self.t=tokens; self.i=0
    def peek(self): return self.t[self.i] if self.i<len(self.t) else None
    def take(self):
        x=self.peek()
        if x is not None: self.i+=1
        return x
    def parse(self):
        node=self.parse_or()
        if self.peek() is not None:
            raise BooleanExpressionError(f"Unexpected token {self.peek()!r}. Check operators and parentheses.")
        return node
    def parse_or(self):
        n=self.parse_and()
        while self.peek() in ("+","|"):
            self.take(); n=("or",n,self.parse_and())
        return n
    def parse_and(self):
        n=self.parse_unary()
        while self.peek() in ("*","&"):
            self.take(); n=("and",n,self.parse_unary())
        return n
    def parse_unary(self):
        if self.peek() in ("!","~"):
            self.take(); return ("not",self.parse_unary())
        n=self.parse_atom()
        while self.peek()=="'":
            self.take(); n=("not",n)
        return n
    def parse_atom(self):
        x=self.take()
        if x is None: raise BooleanExpressionError("Expression ends unexpectedly.")
        if x=="(":
            n=self.parse_or()
            if self.take()!=")": raise BooleanExpressionError("Missing closing parenthesis ')'.")
            return n
        if x in ("+","|","*","&",")","'"):
            raise BooleanExpressionError(f"Unexpected operator {x!r}.")
        if x in ("0","1"): return ("const",int(x))
        if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*",x): return ("var",x)
        raise BooleanExpressionError(f"Invalid token {x!r}.")

def parse_expression(source):
    return Parser(tokenize(source)).parse()

def variables(node):
    if node[0]=="var": return {node[1]}
    if node[0]=="const": return set()
    if node[0]=="not": return variables(node[1])
    return variables(node[1]) | variables(node[2])

def evaluate(node, values):
    op=node[0]
    if op=="const": return bool(node[1])
    if op=="var": return bool(values[node[1]])
    if op=="not": return not evaluate(node[1],values)
    if op=="and": return evaluate(node[1],values) and evaluate(node[2],values)
    if op=="or": return evaluate(node[1],values) or evaluate(node[2],values)
    raise ValueError("Unknown AST node")
