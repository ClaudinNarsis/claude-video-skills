import sys,time,json
"""VIDEO=in.mp4 python matte_sep.py '{"start":0,"end":292,"out":"work/masks/subject","box":[x0,y0,x1,y1],"pts":[[x,y],...],"lbl":[1,..,0]}'
Coords are 960-wide. ALWAYS give a box around the whole person + several points (face, hair, clothes, hands, held mic) and 2 negatives; test 10 frames first.
venv needs: torch torchvision transformers opencv-python-headless pillow numpy. Apple Silicon: sam2.1-hiera-base-plus on MPS, ~1.5 s/frame."""
from matte_common import *
from transformers import Sam2VideoModel, Sam2VideoProcessor
MODEL="facebook/sam2.1-hiera-base-plus"; dev="mps"
model=Sam2VideoModel.from_pretrained(MODEL).to(dev).eval(); proc=Sam2VideoProcessor.from_pretrained(MODEL)
def chunk(frames,points=None,labels=None,mask=None,box=None):
    H=frames[0].shape[0]
    s=proc.init_video_session(video=frames,inference_device=dev,video_storage_device="cpu",inference_state_device="cpu",dtype=torch.float32)
    if mask is None: proc.add_inputs_to_inference_session(inference_session=s,frame_idx=0,obj_ids=1,input_points=[[points]],input_labels=[[labels]],**({'input_boxes':[[box]]} if box else {}))
    else: proc.add_inputs_to_inference_session(inference_session=s,frame_idx=0,obj_ids=1,input_masks=mask.astype(np.uint8))
    res={}
    with torch.inference_mode():
        model(inference_session=s,frame_idx=0)
        for o in model.propagate_in_video_iterator(s,start_frame_idx=0):
            m=proc.post_process_masks([o.pred_masks],original_sizes=[[H,W]],binarize=True)[0]
            res[o.frame_idx]=m.squeeze().cpu().numpy().astype(bool)
    return res
def separate(start,end,pts,lbl,ch=60,outdir="work/masks/subject",box=None):
    os.makedirs(outdir,exist_ok=True); a,seed=start,None
    while a<end:
        b=min(end,a+ch); fr=read_frames(VIDEO,a,b); t=time.time()
        r=chunk(fr,points=pts,labels=lbl,box=box) if seed is None else chunk(fr,mask=seed)
        for k,m in r.items(): cv2.imwrite(f"{outdir}/{a+k:05d}.png",m.astype(np.uint8)*255)
        seed,a=r[len(fr)-1],b
        print(f"frames {a-len(fr)+1}..{b} done in {time.time()-t:.0f}s",flush=True)
if __name__=="__main__":
    seg=json.loads(sys.argv[1]); separate(seg["start"],seg["end"],seg["pts"],seg["lbl"],outdir=seg.get("out","work/masks/subject"),box=seg.get("box"))
