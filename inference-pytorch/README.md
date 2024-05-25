# Pytorch implementation of TransNet V2

This is Pytorch reimplementation of the TransNetV2 model.
It should produce identical results as the Tensorflow version.
The code is for inference only, there is no plan to release Pytorch implementation of the training code.

See [tensorflow inference readme](https://github.com/soCzech/TransNetV2/tree/master/inference)
for details and code how to get correctly predictions for a whole video file.

### INSTALL REQUIREMENTS
```bash
pip install tensorflow==2.1  # needed for model weights conversion
conda install pytorch=1.7.1 cudatoolkit=10.1 -c pytorch
```

### CONVERT WEIGHTS
Firstly tensorflow weights file needs to be converted into pytorch weights file.
```bash
python convert_weights.py [--test]
```
The pytorch weights are saved into *transnetv2-pytorch-weights.pth* file.

### Split Video

To split a video into segments, you need to run four Python scripts.

#### Step 1: Prepare dataset

First, gather all your video (.mp4) files into a single folder, such as `./video`.

It is advisable to process your videos in batches to avoid issues that may occur mid-process. For example, you could process 20 videos at a time.

#### Step 2: Preprocessing

To prevent CUDA out-of-memory errors, split the video into smaller segments as a preprocessing step.

Please run the `preprocessing.py` with the following input:

```bash
python preprocessing.py --input {path to video folder} --output {path to the output folder} --max_frames {maximum frames in each segment}
```

Here is an example
```bash
python preprocessing.py --input ./video --output ./video_preprocessed --max_frames 500
```

The default `max_frames` is 500

#### Step 3: Generate Frames

To optimize GPU usage, convert the preprocessed videos into frames (a sequence of images). These frames are intermediate products and can be deleted after the process is complete.

Please run the `mp4_to_frames.py` with the following output:
```bash
python mp4_to_frames.py --input {path to preprocessed folder} --output {path to output folder}
```

Here is an example:
```bash
python mp4_to_frames.py --input ./video_preprocesssed --output ./video_frames
```

#### Step 4: Generate Splitting Frames

Next, generate the splitting information, which includes the starting and ending frames for each segment. This information will be saved in text files.

Please run the `split_video.py`:

```bash
python split_video.py --input {path to the frames folder} --output {path to the output folder}
```

Here is an example
```bash
python split_video.py --input ./video_frames --output ./video_splitting_info
```


#### Step 5: Generate Splitted Videos

Finally, we can generate the splitted video and metajson using `gen_splitted_video.py`

```bash
python --input_video {path to the preprocessed folder} --input_split {path to the splitting info} --output {path to the output folder} --source {video source} --starting_idx {starting index of the output video}
```

`--source`  specifies the source of the video for metadata purposes.
`--starting_idx` sets the naming start index for the output videos. The default is 0, so the first video will be named 00000000.mp4.

Here is the example
```bash
python --input_video ./video_preprocessed --input_split ./video_splitting_info --output ./video_ouptut --source Youtube
```