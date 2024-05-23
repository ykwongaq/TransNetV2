import cv2
import os
import argparse
import shutil

from tqdm import tqdm


def preprocess_video(video_path, output_folder, max_frames=3000):

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    num_segments = total_frames // max_frames + (
        1 if total_frames % max_frames != 0 else 0
    )

    if num_segments == 1:
        shutil.copy(video_path, output_folder)
        return

    print(f"Splitting video into {num_segments} segments")
    for segment in range(num_segments):
        output_file = os.path.join(
            output_folder, f"{os.path.basename(video_path)}_{segment}.mp4"
        )
        out = cv2.VideoWriter(
            output_file,
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (frame_width, frame_height),
        )

        for frame_num in range(max_frames):
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)

        out.release()

    cap.release()


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
    args = parser.parse_args()
    main(args)
