import cv2
import time


# 拍照并保存到raw_img路径
def take_photo(raw_img="test_img2.jpg"):
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW) # 1是usb摄像头，0是电脑摄像头
    while not cap.isOpened():
        cap = cv2.VideoCapture(1, cv2.CAP_DSHOW) # 1是usb摄像头，0是电脑摄像头
    cap.set(3,1280)
    cap.set(4,720)
    if(cap.get(3) != 1280 or cap.get(4) != 720):
        print("摄像头不支持1280*720分辨率!本次拍照分辨率为%d*%d!" % (cap.get(3), cap.get(4)))
    
    # time.sleep(3)
    # cap.set(cv2.CAP_PROP_POS_FRAMES,100)  #设置要获取的帧号，这是第101帧（下标从0开始）
    # cap.set(cv2.CAP_PROP_FOCUS,10)
    for i in range(1,51):
        ret, frame = cap.read()
    if ret == True:
        cv2.imwrite(raw_img, frame)
    print("已拍照%s" % raw_img)
    cap.set(3,640)
    cap.set(4,480)
    cap.release()
    return frame


# def clip_photo(cap, raw_img="test_clip_img.jpg"):
#     cap.set(3,1280)
#     cap.set(4,720)
#     if(cap.get(3) != 1280 or cap.get(4) != 720):
#         print("摄像头不支持1280*720分辨率!本次拍照分辨率为%d*%d!" % (cap.get(3), cap.get(4)))
#     ret, frame = cap.read()
#     if ret == True:
#         cv2.imwrite(raw_img, frame)
#     print("已拍照%s" % raw_img)
#     cap.set(3,640)
#     cap.set(4,480)
#     return frame

def video(video_path="test_video.avi"):
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW) # 1是usb摄像头，0是电脑摄像头 
    cap.set(3,640)
    cap.set(4,480)
    fourCC =  cv2.VideoWriter_fourcc(*'MJPG')
    #指定视频的名字,编码方式,每秒播放的帧数,每帧的大小
    out = cv2.VideoWriter(video_path,fourCC,10,(640,480))
    stop_time = 30 # 设置拍摄的时长，单位秒
    start_time = time.time()
    # while(time.time() - start_time < stop_time):
    while(cap.isOpened()):
        ret,frame = cap.read()
        if ret == True:
            out.write(frame)
            cv2.imshow("recording",frame)
            code = cv2.waitKey(100)
            # 按大写A或者时间到了就停止了
            if code == ord('A') or (time.time() - start_time > stop_time):
                break
            else:
                continue
    cap.release()
    out.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    print("start")
    take_photo()
    # video()