import os
import argparse
from tqdm import tqdm

def main(args):
    frame_dir = args.frames_dir
    first_frames_dir = args.first_frames_dir

    output_folder = os.path.join(args.output_folder, args.output_folder_name)
    os.makedirs(output_folder, exist_ok=True)

    output_dataset_folder = os.path.join(output_folder, "dataset")
    os.makedirs(output_dataset_folder, exist_ok=True)

    output_first_frame_folder = os.path.join(output_folder, "first_frames")
    os.makedirs(output_first_frame_folder, exist_ok=True)

    # Copy all the first frame to the output_frame_folder
    print(f"Copying first frames from {first_frames_dir} to {output_first_frame_folder}")
    for image_name in tqdm(os.listdir(first_frames_dir)):
        image_path = os.path.join(first_frames_dir, image_name)
        output_image_path = os.path.join(output_first_frame_folder, image_name)
        os.symlink(image_path, output_image_path)

    items = []
    for image_name in os.listdir(first_frames_dir):
        image_name = os.path.splitext(image_name)[0]
        split = image_name.split("###")
        video_name, folder_name, _ = split
        items.append((video_name, folder_name))

    print(f"Copying frames from {frame_dir} to {output_dataset_folder}")
    for (video_name, folder_name) in tqdm(items):
        frame_folder = os.path.join(frame_dir, video_name, folder_name)
        output_frame_folder = os.path.join(output_dataset_folder, video_name, folder_name)
        os.makedirs(output_frame_folder, exist_ok=True)

        for frame_name in os.listdir(frame_folder):
            frame_path = os.path.join(frame_folder, frame_name)
            output_frame_path = os.path.join(output_frame_folder, frame_name)
            os.symlink(frame_path, output_frame_path)

    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames_dir", type=str, default="/homes/david/datasets/youtube_underwater_videos/split_frames")
    parser.add_argument("--first_frames_dir", type=str, default="/homes/david/datasets/youtube_underwater_videos/first_frames/first_frames")
    parser.add_argument("--output_folder", type=str, default="/homes/david/datasets/youtube_underwater_videos/first_frames")
    parser.add_argument("--output_folder_name", type=str, required=True)

    args = parser.parse_args()
    main(args)