# import cv2
from meterviewer import types as T

PartImg = T.NpImage  # reading area of meter image


def cut_img(img: T.NpImage, rect: T.Rect) -> PartImg:
  """根据 rect 裁剪 img"""
  cropped_image = img[rect.ymin : rect.ymax, rect.xmin : rect.xmax]
  return cropped_image
