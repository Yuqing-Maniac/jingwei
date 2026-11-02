# 经纬织图 应用图标：两经两纬交织（上下穿插）成“井”字，左上交点为琥珀主节点、右下交点为体系节点
def svg(size=512, globe=True):
    U = 'gradientUnits="userSpaceOnUse"'
    W = 34; X1, X2, Y1, Y2 = 178, 334, 178, 334; A, B = 70, 442
    s = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="{size}" height="{size}">
<defs>
 <linearGradient id="bg" x1="0" y1="0" x2="180" y2="512" {U}><stop offset="0" stop-color="#1A4A8E"/><stop offset="0.55" stop-color="#0C2552"/><stop offset="1" stop-color="#06122C"/></linearGradient>
 <radialGradient id="glow" cx="256" cy="230" r="300" {U}><stop offset="0" stop-color="#4CA8FF" stop-opacity="0.40"/><stop offset="1" stop-color="#4CA8FF" stop-opacity="0"/></radialGradient>
 <linearGradient id="jing" x1="0" y1="70" x2="0" y2="442" {U}><stop offset="0" stop-color="#A6F5EC"/><stop offset="1" stop-color="#1FB9AA"/></linearGradient>
 <linearGradient id="wei" x1="70" y1="0" x2="442" y2="0" {U}><stop offset="0" stop-color="#B9DAFF"/><stop offset="1" stop-color="#3D97F5"/></linearGradient>
 <linearGradient id="amber" x1="0" y1="140" x2="0" y2="232" {U}><stop offset="0" stop-color="#FFD98A"/><stop offset="1" stop-color="#F09A2A"/></linearGradient>
 <linearGradient id="node" x1="0" y1="282" x2="0" y2="378" {U}><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#D3E4FA"/></linearGradient>
 <linearGradient id="sheen" x1="0" y1="0" x2="0" y2="300" {U}><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.18"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient>
 <linearGradient id="shU" x1="0" y1="{Y2-W/2-16}" x2="0" y2="{Y2-W/2}" {U}><stop offset="0" stop-color="#03102A" stop-opacity="0"/><stop offset="1" stop-color="#03102A" stop-opacity="0.6"/></linearGradient>
 <linearGradient id="shD" x1="0" y1="{Y2+W/2}" x2="0" y2="{Y2+W/2+16}" {U}><stop offset="0" stop-color="#03102A" stop-opacity="0.6"/><stop offset="1" stop-color="#03102A" stop-opacity="0"/></linearGradient>
 <linearGradient id="shL" x1="{X2-W/2-16}" y1="0" x2="{X2-W/2}" y2="0" {U}><stop offset="0" stop-color="#03102A" stop-opacity="0"/><stop offset="1" stop-color="#03102A" stop-opacity="0.6"/></linearGradient>
 <linearGradient id="shR" x1="{X2+W/2}" y1="0" x2="{X2+W/2+16}" y2="0" {U}><stop offset="0" stop-color="#03102A" stop-opacity="0.6"/><stop offset="1" stop-color="#03102A" stop-opacity="0"/></linearGradient>
 <clipPath id="c"><rect x="0" y="0" width="512" height="512" rx="114"/></clipPath>
 <filter id="sh" x="-40%" y="-40%" width="180%" height="180%"><feDropShadow dx="0" dy="7" stdDeviation="9" flood-color="#010612" flood-opacity="0.6"/></filter>
 <filter id="soft" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="14"/></filter>
</defs>
<g clip-path="url(#c)">
 <rect width="512" height="512" fill="url(#bg)"/>
 <rect width="512" height="512" fill="url(#glow)"/>'''
    if globe:
        s += '''
 <g fill="none" stroke="#8CC4FF" stroke-opacity="0.12" stroke-width="3">
  <circle cx="256" cy="256" r="222"/><ellipse cx="256" cy="256" rx="128" ry="222"/><ellipse cx="256" cy="256" rx="222" ry="92"/>
 </g>'''
    W = 34; X1, X2, Y1, Y2 = 178, 334, 178, 334; A, B = 70, 442
    gap = lambda: '#0B2049'
    # 底层：两纬（横）
    s += f'''
 <g stroke-linecap="round" stroke-width="{W}">
  <line x1="{A}" y1="{Y1}" x2="{B}" y2="{Y1}" stroke="url(#wei)"/>
  <line x1="{A}" y1="{Y2}" x2="{B}" y2="{Y2}" stroke="url(#wei)"/>
  <line x1="{X1}" y1="{A}" x2="{X1}" y2="{B}" stroke="url(#jing)"/>
  <line x1="{X2}" y1="{A}" x2="{X2}" y2="{B}" stroke="url(#jing)"/>
 </g>
 <!-- 交织：左下交点纬线压经线；右上交点经线压纬线（压下的一股在交界处加暗，表现上下穿插） -->
 <rect x="{X1-W/2}" y="{Y2-W/2-16}" width="{W}" height="16" fill="url(#shU)"/>
 <rect x="{X1-W/2}" y="{Y2+W/2}" width="{W}" height="16" fill="url(#shD)"/>
 <line x1="{X1-W/2-14}" y1="{Y2}" x2="{X1+W/2+14}" y2="{Y2}" stroke="url(#wei)" stroke-width="{W}" stroke-linecap="butt"/>
 <rect x="{X2-W/2-16}" y="{Y1-W/2}" width="16" height="{W}" fill="url(#shL)"/>
 <rect x="{X2+W/2}" y="{Y1-W/2}" width="16" height="{W}" fill="url(#shR)"/>
 <line x1="{X2}" y1="{Y1-W/2-14}" x2="{X2}" y2="{Y1+W/2+14}" stroke="url(#jing)" stroke-width="{W}" stroke-linecap="butt"/>
 <!-- 主节点光晕 -->
 <circle cx="{X1}" cy="{Y1}" r="62" fill="#F2A33A" opacity="0.35" filter="url(#soft)"/>
 <g filter="url(#sh)">
  <rect x="{X1-46}" y="{Y1-46}" width="92" height="92" rx="26" fill="url(#amber)"/>
  <rect x="{X2-46}" y="{Y2-46}" width="92" height="92" rx="24" fill="url(#node)"/>
 </g>
 <rect x="{X1-46}" y="{Y1-46}" width="92" height="92" rx="24" fill="none" stroke="#FFF1CF" stroke-opacity="0.7" stroke-width="3"/>
 <circle cx="{X1}" cy="{Y1}" r="15" fill="#7A3A00" fill-opacity="0.55"/>
 <rect x="{X2-25}" y="{Y2-25}" width="50" height="50" rx="12" fill="none" stroke="#1FB9AA" stroke-width="9"/>
 <rect width="512" height="300" fill="url(#sheen)"/>
</g>
<rect x="3" y="3" width="506" height="506" rx="111" fill="none" stroke="#A9D2FF" stroke-opacity="0.25" stroke-width="5"/>
</svg>'''
    return s
open('icon.svg','w').write(svg(512,True))
open('icon_small.svg','w').write(svg(512,False))
