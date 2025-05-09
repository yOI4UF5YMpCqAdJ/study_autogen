import ddddocr
from pathlib import Path
import cv2

ocr = ddddocr.DdddOcr(det=True)
with open("yzm.png", 'rb') as f:
    image = f.read()

bboxes = ocr.detection(image)

im = cv2.imread("yzm.png")

for bbox in bboxes:
    x1, y1, x2, y2 = bbox
    im = cv2.rectangle(im, (x1, y1), (x2, y2), color=(0, 0, 255), thickness=2)

cv2.imwrite("result.jpg", im)

print(bboxes)
# image = open("yzm.png", "rb").read()
# result = ocr.classification(image)
# print(result)