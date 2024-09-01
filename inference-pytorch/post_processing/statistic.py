import os

folder = "/homes/david/datasets/youtube_underwater_videos/split_frames"

total_events = 0
for video_name in os.listdir(folder):
    video_folder = os.path.join(folder, video_name)
    num_events = len(os.listdir(video_folder))
    total_events += num_events

print(total_events)