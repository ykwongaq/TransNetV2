#!/bin/bash

# Get the directory name and other parameters from the command line arguments
input=$1
output=$2
source=$3
max_frames=${4:-1000}  # Default value is 1000 if not provided

# Check if directory exists
if [ ! -d "$input" ]; then
    echo "Directory $input does not exist."
    exit 1
fi

# Find and run all Python files in the directory
echo ====================step1====================
python ./preprocessing.py --input $input/video --output $output/video_preprocessed --max_frames $max_frames

echo ====================step2====================
python ./mp4_to_frames.py --input $output/video_preprocessed --output $output/video_frames

echo ====================step3====================
python ./split_video.py --input $output/video_frames --output $output/video_splitting_info

echo ====================step4====================
python ./gen_splitted_video.py --input_video $output/video_preprocessed --input_split $output/video_splitting_info --output $output/video_output --source $source
