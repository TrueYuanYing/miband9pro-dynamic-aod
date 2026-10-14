"""Generate original geometric demo frames; no cartoon or vendor assets."""
import argparse, math
from pathlib import Path
from PIL import Image, ImageDraw

def main():
    parser=argparse.ArgumentParser();parser.add_argument('output',type=Path);args=parser.parse_args()
    if args.output.exists():parser.error('Choose a new directory to preserve existing frames')
    args.output.mkdir(parents=True)
    for index in range(69):
        im=Image.new('RGBA',(336,334),(0,0,0,0));d=ImageDraw.Draw(im)
        if index<17:
            x=70+index*8;y=60+index*7
            d.ellipse((x-18,y-18,x+18,y+18),outline=(255,255,255,255),width=3)
        elif index<33:
            radius=12+(index-17)*6;points=[]
            for j in range(24):
                angle=j*math.pi/12;r=radius if j%2==0 else radius*.45
                points.append((168+math.cos(angle)*r,170+math.sin(angle)*r))
            d.polygon(points,fill=(255,255,255,230))
        else:
            radius=90+(index-33)*.25
            d.ellipse((168-radius,170-radius,168+radius,170+radius),outline=(255,255,255,255),width=4)
            d.line((168,170,168,120),fill='white',width=5);d.line((168,170,205,188),fill='white',width=5)
        im.save(args.output/f'{index:03d}.png')

if __name__=='__main__':main()
