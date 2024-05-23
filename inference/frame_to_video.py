import cv2
import os

import argparse
from tqdm import tqdm


def frame_to_video(input_dir, output_path, fps=30):
    # Get list of images in the folder
    images = [
        img
        for img in os.listdir(input_dir)
        if img.endswith(".jpg") or img.endswith(".png")
    ]
    images.sort()  # Ensure the images are sorted

    # Read the first image to get the dimensions
    frame = cv2.imread(os.path.join(input_dir, images[0]))
    height, width, layers = frame.shape

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # Codec for mp4 format
    video = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    for image in images:
        img_path = os.path.join(input_dir, image)
        frame = cv2.imread(img_path)
        video.write(frame)

    # Release the VideoWriter
    video.release()


def main(args):
    input_dir = args.input_dir
    assert os.path.isdir(input_dir), f"{input_dir} is not a directory"

    output_dir = args.output_dir
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    dps = args.fps
    assert dps > 0, f"fps must be greater than 0"

    if args.is_dir:
        for dirname in tqdm(os.listdir(input_dir), desc="Converting to video"):
            dir_path = os.path.join(input_dir, dirname)
            output_video_name = f"{dirname}.mp4"
            output_video_path = os.path.join(output_dir, output_video_name)
            frame_to_video(dir_path, output_video_path, fps=dps)
    else:
        dir_name = args.input_dir.split("/")[-1]
        output_video_name = f"{dir_name}.mp4"
        output_video_path = os.path.join(output_dir, output_video_name)
        frame_to_video(input_dir, output_video_path, fps=dps)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_dir", type=str, required=True, help="Directory of frames"
    )
    parser.add_argument(
        "--output_dir", type=str, required=True, help="Directory of output video"
    )
    parser.add_argument(
        "--fps", type=int, default=30, help="Frame per second. Default=30"
    )
    parser.add_argument(
        "--is_dir",
        action="store_true",
        help="True if input_dir is directory of folder containing frames. False if input_dir is single frame",
    )
    args = parser.parse_args()
    main(args)
