


#python newobd.py --

# import the necessary packages
import numpy as np
import argparse
import cv2
import base64
import json
import sys
sys.path.insert(0, "../DataTransfer")
from kafka_manager import *
from kafka_producer import *


class GeneralObjectDetection(object):

    def __init__(self, prototxt, model):
        self.image = "../../res/image1.jpg"
        self.prototxt = prototxt
        self.model = model
        self.classes = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]
        self.colors = np.random.uniform(0, 255, size=(len(self.classes), 3))
        self.confidence = 0.3
        
    def run_caffe_detection(self):       
        net = cv2.dnn.readNetFromCaffe(self.prototxt, self.model)
        img=cv2.imread(self.image)
        (h, w) = img.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(img, (300, 300)), 0.007843, (300, 300), 127.5)
        net.setInput(blob)
        detections = net.forward()
        for i in np.arange(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > self.confidence:
                idx = int(detections[0, 0, i, 1])
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                # display the prediction
                label = "{}: {:.2f}%".format(self.classes[idx], confidence*100)
                print("[INFO] {}".format(label))
                cv2.rectangle(img, (startX, startY), (endX, endY), self.colors[idx], 2)
                y = startY - 15 if startY - 15 > 15 else startY + 15
                cv2.putText(img, label, (startX, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors[idx], 2)
        cv2.imshow("output", img)
        cv2.waitKey(0)

             
    
        
                    
                    
    def run_images(self):        
        json_data_list = Consumer.pull_jsons("bay")
        for i in range(len(json_data_list)):
           json_data_parsed = json.loads(json_data_list[i])
            frameBase64 = json_data_parsed["imageBase64"]            
            frame = base64.b64decode(frameBase64)
            fh = open(self.image, "wb")
            fh.write(frame)
            fh.close()                        
            self.run_caffe_detection()
           

    
def main():
    
    prototxt = "../../res/MobileNetSSD_deploy.prototxt.txt"
    model = "../../res/MobileNetSSD_deploy.caffemodel"    
    obj = GeneralObjectDetection(prototxt,model)
    obj.run_images()  
    
if __name__=="__main__":
    main()
