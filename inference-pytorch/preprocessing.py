import os
import argparse
import shutil
import ffmpeg
import time
import math

from tqdm import tqdm


def get_video_metadata(video_path):
    probe = ffmpeg.probe(video_path)
    video_stream = next(
        stream for stream in probe["streams"] if stream["codec_type"] == "video"
    )
    duration = float(video_stream["duration"])
    frame_rate = eval(video_stream["r_frame_rate"])
    return duration, frame_rate


def preprocess_video(video_path, output_dir, frames_per_chunk):
    # Get the video duration and frame rate
    duration, frame_rate = get_video_metadata(video_path)

    # Calculate the chunk duration
    chunk_duration = frames_per_chunk / frame_rate
    num_chunks = int(duration / chunk_duration)

    if num_chunks == 1:
        # If the video is shorter than the chunk duration, just copy the video
        output_path = os.path.join(output_dir, os.path.basename(video_path))
        shutil.copyfile(video_path, output_path)
        return

    print(f"Splitting video into {math.ceil(duration / chunk_duration)} chunks")
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Get the original video name without the extension
    original_name = os.path.splitext(os.path.basename(video_path))[0]

    # Split the video into chunks
    for i in range(num_chunks):
        print(f"Processing chunk {i}/{num_chunks}")
        start_time = i * chunk_duration
        output_path = os.path.join(output_dir, f"{original_name}_{i}.mp4")
        (
            ffmpeg.input(video_path, ss=start_time, t=chunk_duration)
            .output(output_path)
            .global_args("-loglevel", "error")
            .run()  # Show only error messages
        )

    # Handle the last chunk if there's remaining video
    remaining_duration = duration - num_chunks * chunk_duration
    if remaining_duration > 0:
        print(f"Processing chunk {num_chunks}/{num_chunks}")
        start_time = num_chunks * chunk_duration
        output_path = os.path.join(output_dir, f"{original_name}_{num_chunks}.mp4")
        (
            ffmpeg.input(video_path, ss=start_time, t=remaining_duration)
            .output(output_path)
            .global_args("-loglevel", "error")
            .run()  # Show only error messages
        )


def main(args):

    input_folder = args.input
    print(f"Processing video: {args.input}")
    assert os.path.exists(input_folder), f"Input folder {input_folder} does not exist"

    max_frames = args.max_frames
    assert max_frames > 0, "max_frames should be greater than 0"

    output_folder = args.output

    os.makedirs(output_folder, exist_ok=True)

    for video_filename in os.listdir(input_folder):
        print(f"Preprocessing video: {video_filename}")
        video_path = os.path.join(input_folder, video_filename)
        start_time = time.time()
        preprocess_video(video_path, output_folder, max_frames)
        end_time = time.time()
        print(f"Video preprocessed in {end_time - start_time:.2f} seconds")
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
        default=500,
        help="Maximum number of frames to be extracted. Default 3000",
    )
    args = parser.parse_args()
    main(args)
