import os
import subprocess
import argparse
import cv2

def read_processed_file(process_file):
    processed_videos = []
    with open(process_file, "r") as f:
        for line in f:
            processed_videos.append(line.strip())
    return processed_videos

def save_processed_file(process_file, processed_video):
    with open(process_file, "a") as f:
        f.write(f"{processed_video}\n")

def main(args):
    frame_folder = args.frame_folder

    output_folder = args.output_folder
    os.makedirs(output_folder, exist_ok=True)

    first_frame_folder = os.path.join(output_folder, "first_frames")
    os.makedirs(first_frame_folder, exist_ok=True)

    process_file = os.path.join(output_folder, "process.txt")
    processed_videos = read_processed_file(process_file)
    
    video_names = os.listdir(frame_folder)
    video_names.sort()

    for video_name in video_names:
        video_folder = os.path.join(frame_folder, video_name)
        if not os.path.isdir(video_folder):
            continue

        dir_names = os.listdir(video_folder)
        dir_names.sort()
        for dir_name in dir_names:
            frame_dir = os.path.join(video_folder, dir_name)
            if not os.path.isdir(frame_dir):
                continue

            frame_files = os.listdir(frame_dir)
            frame_files.sort()

            output_file = os.path.join(first_frame_folder, f"{video_name}###{dir_name}###{frame_files[0]}")
            if output_file in processed_videos:
                print(f"Skip {output_file}")
                continue
            
            if len(frame_files) < 10:
                print(f"Skip {output_file} as the number of frames is too low")
                continue
                
            first_frame_file = os.path.join(frame_dir, frame_files[0])
            last_frame_file = os.path.join(frame_dir, frame_files[-1])

            first_frame = cv2.imread(first_frame_file)
            last_frame = cv2.imread(last_frame_file)

            height, width, _ = first_frame.shape
            if height <= 720 or width <= 720:
                print(f"Skip {output_file} as the resolution is too low")
                continue

            print(f"Number of frames: {len(frame_files)}")

            temp_output_file = os.path.join(output_folder, "temp.jpg")
            combined_frame = cv2.hconcat([first_frame, last_frame])
            cv2.imwrite(temp_output_file, combined_frame)

            subprocess.run(["code", temp_output_file])

            response = input("Do you want to save this frame? (Enter to save): ")
            if response == "":
                print(f"Save {output_file}")
                os.symlink(first_frame_file, output_file)

            save_processed_file(process_file, output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Select the first frame of the video")
    parser.add_argument("--frame_folder", type=str, default="/homes/david/datasets/youtube_underwater_videos/split_frames", help="Path to the folder containing all the frame subfolders")
    parser.add_argument("--output_folder", type=str, default="/homes/david/datasets/youtube_underwater_videos/first_frames", help="Path to the output folder")
    
    args = parser.parse_args()
    main(args)
    