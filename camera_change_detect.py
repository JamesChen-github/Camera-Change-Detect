import os
import time
import sys
import img_diff
import cv2
import camera
import numpy as np

class CamDet:
    # 运行次数
    run_cnt = 0
    focus_cnt = 0
    # print("创建类变量")
    img_dir = time.strftime('image-%Y%m%d-%H%M%S', time.localtime()) # image文件夹路径
    raw_dir = os.path.join(img_dir, 'raw_img') # raw_img文件夹路径
    raw_img = '' # raw_img图片路径
    # 第一次拍照创建文件夹
    os.mkdir(img_dir)
    os.mkdir(raw_dir)
    
    
    # 拍照并保存到raw_img路径
    def take_photo(raw_img="test_img.jpg"):
        cap = cv2.VideoCapture(1, cv2.CAP_DSHOW) # 1是usb摄像头，0是电脑摄像头
        while not cap.isOpened():
            cap = cv2.VideoCapture(1, cv2.CAP_DSHOW) # 1是usb摄像头，0是电脑摄像头
        cap.set(3,1280)
        cap.set(4,720)
        if(cap.get(3) != 1280 or cap.get(4) != 720):
            print("摄像头不支持1280*720分辨率!本次拍照分辨率为%d*%d!" % (cap.get(3), cap.get(4)))
        for i in range(1,51):
            # cap.set(cv2.CAP_PROP_POS_FRAMES,100)  #设置要获取的帧号，这是第101帧（下标从0开始）
            ret, frame = cap.read()
        if ret == True:
            cv2.imwrite(raw_img, frame)
        print("已拍照%s" % raw_img)
        cap.release()
        return frame
    
    
    # 执行一次拍照比较  调用：CamDet.detect_change(cd1, cd2, cd3)
    def detect_change(*focuses):
        CamDet.run_cnt += 1
        print("第%d次拍照, 时间:%s" % (CamDet.run_cnt, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
        CamDet.raw_img = os.path.join(CamDet.raw_dir, "%s.jpg") % CamDet.run_cnt # 目标照片存放地址,raw_dir是文件夹名
        frame = CamDet.take_photo(CamDet.raw_img)
        
        # 分别执行每个focus的计算
        for focus in focuses:
            focus.detect_focus()
        print("*******************************************************************************")
        
    
    def __init__(self, coord=(0,0,1280,720), stop=True, detect='normal') -> None:
        """ 
            Parameters
            ------

                stop : True, False
                
                coord : (top, left, right, bottom)
                
                detect: 'normal' : 1.4*(ave+5)
                        'strict' : 1.2*(ave+5)
                        'loose' : 1.6*(ave+5)
                        
                for example: cd1 = CamDet(True, (80,90,155,185), 'normal')
        
            Function
            ------
                cut_img() : cut by the focus you defined
                
                compress_img() : compressing after cutting
                
                detect_focus() : the main detector

        """

        CamDet.focus_cnt += 1
        # print("创建对象变量")
        self.focus_name = "focus" + str(CamDet.focus_cnt)
        self.focus_dir = os.path.join(CamDet.img_dir, "%s" % self.focus_name)
        self.cut_dir = os.path.join(self.focus_dir, "cut_img")
        self.compressed_dir = os.path.join(self.focus_dir, "compressed_img")
        # 第一次运行时创建focus文件夹
        os.mkdir(self.focus_dir)
        os.mkdir(self.cut_dir)
        os.mkdir(self.compressed_dir)
        self.cut_img_path = ''
        self.compressed_img_path = ''
        self.maxhamming = 0
        # print('%s初始化最大哈希值差异度: %d' % (self.focus_name, self.maxhamming))
        self.avehamming = 0
        self.threshold = 0
        self.detect = detect
        self.coord = coord
        self.stop = stop
        print(self.focus_name,"初始化 coord=", self.coord, self.stop, self.detect)
        self.stdimg = os.path.join(self.compressed_dir, '1.jpg') # 一开始把1.jpg图片作为标准照片
    
    # 对图片进行裁剪、滤波和压缩
    def cut_img(self, img):
        # 裁剪
        left = self.coord[0]
        top = self.coord[1]
        right = self.coord[2]
        bottom = self.coord[3]
        img = img[top:bottom,left:right]
        cv2.imwrite(self.cut_img_path, img)
        return img

    def compress_img(self, img):
        # 高斯滤波
        # img = cv2.GaussianBlur(src=img, ksize=(11,11), sigmaX=2, sigmaY=2)
        # kernel_3x3 = np.array([[1/16, 1/8, 1/16],
        #                         [1/8, 1/4, 1/8],
        #                         [1/16, 1/8, 1/16]])
        # img = cv2.filter2D(img, 3, kernel_3x3)
        # 压缩
        # if img.shape[1] >= 500 and img.shape[0] >= 333:
        #     size = (int(img.shape[1]/5), int(img.shape[0]/5))
        # elif img.shape[1] >= 300 and img.shape[0] >= 200:
        #     size = (int(img.shape[1]/3), int(img.shape[0]/3))
        size = (33, 32)
            # print(size[0],size[1])
        img = cv2.resize(img, (size[0], size[1]))
        cv2.imwrite(self.compressed_img_path, img)
        # cv2.imshow("a", img)
        # cv2.waitKey(0)
        return img


    def detect_focus(self):
        self.cut_img_path = os.path.join(self.cut_dir, "%d.jpg" % CamDet.run_cnt)
        self.compressed_img_path = os.path.join(self.compressed_dir, "%d.jpg" % CamDet.run_cnt)
        raw_frame = cv2.imread(CamDet.raw_img)
        cut_frame = self.cut_img(raw_frame)
        compressed_frame = self.compress_img(cut_frame)
        
        # 第一次拍完照裁剪完直接返回
        if CamDet.run_cnt == 1:
            return
        else:
            print("")
            hamming = img_diff.img_diff(img=self.compressed_img_path,stdimg=self.stdimg) # 计算hamming距离
            print('%s本次哈希值差异度: %d' % (self.focus_name, hamming))
            if(self.maxhamming < hamming):
                self.maxhamming = hamming
            print("%s平均哈希值差异度: %d" % (self.focus_name, self.avehamming))
            print('%s最大哈希值差异度: %d' % (self.focus_name, self.maxhamming))
            with open(os.path.join(self.focus_dir, "photos_hamming_list.txt"), "a", encoding="UTF-8") as f:
                f.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())+"  raw:"+CamDet.raw_img+"  cut:"+self.cut_img_path+"  hamming:%d\n" % hamming)
            if self.detect == 'strict':
                self.threshold = 1.2*(self.avehamming+5)
            elif self.detect == 'loose':
                self.threshold = 1.6*(self.avehamming+5)
            else:
                self.threshold = 1.4*(self.avehamming+5)
            if CamDet.run_cnt >= 5 and hamming > self.threshold: # 第四次开始利用之前的平均hamming距离作为阈值，大于这个阈值即检测到变化
                # 生成error os.path.join(os.getcwd(), filename 的list
                print("%s哈希差异度大于阈值" % self.focus_name)
                with open(os.path.join(CamDet.img_dir, "error_photos_list.txt"), "a", encoding="UTF-8") as f:
                    f.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())+"  raw:"+CamDet.raw_img+"  cut:"+self.cut_img_path+"  hamming:%d\n" % hamming)
                if self.stop == True:
                    print("正在拍摄...")
                    camera.video(os.path.join(CamDet.img_dir, "error_video.avi"))
                    sys.exit(0)
            else:
                if CamDet.run_cnt % 5 == 1:
                    self.stdimg = os.path.join(self.compressed_dir, '%d.jpg' % CamDet.run_cnt) # 正常情况每5次设置一次标准照片
                self.avehamming = self.avehamming/(CamDet.run_cnt-1)*(CamDet.run_cnt-2)+hamming/(CamDet.run_cnt-1) # 计算平均hamming距离
        




# 调用方法
if __name__ == "__main__":
    cd1 = CamDet(stop=False,detect='normal')
    cd2 = CamDet(coord=(0,0,640,360),stop=False,detect='normal')
    cd3 = CamDet(coord=(640,0,1280,360), stop=False, detect='normal')
    cd4 = CamDet(coord=(0,360,640,720), stop=False)
    for i in range(1,10):
        CamDet.detect_change(cd1,cd2,cd3,cd4)