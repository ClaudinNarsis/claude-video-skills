import sys
"""Background blur behind a SAM 2 person mask. VIDEO=in.mp4 python matte_blur.py SIGMA OUT.mp4 [LIMIT]
Edit SEGS (frame ranges that contain the person; skip cutaways) and BAN (px row below which blur starts, to keep a burnt-in banner sharp).
Sigma 10 = 'a bit'. Fills small holes (mic) and smooths the mask over 3 frames."""
from matte_common import *
SIGMA=float(sys.argv[1]) if len(sys.argv)>1 else 10.0
OUT=sys.argv[2] if len(sys.argv)>2 else "work/bgblur.mp4"
LIMIT=int(sys.argv[3]) if len(sys.argv)>3 else 10**9
SEGS=[(0,292),(480,978)]; BAN=552   # banner bottom in 1080x1920 px
def seg_of(f):
    for a,b in SEGS:
        if a<=f<=b: return (a,b)
def fill_holes(m,maxarea=9000):
    b=(m>0.5).astype(np.uint8); b=cv2.morphologyEx(b,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
    cs,h=cv2.findContours(b,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE); out=b.copy()
    if h is not None:
        for c,hh in zip(cs,h[0]):
            if hh[3]>=0 and cv2.contourArea(c)<maxarea: cv2.drawContours(out,[c],-1,1,-1)
    return np.maximum(out.astype(np.float32),m)
def mask(f,seg,shape):
    a,b=seg; acc=0; wsum=0
    for d,w in ((-1,1),(0,2),(1,1)):
        g=min(max(f+d,a),b); m=fill_holes(cv2.imread(f"work/masks/subject/{g:05d}.png",0).astype(np.float32)/255)
        acc=acc+w*m; wsum+=w
    m=cv2.resize(acc/wsum,(shape[1],shape[0]),interpolation=cv2.INTER_LINEAR)
    return cv2.GaussianBlur(m,(0,0),2.2)
cap=cv2.VideoCapture(VIDEO); fps=cap.get(cv2.CAP_PROP_FPS); Wd,Ht=int(cap.get(3)),int(cap.get(4)); n=int(cap.get(7))
ff=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","bgr24","-s",f"{Wd}x{Ht}","-r",str(fps),"-i","-","-i",VIDEO,
  "-map","0:v","-map","1:a?","-c:v","libx264","-crf","16","-pix_fmt","yuv420p","-colorspace","bt709","-color_primaries","bt709","-color_trc","bt709","-c:a","copy","-shortest",OUT],stdin=subprocess.PIPE)
for f in range(min(n,LIMIT)):
    ok,img=cap.read()
    if not ok: break
    s=seg_of(f)
    if s:
        m=mask(f,s,img.shape)[...,None]
        low=img[BAN:].astype(np.float32); bl=cv2.GaussianBlur(low,(0,0),SIGMA,borderType=cv2.BORDER_REFLECT)
        bg=img.astype(np.float32).copy(); bg[BAN:]=bl
        out=img.astype(np.float32)*m+bg*(1-m)
        img=np.clip(out,0,255).astype(np.uint8)
    ff.stdin.write(img.tobytes())
ff.stdin.close(); ff.wait(); print("wrote",OUT)
