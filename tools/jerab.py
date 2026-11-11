"""Přepočet jeřábu a dopravy pro díly modulu 3,5 t (dřív 20 t). Mění jen jt, dpn a dp; návrh pokrytí a bilance zůstávají."""
import gzip, json, glob, re, sys, collections
DIL = 3.5
# třída jeřábu podle vyložení pro břemeno 3,5 t + vázací prostředky (~4 t)
TRIDY = [(12, 20), (20, 40), (30, 60), (40, 100), (50, 160)]   # jt=20 = hydraulická ruka na kamionu (HMR)
SEV = {'účelová / obytná komunikace – ověřit šíři a poloměry pro návěs': 1,
       'kamion i jeřáb po nezpevněném terénu – nutné panely, ověřit únosnost': 1,
       'jeřáb ~N t (vyložení N m pro díl N t) – ověřit dostupnost a místo na silnici': 1,
       'jeřáb nemá kde stát – plocha N m od silnice, díl N t nelze osadit z komunikace': 2,
       'jeřáb ~N t musí stát na ploše (zpevněná, dost místa) – ověřit únosnost': 1,
       'vedení do N m – omezení jeřábu': 1,
       'cesta pro kamion z hlavní silnice není bez omezení (most, výška, šíře) – ověřit trasu': 1,
       'přístupová komunikace má omezení hmotnosti/výšky/šíře': 2,
       'soukromá komunikace (vjezd se svolením)': 1}
pat = lambda p: re.sub(r'\d+', 'N', p)
def trida(jr):
    for lim, t in TRIDY:
        if jr <= lim: return t
    return 0
def jtxt(t): return 'kamion s hydraulickou rukou' if t == 20 else f'jeřáb ~{t} t'
tot = collections.Counter()
for f in sorted(glob.glob(sys.argv[1] + '/*.json.gz')):
    d = json.load(gzip.open(f)); c = collections.Counter()
    for x in d['db']:
        notes = [p for p in (x.get('dpn') or '').split('; ') if p]
        jr = x.get('jr') or 0; old_dp = x['dp']; t = trida(jr); new = []
        for p in notes:
            q = pat(p)
            if q.startswith('jeřáb ~N t (vyložení') or q.startswith('jeřáb nemá kde stát'):
                continue                                  # přidá se znovu podle nové třídy níže
            if q.startswith('jeřáb ~N t musí stát na ploše'):
                new.append(f'{jtxt(t or 160)} musí stát na ploše (zpevněná, dost místa) – ověřit únosnost'); continue
            new.append(p)
        if any(pat(p).startswith(('jeřáb ~N t (vyložení', 'jeřáb nemá kde stát')) for p in notes) or x.get('jt'):
            if t == 0:
                m = re.search(r'plocha (\d+) m od silnice', x.get('dpn') or '')
                new.append(f'jeřáb nemá kde stát – plocha {m.group(1) if m else round(jr)} m od silnice, díl {DIL:g} t nelze osadit z komunikace'.replace('.', ','))
            elif t == 160:
                new.append(f'jeřáb ~160 t (vyložení {round(jr)} m pro díl {DIL:g} t) – ověřit dostupnost a místo na silnici'.replace('3.5', '3,5'))
            x['jt'] = t
        x['dpn'] = '; '.join(new)
        sevs = [SEV.get(pat(p).replace('kamion s hydraulickou rukou', 'jeřáb ~N t'), 1) for p in new]
        x['dp'] = max(sevs, default=0)
        c[(old_dp, x['dp'])] += 1
        if old_dp == 2 and x['dp'] < 2 and x['ok'] == 1: c['nove_vhodne'] += 1
    d['meta']['dil_t'] = DIL
    d['meta']['jerab'] = 'třída podle vyložení pro díl 3,5 t: do 12 m kamion s hydraulickou rukou, do 20 m ~40 t, do 30 m ~60 t, do 40 m ~100 t, do 50 m ~160 t'
    with gzip.open(f, 'wt', encoding='utf-8', compresslevel=9) as o: json.dump(d, o, ensure_ascii=False, separators=(',', ':'))
    tot.update(c)
    print(f.split('/')[-1][:-8], {f'{a}->{b}': v for (a, b), v in sorted((k, v) for k, v in c.items() if isinstance(k, tuple)) if a != b}, 'nově vhodné', c['nove_vhodne'])
print('CELKEM', {f'{a}->{b}': v for (a, b), v in sorted((k, v) for k, v in tot.items() if isinstance(k, tuple))}, 'nově vhodné', tot['nove_vhodne'])
