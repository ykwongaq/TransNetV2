import ffmpeg
import os
import argparse


def main(args):
    input_folder = args.input
    assert os.path.isdir(input_folder), f"Input folder {input_folder} does not exist"

    output_folder = args.output
    if not os.path.exists(args.output):
        os.makedirs(args.output)

    for filename in os.listdir(input_folder):
        if filename.endswith(".mp4"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, os.path.splitext(filename)[0])

            print(f"Extracting frames from {filename} ...")
            if not os.path.exists(output_path):
                os.makedirs(output_path)

            try:
                (
                    ffmpeg.input(input_path)
                    .output(
                        os.path.join(output_path, "%08d.jpg"),
                        vf="scale=48:27",
                        pix_fmt="rgb24",
                    )
                    .global_args("-loglevel", "error")
                    .run()
                )
                print(f"Frames from {filename} have been extracted to {output_path}")
            except ffmpeg.Error as e:
                print(f"Error extracting frames from {filename}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocess the video data")
    parser.add_argument(
        "--input", type=str, required=True, help="Path to the video file"
    )
    parser.add_argument(
        "--output", type=str, required=True, help="Path to the output directory"
    )
    args = parser.parse_args()
    main(args)
