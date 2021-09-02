from os.path import dirname, join

import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class TextInputGenerator():
    def __init__(self, text, name=None):
        self.name = str(name)
        self.text = text.split("*")
        self.scale = 1
        self.add = 0.1
        self.minus = 0.1
        self.img = None
        self.output_root = join(dirname(dirname(__file__)), "data", "train", "Text")

    def get_optimal_position(self, textScale, size):
        pos = []
        for i in range(len(self.text)):
            textSize = cv.getTextSize(self.text[i], fontFace=cv.FONT_HERSHEY_DUPLEX, fontScale=textScale, thickness=1)
            textWidth = textSize[0][0]
            textHight = textSize[0][1]

            # print(textSize)
            horizontalPadding = int((size - textWidth) / 2)
            verticalPadding = size/2 + (textHight / 2)

            if len(self.text) % 2 == 0:
                firstHight = verticalPadding - len(self.text)/2 * textHight
            else:
                firstHight = verticalPadding - (len(self.text)+1)/2 * textHight
            verticalPadding = int(firstHight + (i+1) * textHight)
            corrdinates = (horizontalPadding, verticalPadding)
            pos.append(corrdinates)
        return pos


    def get_optimal_font_scale(self, width):
        longestText = max(self.text, key=len)
        while True:
            textSize = cv.getTextSize(longestText, fontFace=cv.FONT_HERSHEY_DUPLEX, fontScale=self.scale, thickness=1)
            new_width = textSize[0][0]
            if new_width > width:
                self.scale -= self.minus
            if new_width < width and new_width / width >= 0.90:
                return self.scale
            else:
                self.scale += self.add
                textSize = cv.getTextSize(longestText, fontFace=cv.FONT_HERSHEY_DUPLEX, fontScale=self.scale, thickness=1)
                new_width = textSize[0][0]
                if new_width >= width:
                    self.add = self.add / 2
                    self.scale += self.add


    def gen_text(self):
        self.img = np.zeros((256, 256, 1), np.uint8)
        for x in range(0, 256):
            for y in range(0, 256):
                self.img[x][y] = 255
        font = cv.FONT_HERSHEY_SIMPLEX
        fontScale = self.get_optimal_font_scale(256)
        org = self.get_optimal_position(fontScale, 256)
        fontColor = (0, 0, 0)
        lineType = 100
        for i in range(len(self.text)):
            self.img = cv.putText(self.img, self.text[i], org[i], font, fontScale, fontColor,thickness=5, lineType=lineType)
        # plt.imshow(self.img)
        # plt.show()

    def get_text_image(self):
        return (self.img)

    def save_text_img(self):
        cv.imwrite(join(self.output_root, self.name + ".png"), self.img)


def main():
    # Read from csv file and save the text images
    # df = pd.read_csv(join(dirname(dirname(__file__)), 'tagInfo.csv')).fillna('')
    # info = np.array(df)
    # for t in info:
    #     name = t[0]
    #     content = t[3]
    #     # if content and "*" in content:
    #     if content :
    #         # print(content)
    #         a = TextInputGenerator(content, name)
    #         a.gen_text()
    #         # break
    #         a.save_text_img()

    a = TextInputGenerator("content")
    a.gen_text()
    plt.imshow(a.get_text_image())
    plt.show()


if __name__ == "__main__":
    main()
