import os, subprocess, numpy as np, torch, cv2
VIDEO=os.path.expanduser(os.environ.get("VIDEO","")); W=960   # SAM 2 working width
def read_frames(video,a,b):
    cap=cv2.VideoCapture(video); cap.set(cv2.CAP_PROP_POS_FRAMES,a); out=[]
    for _ in range(a,b+1):
        ok,im=cap.read()
        if not ok: break
        out.append(cv2.cvtColor(cv2.resize(im,(W,int(im.shape[0]*W/im.shape[1]))),cv2.COLOR_BGR2RGB))
    return out
def preview(frame,path):   # gridded frame in 960-wide coords for picking click points
    im=cv2.cvtColor(read_frames(VIDEO,frame,frame)[0],cv2.COLOR_RGB2BGR)
    for x in range(0,im.shape[1],80): cv2.line(im,(x,0),(x,im.shape[0]),(0,255,255),1); cv2.putText(im,str(x),(x+2,12),0,0.4,(0,255,255),1)
    for y in range(0,im.shape[0],60): cv2.line(im,(0,y),(im.shape[1],y),(0,255,255),1); cv2.putText(im,str(y),(2,y-2),0,0.4,(0,255,255),1)
    cv2.imwrite(path,im)
