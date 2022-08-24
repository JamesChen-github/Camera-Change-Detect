# coding=utf-8
from pickle import FALSE
from time import sleep
import argparse
import sys
import relayControl # relay controller
from subprocess import run # run commandline code
from atexit import register
import random

# !!!!!!!!!!!!!!!!!!!!要使用的话要复制整个文件夹，单独文件无法运行
from camera_change_detect import CamDet


def main(argv):
    # read op codes
    parser = argparse.ArgumentParser()
    parser.add_argument('-c','--channel', default=5, help='继电器端口（默认为1）')
    parser.add_argument('-n','--repeat', default=-1, help='测试次数  （默认为无限）') # -1就是无限次
    parser.add_argument('-d','--delay', default=0, help='测试间隔  （默认不等待）')
    parser.add_argument('-t','--timeout', default=10, help='开机超时时间（默认100秒）') # 意思就是开机多久之后关机
    parser.add_argument('--serial', default='0123459876', help='测试板序列号（不出错不用填）')
    args = parser.parse_args()

    channel = int(args.channel)
    repeat = int(args.repeat)
    delay = int(args.delay)
    timeout = int(args.timeout)

    relay = relayControl.Relay()
    @register
    def quit():
        relay.closeDevice()


    n = 1
    
    # stop : True, False 大于阈值后是否停下(是否保留现场)，默认True

    # coord : (top, left, right, bottom) 像素点位置，默认整张图片

    # detect: 'normal' : 1.4*(ave+5)
    #         'strict' : 1.2*(ave+5)
    #         'loose' : 1.6*(ave+5)          阈值设置，默认normal
    
    cd1 = CamDet(stop=False) # 整张照片,stop默认True
    cd2 = CamDet(coord=(10,129,149,365), stop=False, detect='normal')
    cd3 = CamDet(coord=(566,170,807,414), stop=False)
    # cd4 = CamDet(coord=(766,370,807,414), stop=False)
    # cd5 = CamDet(coord=(766,370,807,414), stop=False)
    # cd6 = CamDet(coord=(766,370,807,414), stop=False)
    # cd7 = CamDet(coord=(766,370,807,414), stop=False)
    # cd8 = CamDet(coord=(766,370,807,414), stop=True, detect='loose')
    while repeat == -1 or n <= repeat:
        print(f"测试{n}次：")
        relay.closeChannel(channel)
        sleep(random.uniform(0.01, 1)) # 设置关机多久之后开机，单位秒
        relay.openChannel(channel)
        # sleep(random.uniform(0.01, 10)) # 设置开机多久之后关机，单位秒
        # relay.closeChannel(channel)
        # sleep(random.uniform(0.01, 0.3)) # 设置关机多久之后开机，单位秒
        # relay.openChannel(channel)
        # sleep(random.uniform(0.01, 4)) 
        # relay.closeChannel(channel)
        # sleep(random.uniform(0.01, 0.2)) 
        # relay.openChannel(channel)
        # sleep(random.uniform(0.01, 0.2)) 
        # relay.closeChannel(channel)
        # sleep(random.uniform(0.01, 1)) 
        # relay.openChannel(channel)
        print(" Power on")
        for i in range(timeout):
            if i == timeout-1: # 第timeout-1秒拍照
                CamDet.detect_change(cd1,cd2,cd3) # 往这里面加cd45678点
            sleep(0.95)
            print(f'\r  {i}秒', end='')
            print('.'*i, end='')
        n += 1
        print("\n")
        sleep(delay)



if __name__ == '__main__':
    main(sys.argv[1:])
