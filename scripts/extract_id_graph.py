#!/usr/bin/env python3
"""Extract full ID-graph edges from all repos for HTML dense viewer."""
import re, os, json, yaml
from collections import defaultdict

ROOT = '/home/z/my-project/Z-ai-platform'
REPOS = {
    'standards': f'{ROOT}/standards/standards',
    'guard':     f'{ROOT}/guard/rules',
    'skills':    f'{ROOT}/skills/skills',
}

def repo_for_path(path):
    """Determine which repo a file belongs to (based on path prefix)."""
    if path.startswith(f'{ROOT}/standards/standards/'):
        return 'standards'
    if path.startswith(f'{ROOT}/guard/rules/'):
        return 'guard'
    if path.startswith(f'{ROOT}/skills/skills/'):
        return 'skills'
    return 'platform'

# Pass 1: build ID -> (repo, file, title) map
id_map = {}
for repo, root in REPOS.items():
    for dirpath, _, files in os.walk(root):
        for f in files:
            if not f.endswith('.md'):
                continue
            path = os.path.join(dirpath, f)
            try:
                txt = open(path, encoding='utf-8').read()
            except:
                continue

            # Try blockquote ID first (STD files)
            m = re.search(r'^>\s*ID:\s*([A-Z]+-[A-Z]+-\d+)\s*$', txt, re.MULTILINE)
            if m:
                id_map[m.group(1)] = {'repo': repo, 'file': path.replace(ROOT+'/', ''), 'fmt': 'blockquote'}
                continue

            # Try YAML frontmatter (RULE files have id: field)
            fm_match = re.match(r'^---\s*\n(.*?)\n---', txt, re.DOTALL)
            if fm_match:
                try:
                    fm = yaml.safe_load(fm_match.group(1))
                    if isinstance(fm, dict) and 'id' in fm and isinstance(fm['id'], str):
                        if re.match(r'^(STD|RULE|ZAI|TOOL|PROC)-', fm['id']):
                            id_map[fm['id']] = {'repo': repo, 'file': path.replace(ROOT+'/', ''), 'fmt': 'yaml-id'}
                            continue
                except:
                    pass

            # Try filename (RULE-MONOLITH-001.md etc)
            m2 = re.match(r'^(RULE-[A-Z]+-\d+)', f)
            if m2:
                id_map.setdefault(m2.group(1), {'repo': repo, 'file': path.replace(ROOT+'/', ''), 'fmt': 'filename'})

print(f"IDs found: {len(id_map)}")
prefixes = defaultdict(int)
for k in id_map:
    prefixes[k.split('-')[0]] += 1
print(f"By prefix: {dict(prefixes)}")

# Pass 2: extract edges
edges = []
for id_, info in id_map.items():
    path = os.path.join(ROOT, info['file'])
    try:
        txt = open(path, encoding='utf-8').read()
    except:
        continue

    related_targets = []

    # Blockquote Related:
    for m in re.finditer(r'^>\s*Related:\s*(.+?)$', txt, re.MULTILINE):
        rel = m.group(1).strip()
        # Split on comma/space, but handle "(none ...)" gracefully
        if rel.lower().startswith('(none'):
            continue
        for tgt in re.split(r'[,\s]+', rel):
            tgt = tgt.strip().rstrip('.').rstrip(',')
            if tgt and re.match(r'^(STD|RULE|ZAI|TOOL|PROC)-', tgt):
                related_targets.append(tgt)

    # YAML frontmatter related: (list or string)
    fm_match = re.match(r'^---\s*\n(.*?)\n---', txt, re.DOTALL)
    if fm_match:
        try:
            fm = yaml.safe_load(fm_match.group(1))
            if isinstance(fm, dict) and 'related' in fm:
                rel = fm['related']
                if isinstance(rel, list):
                    related_targets.extend([str(r).strip() for r in rel if r])
                elif isinstance(rel, str):
                    for tgt in re.split(r'[,\s]+', rel):
                        if tgt.strip():
                            related_targets.append(tgt.strip())
        except:
            pass

    for tgt in related_targets:
        tgt = tgt.strip().rstrip('.')
        if tgt in id_map:
            edges.append({
                'src': id_, 'tgt': tgt,
                'src_repo': info['repo'], 'tgt_repo': id_map[tgt]['repo'],
                'src_file': info['file'], 'tgt_file': id_map[tgt]['file'],
            })
        elif re.match(r'^(STD|RULE|ZAI|TOOL|PROC)-', tgt):
            # dangling — skip but report
            pass

print(f"Edges found: {len(edges)}")

# Build prefix matrix
matrix = defaultdict(lambda: defaultdict(int))
for e in edges:
    sp = e['src'].split('-')[0]
    tp = e['tgt'].split('-')[0]
    matrix[sp][tp] += 1

print("\nMatrix (src → tgt):")
print(f"  {'src\\tgt':10} {'STD':>5} {'RULE':>5} {'ZAI':>5} {'TOOL':>5} {'total':>6}")
for sp in ['STD', 'RULE', 'ZAI', 'TOOL']:
    row = matrix[sp]
    total = sum(row.values())
    if total > 0:
        print(f"  {sp:10} {row.get('STD',0):>5} {row.get('RULE',0):>5} {row.get('ZAI',0):>5} {row.get('TOOL',0):>5} {total:>6}")

# Top degree IDs
in_deg = defaultdict(int)
out_deg = defaultdict(int)
for e in edges:
    out_deg[e['src']] += 1
    in_deg[e['tgt']] += 1

print("\nTop 10 by out-degree (most referencing):")
for k, v in sorted(out_deg.items(), key=lambda x: -x[1])[:10]:
    print(f"  {k:25} → {v} edges ({id_map[k]['repo']})")
print("\nTop 10 by in-degree (most referenced):")
for k, v in sorted(in_deg.items(), key=lambda x: -x[1])[:10]:
    print(f"  {k:25} → {v} edges ({id_map[k]['repo']})")

# Save for HTML
out = {
    'ids': {k: {'repo': v['repo'], 'file': v['file']} for k, v in id_map.items()},
    'edges': edges,
    'matrix': {sp: dict(matrix[sp]) for sp in matrix},
    'top_out': [(k, v) for k, v in sorted(out_deg.items(), key=lambda x: -x[1])[:15]],
    'top_in':  [(k, v) for k, v in sorted(in_deg.items(), key=lambda x: -x[1])[:15]],
    'summary': {
        'ids_total': len(id_map),
        'edges_total': len(edges),
        'prefixes': dict(prefixes),
    },
}
with open('/home/z/my-project/scripts/id-graph-data.json', 'w') as f:
    json.dump(out, f, indent=2)
print(f"\nSaved → /home/z/my-project/scripts/id-graph-data.json")
