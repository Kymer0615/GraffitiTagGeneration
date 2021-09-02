from os.path import dirname, join
import torch
import albumentations as A
from albumentations.pytorch import ToTensorV2

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
TRAIN_DIR = join(dirname(dirname("__file__")),"data","train")
VAL_DIR = join(dirname(dirname("__file__")),"data","test")
BATCH_SIZE = 1
LEARNING_RATE = 1e-5
LAMBDA_IDENTITY = 0.0
LAMBDA_CYCLE = 10
NUM_WORKERS = 4
NUM_EPOCHS = 100
LOAD_MODEL = False
SAVE_MODEL = True
# Set the paths here
CHECKPOINT_GEN_G = join(dirname(dirname(__file__)),"checkpoint","genG.pth.tar")
CHECKPOINT_GEN_T = join(dirname(dirname(__file__)),"checkpoint","genT.pth.tar")
CHECKPOINT_CRITIC_G = join(dirname(dirname(__file__)),"checkpoint","criticG.pth.tar")
CHECKPOINT_CRITIC_T = join(dirname(dirname(__file__)),"checkpoint","criticT.pth.tar")

transforms = A.Compose(
    [
        A.Resize(width=256, height=256),
        A.Normalize(mean=[0.5], std=[0.5], max_pixel_value=255),
        ToTensorV2(),
     ],
    additional_targets={"image0": "image"},
)