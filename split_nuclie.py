import os
import uuid
import cv2
import numpy as np
from PIL import Image
from skimage import exposure
from tifffile import imread
import json 

def thresholdImage(img):
  kernelSize = (23,23)
  blockSize = 1 / 8 * img.shape[0] / 2 * 2 + 1
  if blockSize < 1:
    blockSize = img.shape[0] / 2 * 2 + 1
  if int(blockSize)%2!=0: blockSize = blockSize-1
  blurred = cv2.GaussianBlur(img, (11, 11), 0)
  return cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY, int(blockSize)+1, 7)

def fillGaps(img):  
  for i in range(3):
    kernelSize = (7,7)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, kernelSize)
    img= cv2.morphologyEx(img, cv2.MORPH_GRADIENT, kernel)
  return img


# pass points as tuples
def cal(p1,p2):
  return np.linalg.norm(np.array(p1) - np.array(p2))

pt_img_map = {}
imgcnt = 0 

def save_image(x,y,res,imgcnt):

  save_img, closest_dist = -1,float('inf')
  if len(pt_img_map) ==0:
    save_img = [f"nuclie{imgcnt:02d}",0]
    imgcnt+=1
    pt_img_map[(x,y)] = save_img

  else:
    closest_pt = None
    for pt,file in pt_img_map.items():
      dist = cal(pt,(x,y))

      if closest_dist > dist:
        closest_dist,closest_pt = dist,pt

    if closest_dist >400:
      # write to that
      save_img = [f"nuclie{imgcnt:02d}",0]
      imgcnt+=1
      pt_img_map[(x,y)] = save_img
    else:
      pt_img_map[closest_pt] = [pt_img_map[closest_pt][0],pt_img_map[closest_pt][1]+1]
      save_img = pt_img_map[closest_pt]
      x,y=closest_pt
      

  path = "./nuclie_align_ROI1_membrane_1700/"+save_img[0]
  if not os.path.exists(path):
    from pathlib import Path
    Path(path).mkdir(parents=True, exist_ok=True)

  w = 1700
  cx = max(0,x - w/2)
  cy = max(0,y - w/2)
  ht,wt = res.shape
  if cx+w >wt: cx = cx - (cx+w - wt)
  if cy+w >ht: cy = cy - (cy+w - ht)

  res = res[int(cy):int(cy+w), int(cx):int(cx+w)]
  cv2.imwrite(path+"/"+ f"{save_img[1]:05d}"+".jpg", res)
  print(f'{path}/{save_img[1]:05d} position:{(x,y)}')
  return imgcnt

def scale_contour(cnt, scale):
    M = cv2.moments(cnt)
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])

    cnt_norm = cnt - [cx, cy]
    cnt_scaled = cnt_norm * scale
    cnt_scaled = cnt_scaled + [cx, cy]
    cnt_scaled = cnt_scaled.astype(np.int32)

    return cnt_scaled


# increase the number here to accomodate more frames 
ref = imread('/data/FIBSEM/VK1_ROI1/ROI1_4x4x4nm_200kHz_align_tif/VK1_ROI1_4x4x4nm.5093.tif')
for i in range(6800):
  image_id = f"{i:04d}"
  print(f"Processing frame {image_id}")
  #path = '/data/FIBSEM/VK1_ROI3/ROI3/VK_ROI3/ROI3_4x4x4nm_200kHz_raw'
  path = '/data/FIBSEM/VK1_ROI1/ROI1_4x4x4nm_200kHz_align_tif/VK1_ROI1_4x4x4nm.'
  img = imread(path+image_id+'.tif')
  for i in range(1): 
      try:
          #img = exposure.match_histograms(img, ref)
          im = np.array(img).astype(np.uint8)
          maxarea = 0 
          maxContour= 0 
          
          contours, hierarchy = cv2.findContours(image=fillGaps(thresholdImage(im)), mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
  
          for c in range(len(contours)):
            if cv2.contourArea(contours[c]) > 300000 and cv2.contourArea(contours[c])<800000:
              if len(cv2.approxPolyDP(contours[c],0.01*cv2.arcLength(contours[c],True),True))>8:
                contours =list(contours)
                contours[c] = scale_contour(contours[c],1.1)   
                mask = np.zeros(im.shape, np.uint8)
                cv2.drawContours(mask, contours,c, (255,255,255),cv2.FILLED)
                res = cv2.bitwise_and(im,im,mask = mask)
                #x, y, width, height = cv2.boundingRect(contours[c])
                #roi = res[y: y + height, x: x + width]
                M = cv2.moments(contours[c])
                cX,cY = int(M["m10"] / M["m00"]),int(M["m01"] / M["m00"])
                imgcnt = save_image(cX,cY,res,imgcnt)    
      except EOFError:
          print("error")
          break

json = json.dumps(pt_img_map)
f = open("roi3.json","w")
f.write(json)
f.close()
