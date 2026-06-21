#!/usr/bin/env python3
"""Extract full ID-graph data with titles, Aligned_with edges, for dense D3.js viewer."""
import re, os, json, yaml
from collections import defaultdict

ROOT = '/home/z/my-project/Z-ai-platform'
REPOS = {
    'standards': f'{ROOT}/standards/standards',
    'guard':     f'{ROOT}/guard/rules',
    'skills':    f'{ROOT}/skills/skills',
}

def repo_for_path(path):
    if path.startswith(f'{ROOT}/standards/standards/'): return 'standards'
    if path.startswith(f'{ROOT}/guard/rules/'): return 'guard'
    if path.startswith(f'{ROOT}/skills/skills/'): return 'skills'
    return 'platform'

def extract_title(txt, fallback_id, filename):
    # Try YAML title field first
    fm_match = re.match(r'^---\s*\n(.*?)\n---', txt, re.DOTALL)
    if fm_match:
        try:
            fm = yaml.safe_load(fm_match.group(1))
            if isinstance(fm, dict) and 'title' in fm and isinstance(fm['title'], str):
                t = fm['title'].strip()
                if t and not t.startswith('RULE-'):  # RULE YAML title is clean
                    return t
                # For RULE: strip the "RULE-MONOLITH-XXX:" prefix
                if t.startswith('RULE-'):
                    return re.sub(r'^RULE-[A-Z]+-\d+:\s*', '', t)
        except:
            pass
    # Try H1
    m = re.search(r'^#\s+(.+?)$', txt, re.MULTILINE)
    if m:
        title = m.group(1).strip()
        # Clean up STD titles: "# Standard: Standard ID System v2.0 (EN)" → "Standard ID System"
        title = re.sub(r'^Standard:\s+', '', title)
        title = re.sub(r'\s+v\d+\.\d+(\.\d+)?(\s*\(EN\))?$', '', title)
        # Strip RULE- prefix
        title = re.sub(r'^RULE-[A-Z]+-\d+:\s*', '', title)
        if title:
            return title
    # Fallback to filename
    return filename.replace('.md', '').replace('-', ' ')

# Pass 1: build ID -> metadata map
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

            id_ = None
            fmt = None

            # Try blockquote ID first (STD files)
            m = re.search(r'^>\s*ID:\s*([A-Z]+-[A-Z]+-\d+)\s*$', txt, re.MULTILINE)
            if m:
                id_ = m.group(1)
                fmt = 'blockquote'
            else:
                # Try YAML frontmatter
                fm_match = re.match(r'^---\s*\n(.*?)\n---', txt, re.DOTALL)
                if fm_match:
                    try:
                        fm = yaml.safe_load(fm_match.group(1))
                        if isinstance(fm, dict) and 'id' in fm and isinstance(fm['id'], str):
                            if re.match(r'^(STD|RULE|ZAI|TOOL|PROC)-', fm['id']):
                                id_ = fm['id']
                                fmt = 'yaml-id'
                    except:
                        pass
                if not id_:
                    # Filename fallback (RULE-*)
                    m2 = re.match(r'^(RULE-[A-Z]+-\d+)', f)
                    if m2:
                        id_ = m2.group(1)
                        fmt = 'filename'

            if not id_:
                continue

            title = extract_title(txt, id_, f)
            id_map[id_] = {
                'repo': repo,
                'file': path.replace(ROOT+'/', ''),
                'fmt': fmt,
                'title': title,
                'prefix': id_.split('-')[0],
            }

print(f"IDs found: {len(id_map)}")
prefixes = defaultdict(int)
for k in id_map:
    prefixes[id_map[k]['prefix']] += 1
print(f"By prefix: {dict(prefixes)}")

# Pass 2: extract edges (Related: + Aligned_with:)
related_edges = []
aligned_edges = []
edge_set = set()  # dedupe

for id_, info in id_map.items():
    path = os.path.join(ROOT, info['file'])
    try:
        txt = open(path, encoding='utf-8').read()
    except:
        continue

    # Blockquote Related:
    for m in re.finditer(r'^>\s*Related:\s*(.+?)$', txt, re.MULTILINE):
        rel = m.group(1).strip()
        if rel.lower().startswith('(none'):
            continue
        # Strip parenthetical notes (e.g. "ZAI-META-001 (legacy, kept as pointer)")
        for tgt_raw in re.split(r'[,\s]+', rel):
            tgt = tgt_raw.strip().rstrip('.').rstrip(',')
            if tgt and re.match(r'^(STD|RULE|ZAI|TOOL|PROC)-', tgt):
                key = (id_, tgt, 'related')
                if key not in edge_set and tgt in id_map:
                    edge_set.add(key)
                    related_edges.append({
                        'src': id_, 'tgt': tgt,
                        'src_repo': info['repo'], 'tgt_repo': id_map[tgt]['repo'],
                        'type': 'related',
                    })

    # Blockquote Aligned_with:
    for m in re.finditer(r'^>\s*Aligned_with:\s*(.+?)$', txt, re.MULTILINE):
        rel = m.group(1).strip()
        if rel.lower().startswith('(none') or rel.startswith('<comma'):
            continue
        for tgt_raw in re.split(r'[,\s]+', rel):
            # Strip notes
            tgt = tgt_raw.strip().rstrip('.').rstrip(',')
            # Take only the ID portion (before any parenthetical)
            tgt = re.match(r'^[A-Z]+-[A-Z]+-\d+', tgt)
            if tgt:
                tgt = tgt.group(0)
                if tgt in id_map:
                    key = (id_, tgt, 'aligned')
                    if key not in edge_set:
                        edge_set.add(key)
                        aligned_edges.append({
                            'src': id_, 'tgt': tgt,
                            'src_repo': info['repo'], 'tgt_repo': id_map[tgt]['repo'],
                            'type': 'aligned',
                        })

    # YAML frontmatter (RULE files have related: as list, skills have aligned_with:)
    fm_match = re.match(r'^---\s*\n(.*?)\n---', txt, re.DOTALL)
    if fm_match:
        try:
            fm = yaml.safe_load(fm_match.group(1))
            if isinstance(fm, dict):
                # related: (RULE YAML)
                if 'related' in fm:
                    rel = fm['related']
                    targets = []
                    if isinstance(rel, list):
                        targets = [str(r).strip() for r in rel if r]
                    elif isinstance(rel, str):
                        targets = [t.strip() for t in re.split(r'[,\s]+', rel) if t.strip()]
                    for tgt in targets:
                        if tgt in id_map:
                            key = (id_, tgt, 'related')
                            if key not in edge_set:
                                edge_set.add(key)
                                related_edges.append({
                                    'src': id_, 'tgt': tgt,
                                    'src_repo': info['repo'], 'tgt_repo': id_map[tgt]['repo'],
                                    'type': 'related',
                                })
                # aligned_with: (skills YAML)
                if 'aligned_with' in fm:
                    rel = fm['aligned_with']
                    targets = []
                    if isinstance(rel, list):
                        targets = [str(r).strip() for r in rel if r]
                    elif isinstance(rel, str):
                        # Could be "ZAI-META-001 (legacy, kept as pointer), ZAI-META-002 (toolkit skill-creator)"
                        # Extract just IDs
                        targets = re.findall(r'[A-Z]+-[A-Z]+-\d+', rel)
                    for tgt in targets:
                        if tgt in id_map:
                            key = (id_, tgt, 'aligned')
                            if key not in edge_set:
                                edge_set.add(key)
                                aligned_edges.append({
                                    'src': id_, 'tgt': tgt,
                                    'src_repo': info['repo'], 'tgt_repo': id_map[tgt]['repo'],
                                    'type': 'aligned',
                                })
        except:
            pass

all_edges = related_edges + aligned_edges
print(f"\nRelated: edges: {len(related_edges)}")
print(f"Aligned_with: edges: {len(aligned_edges)}")
print(f"Total edges: {len(all_edges)}")

# Save full data for D3 viewer
nodes = [{'id': k, **v} for k, v in id_map.items()]
links = all_edges

# Degree calc
in_deg = defaultdict(int)
out_deg = defaultdict(int)
for e in all_edges:
    out_deg[e['src']] += 1
    in_deg[e['tgt']] += 1
for n in nodes:
    n['out_deg'] = out_deg.get(n['id'], 0)
    n['in_deg'] = in_deg.get(n['id'], 0)
    n['total_deg'] = n['out_deg'] + n['in_deg']

out = {
    'nodes': nodes,
    'links': links,
    'summary': {
        'ids_total': len(nodes),
        'related_edges': len(related_edges),
        'aligned_edges': len(aligned_edges),
        'total_edges': len(all_edges),
        'prefixes': dict(prefixes),
        'by_repo': {r: sum(1 for n in nodes if n['repo'] == r) for r in REPOS},
    },
}
with open('/home/z/my-project/scripts/id-graph-full.json', 'w') as f:
    json.dump(out, f, indent=2)
print(f"\nSaved → /home/z/my-project/scripts/id-graph-full.json")
print(f"  nodes: {len(nodes)}")
print(f"  links: {len(links)}")

# Top 10 by total degree
print("\nTop 10 by total degree:")
for n in sorted(nodes, key=lambda x: -x['total_deg'])[:10]:
    print(f"  {n['id']:25} (in={n['in_deg']:>3}, out={n['out_deg']:>3}, total={n['total_deg']:>3}) — {n['repo']}")
