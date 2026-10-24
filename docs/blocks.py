"""blocks.py -- the README's "Blocks?" column, read from the rules themselves.

  python docs/blocks.py                       # every rule
  python docs/blocks.py S1-SOFT-404 S2-ORPHAN # just these, in this order

Every place a finding is built (finding(...) in audit.py, the finding dicts in
schema_check.py) is read with ast, and each severity/confidence it can have is passed to
verify.blocks(). A rule built at more than one severity lists each one.
"""
import ast
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "..", "scripts")
sys.path.insert(0, SCRIPTS)
from verify import blocks  # noqa: E402


def consts(node):
    """The string values an argument can take: a literal, or either side of a ternary."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, ast.IfExp):
        return consts(node.body) + consts(node.orelse)
    return []


def variants():
    """{rule: {(severity, confidence)}} for every rule built with a literal id."""
    out = {}
    for name in ("audit.py", "schema_check.py"):
        with open(os.path.join(SCRIPTS, name), encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and getattr(node.func, "id", None) == "finding"
                    and len(node.args) >= 3):
                rules, sevs = consts(node.args[0]), consts(node.args[2])
                kw = {k.arg: k.value for k in node.keywords}
                confs = consts(kw["confidence"]) if "confidence" in kw else ["high"]
            elif isinstance(node, ast.Dict):
                d = {k.value: v for k, v in zip(node.keys, node.values)
                     if isinstance(k, ast.Constant)}
                if "id" not in d or "severity" not in d:
                    continue
                # audit.py re-wraps these with finding()'s default confidence
                rules, sevs, confs = consts(d["id"]), consts(d["severity"]), ["high"]
            else:
                continue
            for r in rules:
                out.setdefault(r, set()).update((s, c) for s in sevs for c in confs)
    return out


def main(argv):
    v = variants()
    missing = [r for r in argv if r not in v]
    if missing:
        sys.exit("not built anywhere: " + ", ".join(missing))
    print("| Rule | Severity, confidence | Blocks? |")
    print("|---|---|---|")
    for r in argv or sorted(v):
        vs = [(s, c, blocks({"severity": s, "confidence": c})) for s, c in sorted(v[r])]
        says = {b for _, _, b in vs}
        mixed = len(says) > 1
        verdict = "depends on severity" if mixed else "yes" if True in says else "no"
        cells = ["{0}, {1}{2}".format(s, c, (" (yes)" if b else " (no)") if mixed else "")
                 for s, c, b in vs]
        print("| `{0}` | {1} | {2} |".format(r, "; ".join(cells), verdict))


if __name__ == "__main__":
    main(sys.argv[1:])
