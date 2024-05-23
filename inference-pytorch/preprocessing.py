import cv2
import os
import argparse
import shutil

from tqdm import tqdm
import time
import ffmpeg
import subprocess

from concurrent.futures import ThreadPoolExecutor


def split_segment(input_file, start_time, segment_duration, output_file):
    ffmpeg.input(input_file, ss=start_time, t=segment_duration).output(
        output_file
    ).global_args("-loglevel", "error").run(overwrite_output=True)


def preprocess_video(input_file, output_folder, frames_per_segment=3000):

    # Get video info
    probe = ffmpeg.probe(input_file)
    video_stream = next(
        (stream for stream in probe["streams"] if stream["codec_type"] == "video"), None
    )

    if video_stream is None:
        raise Exception("No video stream found")

    frame_rate = eval(
        video_stream["r_frame_rate"]
    )  # Convert frame rate string to float
    duration = float(video_stream["duration"])  # Total duration of the video in seconds
    total_frames = int(frame_rate * duration)  # Calculate total frames

    segment_duration = (
        frames_per_segment / frame_rate
    )  # Duration of each segment in seconds

    segment_count = total_frames // frames_per_segment + (
        1 if total_frames % frames_per_segment else 0
    )

    if segment_count == 1:
        output_file = os.path.join(output_folder, f"{os.path.basename(input_file)}")
        shutil.copy(input_file, output_file)
        return

    print(f"Splitting video into {segment_count} segments")
    num_workers = args.num_workers
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        for i in range(segment_count):
            start_time = i * segment_duration
            output_file = os.path.join(
                output_folder,
                f"{os.path.splitext(os.path.basename(input_file))[0]}_{i:03d}.mp4",
            )
            futures.append(
                executor.submit(
                    split_segment, input_file, start_time, segment_duration, output_file
                )
            )

        for future in futures:
            future.result()  # Wait for all threads to complete


def main(args):

    input_folder = args.input
    print(f"Processing video: {args.input}")
    assert os.path.exists(input_folder), f"Input folder {input_folder} does not exist"

    max_frames = args.max_frames
    assert max_frames > 0, "max_frames should be greater than 0"

    output_folder = args.output

    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder)

    for video_filename in os.listdir(input_folder):

        print(f"Preprocessing video: {video_filename}")
        video_path = os.path.join(input_folder, video_filename)
        preprocess_video(video_path, output_folder, max_frames)
    print("All video is processed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocess the video data")
    parser.add_argument(
        "--input", type=str, required=True, help="Path to the video file"
    )
    parser.add_argument(
        "--output", type=str, required=True, help="Path to the output directory"
    )
    parser.add_argument(
        "--max_frames",
        type=int,
        default=3000,
        help="Maximum number of frames to be extracted. Default 3000",
    )
    parser.add_argument(
        "--num_workers", type=int, default=4, help="Number of workers. Default 4"
    )
    args = parser.parse_args()
    main(args)
