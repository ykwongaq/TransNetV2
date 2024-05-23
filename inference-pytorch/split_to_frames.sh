#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <input_folder> <output_folder>"
    exit 1
fi

input_folder="$1"
output_folder="$2"
conversion_file="$output_folder/conversion.txt"

# Create the output folder if it doesn't exist
mkdir -p "$output_folder"

# Initialize the conversion file
echo "" > "$conversion_file"

# Initialize the video counter
counter=0

# Loop through all mp4 files in the input folder
for video_file in "$input_folder"/*.mp4; do
    # Check if there are no mp4 files in the input folder
    if [ ! -e "$video_file" ]; then
        echo "No mp4 files found in the input folder."
        exit 1
    fi

    # Get the base name of the video file
    base_name=$(basename "$video_file" .mp4)
    
    # Create a folder for the frames of this video with the name video_<counter>
    frames_folder="$output_folder/video_$counter"
    mkdir -p "$frames_folder"
    
    # Print the progress message
    echo "Processing $video_file ..."
    
    # Run ffmpeg to convert the video to frames with fps set to 30 and non-verbose output
    ffmpeg -loglevel error -i "$video_file" -vf "scale=48:27,fps=30" -pix_fmt rgb24 "$frames_folder/frame_%05d.jpg"
    
    # Print completion message for the current video
    echo "Completed processing $video_file. Frames saved in $frames_folder."
    
    # Append the original and new names to the conversion file
    echo "$base_name video_$counter" >> "$conversion_file"
    
    # Increment the counter
    counter=$((counter + 1))
done

echo "All conversions complete. Filename conversions saved in $conversion_file."
