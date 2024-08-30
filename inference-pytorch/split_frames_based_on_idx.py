import os
import argparse

from tqdm import tqdm
from typing import List, Tuple

def extract_ranges(idx_file: str) -> List[Tuple[int, int]]:
    ranges = []

    with open(idx_file, "r") as file:
        for line in file:
            start, end = line.strip().split(" ")
            ranges.append((int(start), int(end)))

    # Sort the ranges by start, then by end in descending order
    sorted_ranges = sorted(ranges, key=lambda x: (x[0], -x[1]))

    # Initialize the result list with the first range
    filtered_ranges = [sorted_ranges[0]]

    # Iterate over the sorted ranges starting from the second element
    for current in sorted_ranges[1:]:
        last_range = filtered_ranges[-1]
        
        # If the current range is not fully contained in the last range, add it to the result list
        if current[1] > last_range[1]:
            filtered_ranges.append(current)

    return filtered_ranges

def main(args):
    frame_dir = args.frame_dir
    idx_dir = args.idx_dir
    output_dir = args.output_dir
    
    scene_names = os.listdir(frame_dir)
    scene_names.sort()

    frame_folders = [os.path.join(frame_dir, f) for f in os.listdir(frame_dir) if os.path.isdir(os.path.join(frame_dir, f))]
    frame_folders.sort()

    idx_files = []
    for scene_name in scene_names: 
        idx_file = os.path.join(idx_dir, scene_name + ".txt")
        idx_files.append(idx_file)

    for idx_file, frame_folder in tqdm(list(zip(idx_files, frame_folders))):

        if not os.path.exists(idx_file):
            continue

        ranges = extract_ranges(idx_file)
        frame_file_list = [os.path.join(frame_folder, f) for f in os.listdir(frame_folder) if os.path.isfile(os.path.join(frame_folder, f))]
        frame_file_list.sort()

        scene_name = os.path.basename(frame_folder)

        for idx, idx_range in enumerate(ranges):

            output_folder = os.path.join(output_dir, scene_name, f"Folder{idx+1}")
            os.makedirs(output_folder, exist_ok=True)
            
            start, end = idx_range

            for i in range(start, end+1):
                frame_file = frame_file_list[i]
                output_file = os.path.join(output_folder, os.path.basename(frame_file))

                if os.path.lexists(output_file):
                    os.remove(output_file)
                    
                os.symlink(frame_file, output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split frames based on index")
    parser.add_argument("--frame_dir", type=str, default="/homes/david/datasets/youtube_underwater_videos/frames", help="Path to the directory containing frame folders")
    parser.add_argument("--idx_dir", type=str, default="/homes/david/datasets/youtube_underwater_videos/split_frame_idx", help="Path to the directory containing index files")
    parser.add_argument("--output_dir", type=str, default="/homes/david/datasets/youtube_underwater_videos/split_frames", help="Path to the output directory")

    args = parser.parse_args()
    main(args)

