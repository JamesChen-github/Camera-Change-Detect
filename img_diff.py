from tracemalloc import start
import cv2
import time
import os
import re


def get_img_path():
    img_path = input("请输入图片path:")
    # start_time = re.sub(u"([^\u0030-\u0039])", "", start_time) # 只保留数字
    return img_path
    

def img_diff(img, stdimg='0.jpg'):
    img1 = cv2.imread(stdimg)
    img2 = cv2.imread(img)
    hash1 = dHash(img1)
    hash2 = dHash(img2)
    hamming = cmpHash(hash1, hash2)
    #print('hash1：%d' % hash1)
    #print('hash2：%d' % hash2)
    return hamming


def dHash(img):
    # 差值哈希算法
    # # 缩放8*8
    # size = 16
    # img = cv2.resize(img, (size+1, size))
    # 转换灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hash_str = ''
    # 每行前一个像素大于后一个像素为1，相反为0，生成哈希
    for i in range(img.shape[0]):
        for j in range(img.shape[1]-1):
            if abs(int(gray[i, j]) - int(gray[i, j+1])) < 16: # 如果差异小于16个灰度级，统一标记为2，目的是减小误差
                hash_str = hash_str+'2'
            elif gray[i, j] > gray[i, j+1]:
                hash_str = hash_str+'1'
            else:
                hash_str = hash_str+'0'
    # print(hash_str)
    return hash_str


def cmpHash(hash1, hash2):
    # Hash值对比
    # 算法中1和0顺序组合起来的即是图片的指纹hash。顺序不固定，但是比较的时候必须是相同的顺序。
    # 对比两幅图的指纹，计算汉明距离，即两个64位的hash值有多少是不一样的，不同的位数越小，图片越相似
    # 汉明距离：一组二进制数据变成另一组数据所需要的步骤，可以衡量两图的差异，汉明距离越小，则相似度越高。汉明距离为0，即两张图片完全一样
    n = 0
    # hash长度不同则返回-1代表传参出错
    if len(hash1) != len(hash2):
        return -1
    #print('hash1：%d' % len(hash1))
    #print('hash2：%d' % len(hash2))
    # 遍历判断
    for i in range(len(hash1)):
        # 不相等则n计数+1，n最终为相似度
        if hash1[i] != hash2[i]:
            n = n + 1
            #print('hash id %d hash1 %d hash2 %d' % i % hash1[i] % hash2[i] )
    return n*1000/len(hash1)




# 调用方法
if __name__ == "__main__":
    maxhamming = 0
    img_path = get_img_path()
    print(img_path)
    raw_path = os.path.join(img_path, "raw_img")
    focus_paths = []
    for filename in os.listdir(img_path):
        if 'focus' in filename:
            focus_paths.append(os.path.join(img_path, filename, "compressed_img"))
            print(filename)
    
    # 遍历每一个focus下的compressed_img
    for focus_path in focus_paths:
        for img_name in os.listdir(focus_path):
            stdimg = os.path.join(focus_path, '1.jpg')
            if '.jpg' in img_name:
                img = os.path.join(focus_path, img_name)
                print(img)
            hamming = img_diff(img, stdimg)
            if(maxhamming < hamming):
                maxhamming = hamming
            print('本论测试最大哈希值差异: %d' % maxhamming)
            if hamming > 100: # hamming距离的阈值，大于这个阈值即检测到变化
                # 生成error os.path.join(os.getcwd(), filename 的list
                with open("error_photos_list.txt", "a", encoding="UTF-8") as f:
                    f.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())+"  "+img+"   hamming:%d\n" % hamming)
            
            # 每10次改变stdimg
            if '1.jpg' in img_name:
                stdimg = os.path.join(focus_path, img_name)