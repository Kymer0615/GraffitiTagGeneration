from os.path import join, isfile
from pathlib import Path
from matplotlib import pyplot as plt

import cv2 as cv
from os import getcwd, listdir


class preprocess():
    def __init__(self):
        self.img_root = getcwd() + "/../rawData2/"
        self.output_root = getcwd() + "/../rawData3/"
        Path(self.output_root).mkdir(parents=True, exist_ok=True)
        self.imgs = []
        self.proprocess()
        self.saveImg()
    @staticmethod
    def invertBasedOnBackground(img):
        sum = 0
        allWhiteSum = 256 * 256 * 255
        for x in range(0, 256):
            for y in range(0, 256):
                sum += img[x][y]
        # print(sum / allWhiteSum)
        if sum / allWhiteSum < 0.3:
            return cv.bitwise_not(img)
        else:
            return img

    def proprocess(self):
        files = [join(self.img_root, f) for f in listdir(self.img_root) if
                 isfile(join(self.img_root, f)) and ".png" in f]
        for f in files:
            name = f.split("/")[-1].split(".")[0]
            img = cv.imread(f, 0)
            img = cv.cvtColor(img, cv.COLOR_BAYER_RG2GRAY)
            _, img = cv.threshold(img, 127, 255, cv.THRESH_OTSU)
            img = cv.resize(img, (256, 256))
            img= preprocess.invertBasedOnBackground(img)
            # print(img.shape)
            # print(name)
            # plt.imshow(img)
            # plt.show()
            # break
            self.imgs.append((img, name))

    def saveImg(self):
        for img in self.imgs:
            cv.imwrite((self.output_root + img[1] + ".png"), img[0])


def main():
    t = preprocess()
    # img=cv.imread('/Users/chenziyang/Documents/Ziyang/GAN/Graffiti Project/GraffitiGan/rawData3/1.png',0)
    # print(img.shape)
    # img = preprocess.invertBasedOnBackground(img)
    # plt.imshow(img)
    # plt.show()

if __name__ == "__main__":
    main()
