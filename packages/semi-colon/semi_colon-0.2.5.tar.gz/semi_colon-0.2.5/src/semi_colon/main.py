import math
import numpy as np
import matplotlib.pyplot as plt
import urllib.request, os
from urllib.parse import urlparse
import zipfile, tarfile


def imshows(imgs, rows=1, cols=None, bgr=True, figsize=None, axis=False):
  #모든 imgs는 dict 형태가 되게 강제한다.
  if isinstance(imgs, np.ndarray): #NumPy 1개
    size = 1
    imgs = zip([''], [imgs])
  elif isinstance(imgs, (list, tuple)): #List, Tuple
    size = len(imgs)
    imgs = zip(['' for _ in imgs], imgs)
  elif isinstance(imgs, dict): #Dict
    size = len(imgs)
    imgs = imgs.items()

  #행열 설정, 1행이면 n열, 행이 여러개면 열은 이미지 수/행으로 설정
  if rows == 1:
    cols = size  
  elif cols== None:
    cols = math.ceil(size/rows)

  #전체 이미지 표시
  if figsize:
    plt.figure(figsize=figsize)

  for i , (title, img) in enumerate(imgs, start=1):
    plt.subplot(rows, cols, i)
    plt.title(title)
    if img.ndim == 2:
        plt.imshow(img, cmap='gray')
    elif img.ndim == 3:
        if bgr:
            plt.imshow(img[:,:,::-1])
        else:
            plt.imshow(img)
    if axis == False:
      plt.xticks([]); plt.yticks([])
  plt.show();



def download(url, dir=None, file_name=None, extract=False):
  if file_name is None:
    parsed = urlparse(url)
    path = parsed.path

    if parsed.netloc == 'github.com':
      split_str = 'master/'
      if split_str in parsed.path:
        path = path.split(split_str, 1)[-1]  # 'master/' 이후 부분 추출
      if not dir:
        dir = os.path.dirname(path)

    if not dir:
      dir='.'

    if not file_name:
        file_name = os.path.basename(path)
  os.makedirs(dir, exist_ok=True)

  to=os.path.join(dir, file_name)
  urllib.request.urlretrieve(url, to)
  print(f"{to} 파일이 다운로드되었습니다.")

  if extract:
    ext = os.path.splitext(to)[-1]

    if '.zip' == ext :
      with zipfile.ZipFile(to, 'r') as zip:
        ret = zip.extractall(dir)
        print(f'압축풀기:{to}, {ret}')
    elif '.gz' == ext:
      with tarfile.open(to) as tar:
        tar.extractall(dir)

  return to