import argparse
import os
import json
import ffmpeg
import datetime

from tqdm import tqdm


def read_video_info(video_path: str):
    """
    Read the video file and return the metadata
    """
    metadata = {}
    probe = ffmpeg.probe(video_path)
    video_stream = next(
        (stream for stream in probe["streams"] if stream["codec_type"] == "video"),
        None,
    )
    if not video_stream:
        raise ValueError("No video stream found")

    duration = float(video_stream["duration"])
    fps = eval(video_stream["avg_frame_rate"])
    width = int(video_stream["width"])
    height = int(video_stream["height"])

    metadata["duration"] = duration
    metadata["fps"] = fps
    metadata["width"] = width
    metadata["height"] = height
    return metadata


def read_split_file(split_path: str):
    """
    Read the split file, which is a text file, and return the list of timestamps, which is a 2d array
    """
    with open(split_path, "r") as f:
        lines = f.readlines()
        segment_frames = []
        for line in lines:
            start_frame, end_frame = line.strip().split(" ")
            start_frame = int(start_frame)
            end_frame = int(end_frame)
            segment_frames.append([start_frame, end_frame])
        return segment_frames


def main(args):

    input_video_folder = args.input_video
    assert os.path.isdir(
        input_video_folder
    ), f"Input folder {input_video_folder} does not exist"

    input_split_folder = args.input_split
    assert os.path.isdir(
        input_split_folder
    ), f"Input folder {input_split_folder} does not exist"

    input_video_files = set(
        os.path.splitext(filename)[0] for filename in os.listdir(input_video_folder)
    )
    input_split_files = set(
        os.path.splitext(filename)[0] for filename in os.listdir(input_split_folder)
    )

    output_folder = args.output
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    if input_video_files != input_split_files:
        missing_files_in_split = input_video_files - input_split_files
        if missing_files_in_split:
            print("Files missing in input_split_folder:")
            for filename in missing_files_in_split:
                print(filename)

        missing_files_in_video = input_split_files - input_video_files
        if missing_files_in_video:
            print("Files missing in input_video_folder:")
            for filename in missing_files_in_video:
                print(filename)
        raise ValueError("Input files do not have the same filenames")

    IDX = args.starting_idx

    metadata_list = []

    outter_bar = tqdm(os.listdir(input_video_folder))
    for video_filename in outter_bar:
        outter_bar.set_description(f"Processing {video_filename}")
        split_filename = os.path.splitext(video_filename)[0] + ".txt"
        video_path = os.path.join(input_video_folder, video_filename)
        split_path = os.path.join(input_split_folder, split_filename)

        # Collect metadata
        probe = ffmpeg.probe(video_path)
        video_stream = next(
            (stream for stream in probe["streams"] if stream["codec_type"] == "video"),
            None,
        )
        if not video_stream:
            raise ValueError("No video stream found")

        fps = eval(video_stream["avg_frame_rate"])
        original_name = os.path.splitext(os.path.basename(video_path))[0]
        original_name = original_name.split("_")[0]
        original_name = f"{original_name}.mp4"
        extension = os.path.splitext(os.path.basename(video_path))[1].replace(".", "")
        current_time = datetime.datetime.now().strftime("%Y:%m:%d %H:%M:%S")

        segment_frames = read_split_file(split_path)

        inner_bar = tqdm(enumerate(segment_frames), leave=False)
        for i, (start_frame, end_frame) in inner_bar:
            inner_bar.set_description(f"Processing {video_filename} with segment {i}")
            idx_str = str(IDX).zfill(8)
            output_filename = f"{idx_str}.mp4"
            output_path = os.path.join(output_folder, output_filename)

            start_time = start_frame / fps
            duration = (end_frame - start_frame + 1) / fps

            (
                ffmpeg.input(video_path, ss=start_time, t=duration)
                .output(output_path)
                .global_args("-loglevel", "error")
                .run()
            )

            IDX += 1

            metadata = read_video_info(output_path)
            metadata["source"] = args.source
            metadata["original_name"] = original_name
            metadata["filename"] = output_filename
            metadata["caption"] = ""
            metadata["caption_attributes"] = []
            metadata["created_time"] = current_time
            metadata["ext"] = extension
            metadata["path"] = ""

            metadata_list.append(metadata)

    json_output_path = os.path.join(output_folder, "metadata.json")
    with open(json_output_path, "w") as f:
        json.dump(metadata_list, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocess the video data")
    parser.add_argument(
        "--input_video", type=str, required=True, help="Path to the video file"
    )
    parser.add_argument(
        "--input_split", type=str, required=True, help="Path to the split video file"
    )
    parser.add_argument(
        "--output", type=str, required=True, help="Path to the output directory"
    )
    parser.add_argument(
        "--source", type=str, required=True, help="Path to the source directory"
    )
    parser.add_argument(
        "--starting_idx",
        type=int,
        default=0,
        help="Starting index for the output file. Default 0",
    )
    args = parser.parse_args()
    main(args)
