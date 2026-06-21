#!/usr/bin/env python3
"""Build inline JSON for hierarchy-live.html from id-graph-full.json.

Reads:  /home/z/my-project/Dense-graph/data/id-graph-full.json
Writes: /home/z/my-project/Dense-graph/scripts/_hierarchy-inline.json

Output is a compact JS expression (no whitespace) suitable for inline
embedding: const IDG = {"nodes":[{"id":"...","r":"...","t":"...","p":"...","f":"..."},...],"links":[{"s":"...","t":"...","k":"..."},...],"summary":{...}};
"""
import json
import sys
from pathlib import Path

SRC = Path("/home/z/my-project/Dense-graph/data/id-graph-full.json")
DST = Path("/home/z/my-project/Dense-graph/scripts/_hierarchy-inline.json")

data = json.loads(SRC.read_text())

compact = {
    "nodes": [
        {"id": n["id"], "r": n["repo"], "t": n["title"], "p": n["prefix"], "f": n["file"]}
        for n in data["nodes"]
    ],
    "links": [
        {"s": l["src"], "t": l["tgt"], "k": l["type"]}
        for l in data["links"]
    ],
    "summary": data["summary"],
}

# Compact JSON, no whitespace
inline = json.dumps(compact, separators=(",", ":"), ensure_ascii=False)
DST.write_text(inline)
print(f"Wrote {DST} ({len(inline)} bytes, {len(compact['nodes'])} nodes, {len(compact['links'])} links)")
