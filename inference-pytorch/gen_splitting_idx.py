import torch
from transnetv2_pytorch import TransNetV2
import numpy as np
import sys
import os
from PIL import Image
import argparse
from tqdm import tqdm
import shutil


def prepare_model():
    model = TransNetV2()
    state_dict = torch.load("transnetv2-pytorch-weights.pth")
    model.load_state_dict(state_dict)
    model.eval().cuda()
    return model


def predictions_to_scenes(predictions: np.ndarray, threshold: float = 0.5):
    predictions = (predictions > threshold).astype(np.uint8)

    scenes = []
    t, t_prev, start = -1, 0, 0
    for i, t in enumerate(predictions):
        if t_prev == 1 and t == 0:
            start = i
        if t_prev == 0 and t == 1 and i != 0:
            scenes.append([start, i])
        t_prev = t
    if t == 0:
        scenes.append([start, i])

    # just fix if all predictions are 1
    if len(scenes) == 0:
        return np.array([[0, len(predictions) - 1]], dtype=np.int32)

    return np.array(scenes, dtype=np.int32)

def split_range(start, end, range_limit):
    ranges = []
    current_start = start
    current_end = 0
    while current_end < end:
        current_end = min(current_start + range_limit - 1, end)
        ranges.append((current_start, current_end))
        current_start = (current_start + current_end) // 2 + 1
    
    return ranges

def load_video_frame(frames_folder, frame_height=27, frame_width=48, range=10000):
    # Get the list of frame files and sort them
    frame_files = sorted([f for f in os.listdir(frames_folder) if f.endswith(".jpg")])
    num_frames = len(frame_files)

    ranges = split_range(0, num_frames-1, range)

    video_images_list = []
    for (start_frame, end_frame) in ranges:
        num_frames_in_range = end_frame - start_frame + 1

        # Initialize a tensor to hold the video frames
        video_images = torch.zeros(
            1, num_frames_in_range, frame_height, frame_width, 3, dtype=torch.uint8
        )

        frame_files_in_range = frame_files[start_frame:end_frame+1]
        for i, frame_file in enumerate(frame_files_in_range):
            frame_path = os.path.join(frames_folder, frame_file)
            image = Image.open(frame_path).convert("RGB")  # Ensure image is in RGB format
            image = image.resize((frame_width, frame_height))
            frame = np.array(image)
            video_images[0, i] = torch.tensor(frame, dtype=torch.uint8)

        video_images_list.append(video_images)

    return video_images_list, ranges


def main(args):
    input_folder = args.input
    assert os.path.isdir(input_folder), f"Input folder {input_folder} does not exist"

    output_folder = args.output
    # Clear the output folder
    os.makedirs(output_folder, exist_ok=True)

    model = prepare_model()

    range = args.range

    skipped_videos = []
    error_message_path = os.path.join(output_folder, "error_message.txt")
    # if os.path.exists(error_message_path):
    #     os.remove(error_message_path)
    # open(error_message_path, "w").close()

    progress_bar = tqdm(os.listdir(input_folder))
    for video_name in progress_bar:
        frame_folder = os.path.join(input_folder, video_name)
        if not os.path.isdir(frame_folder):
            continue

        if len(os.listdir(frame_folder)) == 0:
            print(f"Skipping {video_name} as the folder is empty")
            skipped_videos.append(video_name)
            # with open(error_message_path, "a") as f:
            #     f.write(f"{video_name}: Empty folder\n")
            continue

        progress_bar.set_description(f"Processing {video_name}")
        # frames = load_video_frame(frame_folder, range=range)
        video_images_list, ranges = load_video_frame(frame_folder, range=range)

        try:
            output_list = []
            for video_images, (start_frame, _) in zip(video_images_list, ranges):
                single_frame_pred, _ = model(video_images.cuda())

                single_frame_pred = torch.sigmoid(single_frame_pred).detach().cpu().numpy()

                output = predictions_to_scenes(single_frame_pred[0])
                output += start_frame
                output_list.append(output)
                video_images.cpu()
                torch.cuda.empty_cache()

            output_np = np.concatenate(output_list, axis=0)
            output_file = os.path.join(output_folder, f"{video_name}.txt")
            np.savetxt(output_file, output_np, fmt="%d")

        except RuntimeError as e:
            if "out of memory" in str(e):
                print("CUDA out of memory. Skipping this iteration.")
                torch.cuda.empty_cache()  # Clear GPU memory cache
                skipped_videos.append(video_name)
                # with open(error_message_path, "a") as f:
                #     f.write(f"{video_name}: {str(e)}\n")
            else:
                raise e  # Re-raise the exception if it is not related to CUDA OOM
        

    if len(skipped_videos) > 0:
        print(f"Skipped videos due to CUDA out of memory: {skipped_videos}")
    print(f"Output files are saved in {output_folder}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split video into scenes")
    parser.add_argument("--input", type=str, help="Path to the video file")
    parser.add_argument("--output", type=str, help="Path to the output folder")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Threshold for scene change detection. Default 0.5",
    )
    parser.add_argument("--range", type=int, default=1500, help="Range limit")
    args = parser.parse_args()
    main(args)