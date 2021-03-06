#!/bin/sh

cd ../etc/
python clean_frame_metadata_logs.py

cd ../bin
./start_kafka_server.sh
wait

cd ../etc/
python clean_and_clear_topics.py

cd ../projects/ObjectDetection/
python FrameLabeling.py --model "../../res/MobileNetSSD_deploy.caffemodel" \
                        --model_prototxt "../../res/MobileNetSSD_deploy.prototxt.txt" \
                        --labels "../../res/labels.txt" &
pids[0]=$!

python GeneralObjDetection.py --model "../../res/MobileNetSSD_deploy.caffemodel" \
                              --model_prototxt "../../res/MobileNetSSD_deploy.prototxt.txt" \
                              --labels "../../res/labels.txt" &
#python GeneralObjDetectionYOLO.py &
pids[1]=$!

python TargettedObjectDetectionProcess.py --graph "../../res/TfModel/output_graph.pb" \
                                          --labels "../../res/TfModel/output_labels.txt" \
                                          --input_layer "Placeholder" \
                                          --output_layer "final_result" \
                                          --input_height 224 \
                                          --input_width 224 &
pids[2]=$!

cd ../ETL/
python ETLProcess.py --video "../../res/Videos/vid.mp4"

for pid in ${pids[*]}; do
    wait $pid
done

cd ../../etc/
python clean-pyc.py


