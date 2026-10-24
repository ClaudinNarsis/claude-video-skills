#!/usr/bin/env python3
"""Zoom-whip transition on hard joins. Usage: transitions.py in.mp4 out.mp4 "1.5:1,3.733:1,18.967:0.5"
Each entry = time of the FIRST frame of the new shot : strength (1 = full, 0.5 = jump cut inside one shot).
6 frames (0.2 s): outgoing shot zooms in up to 10% with growing horizontal blur; incoming shot settles out. Audio is copied.
Find cuts first: ffmpeg -i in.mp4 -vf "select='gt(scene,0.08)',metadata=print:key=lavfi.scene_score" -an -f null -
(scores > 0.7 = hard cuts, ~0.3 = jump cut; ignore hits from caption exits / scrolling screens). Needs python with cv2+numpy (matte venv)."""
import subprocess,sys,os,cv2,numpy as np
SRC,OUT=sys.argv[1],sys.argv[2]
CUTS={float(a):float(b) for a,b in (x.split(':') for x in sys.argv[3].split(','))}
S_OUT=[0.25,0.55,1.0]; S_IN=[1.0,0.55,0.25]; SC=float(os.environ.get('TRANS_SCALE','1'))   # taste dial: 1 = as shipped, 0.6 = lighter
ZOOM=0.10*SC; BLUR=int(60*SC)
plan={}
for t,k in CUTS.items():
    c=round(t*30)
    for i,s in enumerate(S_OUT): plan[c-3+i]=s*k
    for i,s in enumerate(S_IN): plan[c+i]=s*k
cap=cv2.VideoCapture(SRC); fps=cap.get(cv2.CAP_PROP_FPS); W,H=int(cap.get(3)),int(cap.get(4))
ff=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(fps),"-i","-","-i",SRC,"-map","0:v","-map","1:a?",
 "-c:v","libx264","-crf","16","-pix_fmt","yuv420p","-colorspace","bt709","-color_primaries","bt709","-color_trc","bt709","-c:a","copy","-shortest",OUT],stdin=subprocess.PIPE)
f=0
while True:
    ok,img=cap.read()
    if not ok: break
    s=plan.get(f)
    if s:
        img=cv2.warpAffine(img,cv2.getRotationMatrix2D((W/2,H/2),0,1+ZOOM*s),(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
        L=int(1+BLUR*s)|1
        if L>2: img=cv2.filter2D(img,-1,np.full((1,L),1.0/L,np.float32),borderType=cv2.BORDER_REFLECT)
    ff.stdin.write(img.tobytes()); f+=1
ff.stdin.close(); ff.wait(); print("wrote",OUT,f,"frames")
