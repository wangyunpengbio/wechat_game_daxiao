import imageTools
import pickle
import time
import util
from config import config
import os
import cv2
import shutil


'''创建及清空必要的文件夹'''
try:
    shutil.rmtree('ScreenShot')
except Exception:
    pass
os.mkdir('ScreenShot')
if not os.path.exists('SingleChar'):
    os.mkdir('SingleChar')
if config['debug']:
    print("开启了调试模式，请手动答题")
    if not os.path.exists('ScreenShotForTrain'):
        os.mkdir('ScreenShotForTrain')


#加载逻辑回归模型
with open('lr.pickle', 'rb') as fr:
    lr = pickle.load(fr)

print("模型加载成功")

preRes = '' #保存上一步的表达式，防止因截图过快导致的本次点击了上一张图的答案


'''
一次屏幕点击
'''
def one_tap(res):
    print(eval(res))
    if eval(res):
        util.tapScreenFromPC(config['pc_tap_x'], config['pc_tap_up_y'])
    else:
        util.tapScreenFromPC(config['pc_tap_x'], config['pc_tap_down_y'])

# filename='ScreenShotForTrain/false2.png'
# imageTools.get_result(lr, cv2.imread(filename, 0), filename)

count = 1   #迭代轮数
while True:
    # t1 = time.time()
    img = util.shotByWinAPI('ScreenShot/%d.png' %count)
    if config['debug']:
        cv2.imwrite('ScreenShotForTrain/%d.png' %int(time.time()), img)
        print("截图成功")
        time.sleep(0.3)
        continue
    # t2= time.time()
    # print('截图耗时%f' %(t2 - t1))
    res = imageTools.get_result(lr, img, '%d.png' % count)
    # t3 = time.time()
    #print('获取结果耗时%f' % (t3 - t2))
    if res == preRes or res == '':
        '''如果表达式和之前的表达式相同，则代表截图重复，可能此时手机已经跳到了下一题，因此不进行点击'''
        print('截图重复')
        time.sleep(config['sleep_when_repeat'] / (count // 10 + 1))
        continue
    else:
        print('第%d题： %s'%(count,res), end=' ')
        preRes = res
        try:
            one_tap(res)
        except SyntaxError:
            print("游戏结束！")
            exit(0)
        count += 1
