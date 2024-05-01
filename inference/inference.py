import os
import numpy as np
import tensorflow as tf
import ffmpeg
import argparse

from transnetv2 import TransNetV2

def clear_dir_contents(dir_path):
    # Clear files in dir_path
    for file_name in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)

def main(args):
    video_folder = args.dir
    assert os.path.isdir(video_folder), f"ERROR: {video_folder} is not a directory."

    print(f"Processing video folder: {video_folder}")

    model = TransNetV2(args.weights)

    video_idx = 0

    for video_filename in os.listdir( video_folder):
        if not video_filename.endswith(".mp4"):
            continue
        
        
        video_path = os.path.join(video_folder, video_filename)
        _, single_frame_predictions, _ = model.predict_video(video_path)
        scenes = model.predictions_to_scenes(single_frame_predictions)
        scenes = scenes.tolist()
        print(scenes)

        for (start_frame, end_frame) in scenes:
            video_name = f"video_{video_idx}"
            video_idx += 1
            output_video_folder = os.path.join(args.output, video_name)
            os.makedirs(output_video_folder, exist_ok=True)
            clear_dir_contents(output_video_folder)
            # Clear files in video_output_folder
            
            # Save frames
            print(f"Saving frames to {output_video_folder}...")
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(stream, f"{output_video_folder}/%06d.jpg", loglevel="quiet", start_number=0, vf=f'select=\'between(n,{start_frame},{end_frame})\'')
            ffmpeg.run(stream, overwrite_output=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=str, default="../video", help="path to video folder to process")
    parser.add_argument("--output", type=str, default="../video_output", help="path to output folder")
    parser.add_argument("--weights", type=str, default=None, help="path to TransNet V2 weights, tries to infer the location if not specified")
    parser.add_argument
    args = parser.parse_args()
    main(args)