#!/usr/bin/env python3
"""Loud multi-font animated captions -> ASS (1080x1920). Usage: captions_loud.py spec.json out.ass
Burn with: python3 $FF/scripts/caption.py in.mp4 --ass out.ass --fonts-dir $EV/fonts -o out.mp4  (needs ffmpeg-full on PATH)
Spec = {"groups":[{"start":s,"end":e,"lines":[{"y":1240,"delay":0,"rot":-5,"runs":[{"font","size","fill","outline","bord","text","flash"?,"flash_d"?}]}]}]}
Animation per line: pop-in with overshoot + tilt, key-word colour flash, slow 7% push, exit shrink/fade.
NOTE: ASS \\t() times are MILLISECONDS."""
import sys,json
ms=lambda x:int(round(x*1000))
def bgr(h): h=h.lstrip('#'); return f'&H00{h[4:6]}{h[2:4]}{h[0:2]}&'.upper()
def ts(t): return f'{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}'
def run(r):
    c=f"\\c{bgr(r['fill'])}"
    if r.get('flash'):
        d=r.get('flash_d',0); c=f"\\c&HFFFFFF&\\t({ms(d+0.18)},{ms(d+0.30)},\\c{bgr(r['flash'])})"
    return f"{{\\fn{r['font']}\\fs{r['size']}{c}\\3c{bgr(r['outline'])}\\bord{r['bord']}\\shad5\\4c&H000000&}}{r['text']}"
def line(a,b,L):
    d=L.get('delay',0.0); rot=L.get('rot',-5); y=L['y']; x=L.get('x',540); dur=b-a
    anim=(f'\\an5\\pos({x},{y})\\fscx35\\fscy35\\alpha&HFF&\\frz{rot}\\blur1'
          f'\\t({ms(d)},{ms(d+0.10)},\\fscx126\\fscy126\\alpha&H00&\\frz{-rot/3:.1f})'
          f'\\t({ms(d+0.10)},{ms(d+0.20)},\\fscx100\\fscy100\\frz0)'
          f'\\t({ms(d+0.25)},{ms(dur-0.12)},\\fscx107\\fscy107)'
          f'\\t({ms(dur-0.12)},{ms(dur)},\\fscx70\\fscy70\\alpha&HFF&)')
    return f"Dialogue: 0,{ts(a)},{ts(b)},Default,,0,0,0,,{{{anim}}}{''.join(run(r) for r in L['runs'])}"
HDR='''[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Impact,100,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,6,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
if __name__=="__main__":
    spec=json.load(open(sys.argv[1])); D=[line(g['start'],g['end'],L) for g in spec['groups'] for L in g['lines']]
    open(sys.argv[2],'w',encoding='utf-8').write(HDR+'\n'.join(D)+'\n'); print(len(D),'lines ->',sys.argv[2])
