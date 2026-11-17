import json, re, statistics, datetime, collections, csv
TODAY = datetime.date(2026, 11, 8)

# ---- load
search = {}
variants = collections.defaultdict(set)
for fn in ['raw_search.jsonl', 'raw_search_p1.jsonl', 'raw_search_p3.jsonl']:
    for l in open(fn):
        r = json.loads(l)
        search.setdefault(r['id'], r)
        variants[r['id']].add(r['variant'] + ':' + r['query'])
meta = {}
for fn in ['raw_meta.jsonl', 'raw_meta_curl.jsonl']:
    for l in open(fn):
        r = json.loads(l)
        if r.get('upload_date') and '-' not in r['upload_date']:
            d = r['upload_date']
            r['upload_date'] = f"{d[:4]}-{d[4:6]}-{d[6:]}"
        meta[r['id']] = r

rows = []
for i, m in meta.items():
    if not m.get('upload_date'):
        continue
    d = datetime.date.fromisoformat(m['upload_date'])
    age = (TODAY - d).days
    views = m.get('view_count') or search[i]['views'] or 0
    rows.append({
        'id': i, 'title': m['title'], 'channel': m['channel'], 'views': views,
        'likes': m.get('like_count'), 'duration': m['duration'], 'upload_date': m['upload_date'],
        'age_days': age, 'vpd': views / max(age, 1), 'tags': m.get('tags') or [],
        'desc': (m.get('description') or '')[:300],
        'variants': sorted(variants[i]),
        'url': 'https://www.youtube.com/shorts/' + i,
    })

# ---- classification
STARS = {
    'ronaldo': r'ronaldo|cr7|cristiano|siu+',
    'messi': r'messi|lionel|\bgoat\b.*argent',
    'mbappe': r'mbapp',
    'haaland': r'haaland',
    'yamal': r'yamal',
    'vinicius': r'vini(cius|\b)|vinícius|vinijr',
    'bellingham': r'bellingham',
    'kane': r'\bkane\b',
    'salah': r'salah',
    'neymar': r'neymar',
    'pogba': r'pogba',
    'ronaldinho': r'ronaldinho',
    'zidane': r'zidane|zizou',
    'maradona': r'maradona',
    'pele': r'\bpel[eé]\b',
}
ANGLES = {
    'family_personal': r'\bfamily\b|\bmom\b|mother|\bdad\b|father|\bson\b|daughter|\bkids?\b|wife|girlfriend|\bbaby\b|grandma|brother|sister|wedding|\bines\b|georgina|antonela|ronaldo jr|\bjr\b|\bgift\b|christmas|hug|proud|love',
    'childhood_origin': r'child|poor|\bstory\b|journey|struggl|bullied|origin|rags|untold|\bat \d\d\b|young|grew up|burger|sweeping|rich|from .* to ',
    'rivalry_vs': r'\bvs\.?\b|versus|rival|\bbeef\b|feud|\bor\b.*\?|better than|best ever|goat',
    'revenge_redemption': r'revenge|redemption|comeback|silenced|payback|prove|answer|haters|doubt|never forget|didn.t believe|forgive|apolog',
    'humiliation_skill': r'humiliat|destroy|cooked|embarrass|exposed|nutmeg|ankle|disrespect|trap|crazy skill|skill|dribbl|trolled|lesson',
    'record_numbers': r'record|history|first (player|ever)|only player|\d+ (goals|years|titles|trophies|million|m\b|assists|caps)|\bmost\b|youngest|oldest|fastest|\b\d{3,}\b|\$\d|€\d|£\d',
    'rare_moment': r'rare|never seen|unseen|unbelievable|once in|leaked|behind the scenes|forgotten|you missed|nobody noticed|footage',
    'controversy_ref': r'controvers|banned|red card|\bref(eree)?\b|\bvar\b|scandal|illegal|cheat|altercation|fight|heated|angry|furious|slap|punch|spat|argument|racis|offside|penalty',
    'what_if': r'what if|imagine|if .* had|could have',
    'quiz_guess': r'guess|quiz|can you|who is|how many|which one|rate |ranking|ranked|top \d+',
    'transfer_news': r'transfer|signs?\b|signing|deal|join(s|ed)?\b|contract|leave|leaving|move|release clause|bid|offer|rumou?r|breaking|official|here we go',
    'emotional_tears': r'cried|crying|tears|emotional|heartwarming|sweet|heartbreak|💔|🥹|❤️‍🩹|sad|touching|respect|tribute|jota',
    'kids_fun_viral': r'kid|funny|funniest|reaction|challenge|parody|😂|🤣|prank|laugh',
    'highlights_skills': r'goal|goals|skills|highlights|assist|masterclass|magic|insane|unreal',
}


def tag(title, desc='', tags=None):
    t = (title or '').lower()
    out_s = [k for k, p in STARS.items() if re.search(p, t)]
    out_a = [k for k, p in ANGLES.items() if re.search(p, t)]
    return out_s, out_a


for r in rows:
    r['stars'], r['angles'] = tag(r['title'])
    r['is_short'] = r['duration'] <= 61


def pct(v, q):
    v = sorted(v)
    if not v:
        return None
    k = (len(v) - 1) * q
    f = int(k)
    c = min(f + 1, len(v) - 1)
    return v[f] + (v[c] - v[f]) * (k - f)


def stat(vs):
    return {'n': len(vs), 'median': int(statistics.median(vs)) if vs else None,
            'p90': int(pct(vs, 0.9)) if vs else None, 'mean': int(sum(vs) / len(vs)) if vs else None}


def table(sel, key, label):
    g = collections.defaultdict(list)
    for r in sel:
        for k in r[key] or ['(none)']:
            g[k].append(r['views'])
    return {k: stat(v) for k, v in sorted(g.items(), key=lambda x: -len(x[1]))}


if __name__ == '__main__':
    shorts = [r for r in rows if r['is_short']]
    rec60 = [r for r in shorts if r['age_days'] <= 60]
    rec90 = [r for r in shorts if r['age_days'] <= 90]
    rec30 = [r for r in shorts if r['age_days'] <= 30]
    print('rows', len(rows), 'shorts<=61s', len(shorts), '<=90d', len(rec90), '<=60d', len(rec60), '<=30d', len(rec30))
    res = {'counts': {'meta_rows': len(rows), 'shorts': len(shorts), 'shorts_60d': len(rec60), 'shorts_30d': len(rec30), 'shorts_90d': len(rec90)}}
    for name, sel in [('last60d', rec60), ('last90d', rec90), ('all_shorts', shorts)]:
        res[name] = {'overall': stat([r['views'] for r in sel]),
                     'by_angle': table(sel, 'angles', 'angle'), 'by_star': table(sel, 'stars', 'star')}
    json.dump(res, open('stats.json', 'w'), indent=1)
    json.dump(rows, open('shorts_dataset.json', 'w'), ensure_ascii=False, indent=0)
    with open('shorts_dataset.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['id', 'title', 'channel', 'views', 'likes', 'duration', 'upload_date', 'age_days', 'vpd', 'stars', 'angles', 'url'])
        for r in sorted(rows, key=lambda r: -r['views']):
            w.writerow([r['id'], r['title'], r['channel'], r['views'], r['likes'], r['duration'], r['upload_date'], r['age_days'], round(r['vpd']), '|'.join(r['stars']), '|'.join(r['angles']), r['url']])
    for name in ['last60d', 'last90d']:
        print('==', name, res[name]['overall'])
        for k, v in res[name]['by_angle'].items():
            print(f"  {k:22s} {v}")
        for k, v in res[name]['by_star'].items():
            print(f"  * {k:14s} {v}")
