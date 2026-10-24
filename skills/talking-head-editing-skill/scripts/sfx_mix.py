#!/usr/bin/env python3
"""Place sound-effects kit sounds on cues (no music). Usage: sfx_mix.py in.mp4 cues.json out_raw.mp4   (needs ffmpeg-full on PATH)
Then: python3 $FF/scripts/loudness.py out_raw.mp4 -I -15 --tp -4.4 -o final.mp4   (Reels check wants -14 +/- 2 LUFS)
cues.json = [{"t":1.5,"type":"scene_cut|click|appear|reveal","gain_adj":-6?,"riser_len":2.0?}]
 scene_cut -> whoosh starting 2 frames BEFORE t; click; appear -> pop; reveal -> impact; riser_len adds a riser that ENDS at t.
Gains (dB) are tuned so SFX are audible ~8 dB under speech: whoosh -3, click -2, pop -8, impact -4, riser -10. sound_pass.py needs a music file; this does not."""
import json,subprocess,sys,os
K=os.path.expanduser('~/.claude/skills/sound-effects/sfx/kit/'); SRC,CUES,OUT=sys.argv[1:4]
G={'whoosh':-3,'click':-2,'pop':-8,'impact':-4,'riser':-10}; CAT={'scene_cut':'whoosh','click':'click','appear':'pop','reveal':'impact'}
RL=2.014271; EARLY=2/30; ev=[]
for i,c in enumerate(json.load(open(CUES))):
    cat=CAT[c['type']]; t=c['t']-(EARLY if cat=='whoosh' else 0)
    ev.append((t,cat,G[cat]+c.get('gain_adj',0),i))
    if 'riser_len' in c: ev.append((c['t']-RL,'riser',G['riser'],i))
json.dump([dict(start=round(a,3),cat=b,gain=g,cue=d) for a,b,g,d in ev],open(os.path.splitext(OUT)[0]+'_events.json','w'),indent=1)
cmd=['ffmpeg','-loglevel','error','-y','-i',SRC]; fc=[]; labs=['[0:a]']
for n,(s,cat,g,_) in enumerate(ev,1):
    cmd+=['-i',K+cat+'.ogg']; ms=int(max(s,0)*1000)
    fc.append(f'[{n}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={g}dB,adelay={ms}|{ms}[s{n}]'); labs.append(f'[s{n}]')
fc.append(''.join(labs)+f'amix=inputs={len(labs)}:normalize=0:duration=first,alimiter=limit=0.97:level=0[a]')
cmd+=['-filter_complex',';'.join(fc),'-map','0:v','-map','[a]','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',OUT]
subprocess.run(cmd,check=True); print('wrote',OUT,len(ev),'events')
