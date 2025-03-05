# Using LightlyTrain with YOLO

This tutorial demonstrates how to pre-train a YOLO model using `lightly-train` and then fine-tune it for object detection using the `ultralytics` framework.

```{warning}
Using Ultralytics models might require a commercial Ultralytics license. See the
[Ultralytics website](https://www.ultralytics.com/license) for more information.
```

## Install Dependencies

Install the required packages:

```bash
pip install lightly-train[ultralytics]
```

## Download the Dataset

For the purpose of this tutorial, we use the [Fruits Detection](https://github.com/lightly-ai/dataset_fruits_detection) dataset.

You can clone it from GitHub:

```bash
git clone https://github.com/lightly-ai/dataset_fruits_detection.git ./Fruits-detection
```

All the detections in `Fruits-detection/train/labels` are in YOLO detection format.
The content of `Fruits-detection/data.yaml` is the following:

```yaml
names:
  - Apple
  - Banana
  - Grape
  - Orange
  - Pineapple
  - Watermelon
nc: 6
test: test/images
train: train/images
val: valid/images
```

```{note}
Labels are not required for self-supervised pre-training. We will use the labels only for finetuning.
```

## Pre-train and Fine-tune

We will use `lightly-train` to pre-train a YOLO model using self-supervised learning.

The following scripts will:

- Initialize a YOLOv8s model with random weights.
- Pre-train the YOLOv8s model on the Fruits Detection train set using DINO self-supervised learning.
- Export the pre-trained YOLOv8s model.
- Fine-tune the pre-trained model on the Fruits Detection dataset using labels.

```python
# pretrain_yolo.py
from ultralytics import YOLO

import lightly_train

if __name__ == "__main__":
    model = YOLO("yolov8s.yaml")
    # model = YOLO("yolov8s.pt") # Uncomment this to start from a COCO checkpoint.

    # Pre-train with lightly-train.
    lightly_train.train(
        out="out/my_experiment",                # Output directory.
        data="Fruits-detection/train/images",   # Directory with images.
        model=model,                            # Pass the YOLO model.
        method="dino",                          # Self-supervised learning method.
        epochs=100,                             # Adjust epochs for faster training.
        batch_size=64,                          # Adjust batch size based on hardware.
    )

```

```python
# finetune_yolo.py
from pathlib import Path

from ultralytics import YOLO

if __name__ == "__main__":
    # Load the exported model.
    model = YOLO("out/my_experiment/exported_models/exported_last.pt")

    # Fine-tune with ultralytics.
    data = Path("Fruits-detection/data.yaml").absolute()
    model.train(data=data, epochs=100)
```

```{note}
The exported model can also be used from the command line.

Use: `yolo detect train model=out/my_experiment/exported_models/exported_last.pt" data="Fruits-detection/data.yaml" epochs=100`.
```

Congratulations! You have successfully pre-trained a model using `lightly-train` and fine-tuned it for object detection using `ultralytics`.

For more advanced options, explore the [Python API](#lightly-train) and [Ultralytics documentation](https://docs.ultralytics.com).

## Next Steps

- Experiment with different self-supervised learning methods in `lightly-train`.
- Try various YOLO models (`YOLOv5`, `YOLOv6`, `YOLOv11`).
- Use the pre-trained model for other tasks, like {ref}`image embeddings <embed>`.
