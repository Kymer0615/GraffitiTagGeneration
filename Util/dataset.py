from torch.utils.data import Dataset
from PIL import Image
import os
import numpy as np


class GraffitiTextDataset(Dataset):
    def __init__(self, root_graf, root_text, transform=None):
        self.root_graff = root_graf
        self.root_text = root_text
        self.transform = transform

        self.graff_image = [img for img in os.listdir(root_graf) if ".png" in img]
        self.text_image = [img for img in os.listdir(root_text) if ".png" in img]
        self.graff_len = len(self.graff_image)
        self.text_len = len(self.text_image)
        self.lenth_dataset = max(self.graff_len, self.text_len)

    def __len__(self):
        return self.lenth_dataset

    def __getitem__(self, index):
        graff_image = self.graff_image[index % self.graff_len]
        text_image = self.text_image[index % self.text_len]

        text_path = os.path.join(self.root_text, text_image)
        graff_path = os.path.join(self.root_graff, graff_image)

        graff_image = np.array(Image.open(graff_path))
        text_image = np.array(Image.open(text_path))

        if self.transform:
            augmentations = self.transform(image=graff_image, image0=text_image)
            graff_image=augmentations["image"]
            text_image=augmentations["image0"]

        return graff_image,text_image
