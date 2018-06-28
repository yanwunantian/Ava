from label_image import main as labelImage
import os
import cv2
import base64
import json
import numpy as np
import sys
import numpy as np
import tensorflow as tf
sys.path.insert(0, "../Utility/")   # used to import files from other folder dir in project
from utilities import *



graph = "../../res/TfModel/output_graph.pb"
labels = "../../res/TfModel/output_labels.txt"
input_layer = "Placeholder"
output_layer = "final_result"
input_height = 224   # Neccessary input_height for mobilnet model
input_width = 224    # Neccessary input_wifth for mobilenet model

    
def main():
    print("\nConsuming messages from 'framefeeder'")
    json_data_list = Consumer.pull_jsons("framefeeder")   # pull jsons from kafka topic into list for processing
    print("\nRunning labelImage against all frames ")
    for i in range(len(json_data_list)):
        json_data_parsed = json.loads(json_data_list[i])   # loads json data into a parsed string (back to dict)
        frameBase64 = json_data_parsed["imageBase64"]   # extracts base64 string of image (frame)
        frame = base64.b64decode(frameBase64)         # decodes base64 image
        frameAsTensor = tf.image.decode_jpeg(frame, channels=3)   # convert frame to Tensor as string
        print("FrameNum: " + str(i))    # display which frame is being targeted object detected against
        confidenceStat = labelImage(graph, labels, input_layer, output_layer, input_height, input_width, frameAsTensor)    # tests frame for targeted object
        if confidenceStat != None:     # if the target object was found within the threshold confidence, append that information to the JSON file. 
            json_data_parsed['foundTargetWithConfidence'] = str(confidenceStat)
            json_data_list[i] = json.dumps(json_data_parsed)
    Utilities.storeJson(json_data_list, "../../res/frameMetadataListTargetOBJD.txt")    # Store updated metadata Jsons locally
    Utilities.exportJson(json_data_list, "target")    # export updated Json files to kafka topic 'target'
    

if __name__ == "__main__":
    main()