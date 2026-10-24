"""blocks.py -- the README's "Blocks?" column, read from the rules themselves.

  python docs/blocks.py                       # every rule
  python docs/blocks.py S1-SOFT-404 S2-ORPHAN # just these, in this order

Every place a finding is built (finding(...) in audit.py, the finding dicts in
schema_check.py) is read with ast, and each severity/confidence it can have is passed to
verify.blocks(). A rule built at more than one severity lists each one. A value that is a
literal, either side of a ternary, or a name bound by a `for` over a literal tuple of
tuples is resolved; anything else exits 1, naming the rule and the line, because a value
this script cannot read is not a value it may call "no".
"""
import ast
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "..", "scripts")
sys.path.insert(0, SCRIPTS)
from verify import blocks  # noqa: E402

# audit.py re-wraps schema_check.py's finding dicts, read at their source below
PASS_THROUGH = {("audit.py", "f['id']")}


def loop_bindings(tree):
    """{Call node: {name: [values]}} for names bound by `for a, b in ((...), ...)`.
    Values that are not string literals are left out, so they stay unresolved."""
    env = {}
    for loop in ast.walk(tree):
        if not (isinstance(loop, ast.For) and isinstance(loop.target, ast.Tuple)
                and isinstance(loop.iter, (ast.Tuple, ast.List))):
            continue
        names = [t.id if isinstance(t, ast.Name) else None for t in loop.target.elts]
        bound = {}
        for row in loop.iter.elts:
            if not (isinstance(row, ast.Tuple) and len(row.elts) == len(names)):
                bound = {}
                break
            for name, v in zip(names, row.elts):
                if name:
                    bound.setdefault(name, []).append(v)
        for node in ast.walk(loop):    # outer loops first, so an inner loop's names win
            if isinstance(node, ast.Call):
                env.setdefault(node, {}).update(bound)
    return env


def consts(node, env):
    """The string values an argument can take, or None if any of them is not a literal."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, ast.IfExp):
        a, b = consts(node.body, env), consts(node.orelse, env)
        return a + b if a is not None and b is not None else None
    if isinstance(node, ast.Name) and node.id in env:
        vals = [consts(v, env) for v in env[node.id]]
        return None if None in vals else sorted({x for v in vals for x in v})
    return None


def variants():
    """{rule: {(severity, confidence)}}; exits 1 on any value it cannot resolve."""
    out, bad = {}, []
    for name in ("audit.py", "schema_check.py"):
        with open(os.path.join(SCRIPTS, name), encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
        env = loop_bindings(tree)
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and getattr(node.func, "id", None) == "finding"
                    and len(node.args) >= 3):
                if (name, ast.unparse(node.args[0])) in PASS_THROUGH:
                    continue
                e = env.get(node, {})
                kw = {k.arg: k.value for k in node.keywords}
                conf = kw.get("confidence", node.args[7] if len(node.args) > 7 else None)
                rules, sevs = consts(node.args[0], e), consts(node.args[2], e)
                confs = ["high"] if conf is None else consts(conf, e)
            elif name == "schema_check.py" and isinstance(node, ast.Dict):
                d = {k.value: v for k, v in zip(node.keys, node.values)
                     if isinstance(k, ast.Constant)}
                if "id" not in d or "severity" not in d:
                    continue
                # audit.py re-wraps these with finding()'s default confidence
                rules, sevs, confs = consts(d["id"], {}), consts(d["severity"], {}), ["high"]
            else:
                continue
            if rules is None or sevs is None or confs is None:
                bad.append("{0}:{1}: {2}: severity {3}, confidence {4}".format(
                    name, node.lineno, ", ".join(rules) if rules else "unknown rule",
                    "?" if sevs is None else "/".join(sevs),
                    "?" if confs is None else "/".join(confs)))
                continue
            for r in rules:
                out.setdefault(r, set()).update((s, c) for s in sevs for c in confs)
    if bad:
        sys.exit("cannot resolve to literals:\n  " + "\n  ".join(bad))
    return out


def row(vs):
    """(cells, verdict) for one rule's (severity, confidence) pairs."""
    vs = [(s, c, blocks({"severity": s, "confidence": c})) for s, c in sorted(vs)]
    mixed = len({b for _, _, b in vs}) > 1
    verdict = "depends on severity" if mixed else "yes" if vs[0][2] else "no"
    cells = ["{0}, {1}{2}".format(s, c, (" (yes)" if b else " (no)") if mixed else "")
             for s, c, b in vs]
    return "; ".join(cells), verdict


def main(argv):
    v = variants()
    missing = [r for r in argv if r not in v]
    if missing:
        sys.exit("not built anywhere: " + ", ".join(missing))
    print("| Rule | Severity, confidence | Blocks? |")
    print("|---|---|---|")
    for r in argv or sorted(v):
        print("| `{0}` | {1} | {2} |".format(r, *row(v[r])))


if __name__ == "__main__":
    main(sys.argv[1:])
