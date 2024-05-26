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

#### Step 2: Run The Script

Please run `inference.sh` as the following the format:
```bash
bash inference.sh {path to the video folder} {path to tht output folder} {source} {max_frames}
```

- `path to the video folder`: It is the path to the folder that you store the `.mp4` files
- `path to the output folder`: It is the path to the folder that you store the output splitted videos
- `source`: It indicated the source of the video. It is used for the metadata.
- `max_frames`: Number of frames for preprocessing the video. Due to the GPU limited, we will cut the video into smaller segments. Please adjust it based on GPU. Default is 1000

Here is the example:
```bash
bash inference.sh ./video ./video_output Youtube 500
```
