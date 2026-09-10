W, M = 900, 100
p = []
p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{W}" viewBox="0 0 {W} {W}">')
p.append('<defs>')
p.append('<linearGradient id="wood" x1="0" y1="0" x2="0" y2="1">')
p.append('<stop offset="0" stop-color="#6b5236"/><stop offset="0.5" stop-color="#4e3b27"/><stop offset="1" stop-color="#3a2b1c"/></linearGradient>')
p.append('<linearGradient id="iron" x1="0" y1="0" x2="0" y2="1">')
p.append('<stop offset="0" stop-color="#5a5f63"/><stop offset="0.45" stop-color="#33383c"/><stop offset="1" stop-color="#1e2225"/></linearGradient>')
p.append('<radialGradient id="stain" cx="0.5" cy="0.5" r="0.75">')
p.append('<stop offset="0.55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#120a06" stop-opacity="0.55"/></radialGradient>')
p.append('</defs>')
p.append(f'<rect x="14" y="14" width="{W-28}" height="{W-28}" rx="18" fill="url(#wood)"/>')
for i in range(1, 9):
    y = 14 + i * (W - 28) / 9
    p.append(f'<rect x="14" y="{y-1.5:.1f}" width="{W-28}" height="3" fill="#2c2015" opacity="0.55"/>')
p.append(f'<rect x="14" y="14" width="{W-28}" height="{W-28}" rx="18" fill="none" stroke="url(#iron)" stroke-width="26"/>')
p.append(f'<rect x="30" y="30" width="{W-60}" height="{W-60}" rx="10" fill="none" stroke="#151a1d" stroke-width="4" opacity="0.7"/>')
p.append(f'<rect x="0" y="0" width="{W}" height="{W}" fill="url(#stain)"/>')
p.append(f'<rect x="{M-6}" y="{M-6}" width="{W-2*M+12}" height="{W-2*M+12}" rx="8" fill="#120c08" opacity="0.85"/>')
p.append(f'<rect x="{M-6}" y="{M-6}" width="{W-2*M+12}" height="{W-2*M+12}" rx="8" fill="none" stroke="#0a0705" stroke-width="8"/>')
p.append('</svg>')
open('sorting_table.svg','w').write('\n'.join(p))
print('svg written')
