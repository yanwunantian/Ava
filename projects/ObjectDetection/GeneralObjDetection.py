# USAGE
# python deep_learning_with_opencv.py --image images/jemma.png --prototxt bvlc_googlenet.prototxt --model bvlc_googlenet.caffemodel --labels synset_words.txt

# import the necessary packages
import numpy as np
import argparse
import cv2
import base64
import json
import sys
sys.path.insert(0, "../Utility/")   # used to import files from other folder dir in project
from utilities import *

class GeneralImageClassification(object):
        
    def __init__(self, prototxt, model):
        self.image = "../../res/genimg.jpg"
        self.prototxt = prototxt
        self.model = model
        self.labels = "../../res/synset_words.txt"


    def run_classification(self):
        net = cv2.dnn.readNetFromCaffe(self.prototxt, self.model)
        image = cv2.imread(self.image)
        rows = open(self.labels).read().strip().split("\n")
        classes = [r[r.find(" ") + 1:].split(",")[0] for r in rows]
        newimg = cv2.resize(image,(224,224))
        blob = cv2.dnn.blobFromImage(newimg, 1, (224, 224), (104, 117, 123))      
        net.setInput(blob)
        preds = net.forward()
        idxs = np.argsort(preds[0])[::-1][:5]
        for (i, idx) in enumerate(idxs):	
	    if i == 0:
	        output = "Label: {}, {:.2f}%".format(classes[idx],
		    preds[0][idx] * 100)
		cv2.putText(image, output, (5, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
       # print("[INFO] {}. label: {}, probability: {:.5}".format(i + 1,classes[idx], preds[0][idx]))        
	       # cv2.imshow("Image", image)
               #cv2.waitKey(0)
	#print("[INFO] {}. label: {}, probability: {:.5}".format(i + 1,
		#classes[idx], preds[0][idx]))
            print("[INFO] {}. label: {}, probability: {:.5}".format(i + 1,classes[idx], preds[0][idx]))
        #cv2.imshow("Image", image)
        #cv2.waitKey(0)

    def run_images(self):
        print("Consuming messages form 'target2'\n")
        consumer = Consumer.initialize("target2")
        for m in consumer:
            json_data = m.value     
            print("\n Running object detection model against the frames")
            json_data_parsed = json.loads(json_data)
            frame = Utilities.decodeFrame(json_data_parsed)     # TODO: change this so that we dont have to write a file. 
            fh = open(self.image, "wb")
            fh.write(frame)
            fh.close()                        
            self.run_classification()
            Utilities.exportJson(json_data, "general")    # currently exports same data read from kafka topic until we know what to add from this component
         
            
            
    
def main():
    prototxt = "../../res/bvlc_googlenet.prototxt"
    model = "../../res/bvlc_googlenet.caffemodel"
    obj = GeneralImageClassification(prototxt,model)
    obj.run_images()



if __name__=="__main__":
        main()