# USAGE
# python deep_learning_with_opencv.py --image images/jemma.png --prototxt bvlc_googlenet.prototxt --model bvlc_googlenet.caffemodel --labels synset_words.txt

# import the necessary packages
import sys
sys.path.insert(0, "../Utility/")   # used to import files from other folder dir in project
from utilities import *
 
 
# changed class from ImageClassification to ObjectDetection
# uses the code for  FrameLabeling as a base
class GeneralObjectDetection(object):
    # added missing variables (classes, confidenceThreshold)
    # extracted and added variables for size, mean_subtraction, and scalar
    def __init__(self, prototxt, model, labels):
        """ Constructor - Initalizes prototxt and model """
        self.image = None
        self.prototxt = prototxt
        self.model = model
        self.classes = open(labels).read().strip().split('\n')
        self.size = 300
        self.mean_subtraction = 0.007843
        self.scalar = 127.5
        self.confidenceThreshold = 0.3
 
 
    # removed all code related to label, or creating bounding boxes
    # added json_data_parsed to method parameters
    def run_object_detection(self, json_data_parsed):
        """ Runs the general object detection on a frame """
        net = cv2.dnn.readNetFromCaffe(self.prototxt, self.model)
        # replaced values with variables
        blob = cv2.dnn.blobFromImage(cv2.resize(self.image, (self.size, self.size)), self.mean_subtraction, (self.size, self.size), self.scalar)
        net.setInput(blob)
        detections = net.forward()
        # create a list to store found labels
        label_list = []
        for i in np.arange(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > self.confidenceThreshold:
                idx = int(detections[0, 0, i, 1])
                if idx >= 1 and idx <= 20:      # display the prediction
                    label = "{}: {:.2f}%".format(self.classes[idx], confidence*100)
                    print("[INFO] {}".format(label))
                    label_list.append(label)    # adds new label to label_list
        if label_list:   # if label_list is not empty (meaning gen objects wer found), then add to json
            json_data_parsed['GeneralObjectsDetected'] = label_list  # appends label_list to JSON data
 
    def run_images(self):
        """ Runs each image through the general object detection """
        print("Consuming messages from 'target2'\n")
        consumer = Consumer.initialize("target2")
        for m in consumer:
            json_data = m.value     
            json_data_parsed = json.loads(json_data)
            print("\n Running General Object Det against frame: " + str(json_data_parsed['frameNum']) + "\n")
            frame = Utilities.decodeFrameForObjectDetection(json_data_parsed)   # this utility method will not only decode the b64 string, but also prepare the image to be compatible with opencv
            self.image = frame
            self.run_object_detection(json_data_parsed)
            json_data = json.dumps(json_data_parsed)  # writes json_data_parsed to the JSON file
            Utilities.storeJson(json_data, "../../res/FramesMetadataGenObjDetections/" + json_data_parsed['videoName'] + "_Metadata.txt")
            Utilities.exportJson(json_data, "general")   # exports JSON file with the list of labels for the identified objects
        consumer.close()
        print("\nGeneral Object Detection consumer closed!")
 
 
def main():
    """ Auto run main method """
    parser = argparse.ArgumentParser()   # Parser to parse arguments passed
    parser.add_argument('--model', type=str, help='Path to prototxt file')
    parser.add_argument('--model_prototxt', type=str, help='Path to model')
    parser.add_argument("--labels", type=str, help="path to list of class labels")
    args = parser.parse_args()
    obj = GeneralObjectDetection(args.model_prototxt, args.model, args.labels)
    obj.run_images()
 
 
if __name__=="__main__":
        main()
 
