import cv2, numpy as np, subprocess, imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

W,H,FPS = 1080,1920,24
FB = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

SEGS = [(0,73,"Muddy paws,\nat the door"),
        (73,146,"A fine water mist\nas you brush"),
        (146,219,"For cats who\ndislike being brushed")]

def text_layer(txt, size=68, font=FB, fill=(255,255,255,255)):
    f = ImageFont.truetype(font, size)
    lines = txt.split("\n")
    d0 = ImageDraw.Draw(Image.new("RGBA",(1,1)))
    lh = size + 18
    widths = [d0.textbbox((0,0),l,font=f)[2] for l in lines]
    img = Image.new("RGBA",(W,H),(0,0,0,0)); d = ImageDraw.Draw(img)
    y = H - 300 - lh*len(lines)
    for l,wd in zip(lines,widths):
        d.text(((W-wd)//2, y), l, font=f, fill=fill)
        y += lh
    return np.array(img)

def scrim():
    g = np.zeros((H,W,4), np.uint8)
    start = H-620
    for y in range(start,H):
        a = int(190 * ((y-start)/(H-start))**0.8)
        g[y,:,3] = a
    return g

SCRIM = scrim()
LAYERS = {i:text_layer(t) for i,(a,b,t) in enumerate(SEGS)}

def over(bgr, rgba, alpha=1.0):
    a = (rgba[:,:,3:4].astype(np.float32)/255.0)*alpha
    fg = rgba[:,:,2::-1].astype(np.float32)          # RGB -> BGR
    return (bgr.astype(np.float32)*(1-a) + fg*a).astype(np.uint8)

cap = cv2.VideoCapture('peluma-reel-3.mp4')
frames = []
i = 0
while True:
    ok,f = cap.read()
    if not ok: break
    frames.append(f); i += 1
cap.release()

out_frames = []
for idx,f in enumerate(frames):
    seg = next(k for k,(a,b,_) in enumerate(SEGS) if a <= idx < b)
    a,b,_ = SEGS[seg]
    local = idx - a
    fade = min(1.0, local/8.0) * min(1.0, (b-a-local)/6.0)
    fade = max(0.0, fade)
    fr = over(f, SCRIM, fade)
    fr = over(fr, LAYERS[seg], fade)
    out_frames.append(fr)

# end card
logo = Image.open('logo-src.png').convert('RGBA'); logo = logo.crop(logo.getbbox())
lw = 620; logo = logo.resize((lw, round(logo.size[1]*lw/logo.size[0])), Image.LANCZOS)
card = Image.new('RGB',(W,H),(255,255,255))
card.paste(logo, ((W-lw)//2, H//2-300), logo)
d = ImageDraw.Draw(card)
f1 = ImageFont.truetype(FB,64); f2 = ImageFont.truetype(FR,40)
t1 = "pelumapets.com"; t2 = "Free US shipping"
d.text(((W-d.textbbox((0,0),t1,font=f1)[2])//2, H//2+40), t1, font=f1, fill=(0,0,0))
d.text(((W-d.textbbox((0,0),t2,font=f2)[2])//2, H//2+150), t2, font=f2, fill=(90,90,90))
card_bgr = cv2.cvtColor(np.array(card), cv2.COLOR_RGB2BGR)
last = out_frames[-1]
for k in range(10):                       # crossfade into the card
    a = (k+1)/10
    out_frames.append((last.astype(np.float32)*(1-a)+card_bgr.astype(np.float32)*a).astype(np.uint8))
out_frames += [card_bgr]*34               # hold ~1.4s

ff = imageio_ffmpeg.get_ffmpeg_exe()
p = subprocess.Popen([ff,'-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}',
    '-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','slow','-crf','19',
    '-pix_fmt','yuv420p','-movflags','+faststart','peluma-reel-4.mp4'],
    stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
for f in out_frames: p.stdin.write(f.tobytes())
p.stdin.close(); err = p.stderr.read().decode()[-400:]; p.wait()
print("frames:", len(out_frames), "dur:", round(len(out_frames)/FPS,2),"s rc:",p.returncode)
print(err if p.returncode else "")
