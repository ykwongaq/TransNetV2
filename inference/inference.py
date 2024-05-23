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

        print(f"Processing video {video_filename}...")
        video_path = os.path.join(video_folder, video_filename)
        start_time = time.time()
        _, single_frame_predictions, _ = model.predict_video(video_path)
        end_time = time.time()
        prediction_time = end_time - start_time
        print(f"Prediction time: {prediction_time} seconds")

        current_time = time.strftime("%d%m%H:%M:%S")
        video_info_output_path = os.path.join(
            args.output, f"video_info_{current_time}.txt"
        )
        with open(video_info_output_path, "a") as f:
            f.write(
                f"file '{video_filename}' to video_{scene_id}.mp4 with time {prediction_time}\n"
            )

        if single_frame_predictions is None:
            print(f"Failed to process video {video_path}")
            failing_video.append(video_path)
            continue

        scenes = model.predictions_to_scenes(single_frame_predictions)
        scenes = scenes.tolist()

        video_filename = video_filename.split(".")[0] + ".txt"
        output_path = os.path.join(args.output, video_filename)
        os.makedirs(args.output, exist_ok=True)

        print(f"Saving scenes to {output_path}...")
        with open(output_path, "w") as f:
            for start_frame, end_frame in scenes:
                f.write(f"{start_frame} {end_frame}\n")

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
