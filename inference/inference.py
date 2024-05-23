import os
import numpy as np
import tensorflow as tf
import ffmpeg
import argparse

from transnetv2 import TransNetV2
import time


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

    failing_video = []

    scene_id = 0
    for video_filename in os.listdir(video_folder):
        if not video_filename.endswith(".mp4"):
            continue
        
            
        video_path = os.path.join(video_folder, video_filename)
        start_time = time.time()
        _, single_frame_predictions, _ = model.predict_video(video_path)
        end_time = time.time()
        prediction_time = end_time - start_time
        print(f"Prediction time: {prediction_time} seconds")

        with open("video_list.txt", "a") as f:
            f.write(f"file '{video_filename}' to video_{scene_id}.mp4 with time {prediction_time}\n")

        if single_frame_predictions is None:
            print(f"Failed to process video {video_path}")
            failing_video.append(video_path)
            continue

        scenes = model.predictions_to_scenes(single_frame_predictions)
        scenes = scenes.tolist()

        os.makedirs(args.output, exist_ok=True)
        split_id = 0
        for idx, (start_frame, end_frame) in enumerate(scenes):
            # video_name = video_filename.split(".")[0]
            # video_name = f"{video_name}_{idx}"
            video_name = f"video_{scene_id}_{split_id}"
            output_video_folder = os.path.join(args.output, video_name)
            split_id += 1
            os.makedirs(output_video_folder, exist_ok=True)

            # Clear files in video_output_folder
            clear_dir_contents(output_video_folder)

            # Save frames
            print(f"Saving frames to {output_video_folder}...")
            try:
                stream = ffmpeg.input(video_path)
                stream = ffmpeg.output(
                    stream,
                    f"{output_video_folder}/%06d.jpg",
                    loglevel="quiet",
                    start_number=0,
                    vf=f"select='between(n,{start_frame},{end_frame})'",
                    r=args.fps,
                )
                ffmpeg.run(stream, overwrite_output=True)
            except Exception as e:
                print(
                    f"Failed to save frames for video {video_path} with error message: {e}"
                )
                failing_video.append(video_path)
                continue
        scene_id += 1

    print(f"Finished")
    if len(failing_video) > 0:
        print(f"Failed to process {len(failing_video)} videos:")
        for video_path in failing_video:
            print(video_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dir", type=str, default="../video", help="path to video folder to process"
    )
    parser.add_argument(
        "--output", type=str, default="../video_output", help="path to output folder"
    )
    parser.add_argument(
        "--weights",
        type=str,
        default=None,
        help="path to TransNet V2 weights, tries to infer the location if not specified",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=30,
        help="frame per second for the output video. Default is 30 fps.",
    )
    args = parser.parse_args()
    main(args)
