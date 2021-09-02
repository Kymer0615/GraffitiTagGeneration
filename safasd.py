import shutil
import uuid
from os import getcwd, listdir, remove
from urllib.request import urlretrieve
import pandas as pd
import numpy as np
#
# a='https://scontent-nrt1-1.cdninstagram.com/v/t51.2885-15/e35/s1080x1080/124030331_102345718339794_8495268383277284118_n.jpg?_nc_ht=scontent-nrt1-1.cdninstagram.com&_nc_cat=106&_nc_ohc=sbXnp4f8bAAAX_D4zMO&edm=AP_V10EBAAAA&ccb=7-4&oh=f6a45690ebc446fffd73ca813ba59a23&oe=612A75A4&_nc_sid=4f375e'
#
# uuid_str = uuid.uuid4().hex
# urlretrieve(a, getcwd() + 'rawdata/%s.png' % uuid_str)

# 初始化csv
# df=pd.DataFrame(columns=['FileName', 'URL', 'Content'])
# df.to_csv(getcwd()+"/tagInfo.csv",index=False)

df = pd.read_csv(getcwd() + '/tagInfo.csv').replace(np.nan, '', regex=True)
a = np.array(df)

# print(a.shape)
# df2 = pd.DataFrame([[uuid.uuid4().time_mid, 1, 2]], columns=['FileName', 'URL', 'Content'])
# df = df.append(df2, ignore_index=True)
# df.to_csv(
#     getcwd() + "/tagInfo.csv",
#     mode='a', header=False, index=False)

from os.path import dirname, join

#
# print(dirname(dirname(__file__)))

train_graff_root = join((dirname(__file__)), "data","train", "Graffiti")
train_text_root = join((dirname(__file__)), "data", "train","Text")
test_graff_root = join((dirname(__file__)), "data", "test","Graffiti")
test_text_root = join((dirname(__file__)), "data","test", "Text")
nameL = []
counter = 0

# 分训练集
for filename in listdir(train_graff_root):
    if filename.endswith(".png") and counter != 397:
        nameL.append(filename)
        counter+=1
        shutil.move(join(train_graff_root,filename), join(test_graff_root,filename))


for filename in listdir(train_text_root):
    if filename.endswith(".png"):
        if filename in nameL:
            shutil.move(join(train_text_root,filename),join(test_text_root,filename))

# 检测
# root = "/Users/chenziyang/Documents/Ziyang/GAN/Graffiti Project/untitled folder/data1/train/Graffiti"
# csv_root = ""
# L=[]
# l=[]
# A=[]
# a=[]
# for filename in listdir(root):
#     if filename.endswith(".png"):
#         L.append(str(filename.split(".")[0]))
# for i in a:
#     if i[3] and str(i[0]) not in L:
#         l.append(str(i[0]))

# for i in a:
#     if i[3]:
#         A.append(str(i[0]))
# for filename in listdir(root):
#     if filename.endswith(".png") and str(filename.split(".")[0]) not in L:
#         a.append(str(filename.split(".")[0]))
# print(l)
# print(a)

# 去掉不认识的
# for i in a:
#     if i[4] is "?":
#         print(i[0])