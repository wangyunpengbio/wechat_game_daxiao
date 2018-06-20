import cv2
import numpy as np
import config
import time
import os


def cropImg(img):
    """裁剪原始截图"""
    height = img.shape[0]
    img2 = img[int(config.config['exp_area_top_rate'] * height):int(config.config['exp_area_bottom_rate'] * height), :]
    # print('裁剪完毕')
    return img2


def binaryImg(img):
    """二值化图片"""
    ret, thresh1 = cv2.threshold(img, config.config['binary_threshold'], 255, cv2.THRESH_BINARY)
    # print('二值化完毕')
    return thresh1

def find_min_rect(img):
    """去除字符附近的黑色区域"""
    row_sum = np.sum(img, axis=0)  # 求行的和
    col_sum = np.sum(img, axis=1)  # 求列的和
    row_character_index = np.where(row_sum != 0)[0]
    col_character_index = np.where(col_sum != 0)[0]
    row_start = row_character_index[0]
    row_end = row_character_index[-1]
    col_start = col_character_index[0]
    col_end = col_character_index[-1]
    img = img[col_start:col_end, row_start:row_end]
    # 最后取出"大","小"的汉字
    img = img[:, int(img.shape[1]/2):img.shape[1]]
    return img

def cropAgain(img):
    """再次裁剪"""
    height = img.shape[0]
    width = img.shape[1]
    # 切出上1/3部分
    img1 = img[0:int(0.30 * height), :]
    # 切出中间"谁大","谁小"部分
    img2 = img[int(0.4 * height):int(0.6 * height), int(0.2 * width):int(0.8 * width)]
    img2 = find_min_rect(img2)
    # 切出下1/3部分
    img3 = img[int(0.7 * height):height, :]
    # print('再次裁剪完毕')
    return img1, img2, img3


def contours2tuple(contours):
    for c in contours:
        # find bounding box coordinates
        x, y, w, h = cv2.boundingRect(c)
        if w < config.config['pc_single_char_width_min']:  # 将边边角角筛掉
            continue
        if 2 * config.config['pc_single_char_width'] < w < 3 * config.config['pc_single_char_width']:  # 如果是两个字符黏在一起的情况,将其从中间分开
            yield (x, y, w // 2, h)
            yield (x + w // 2, y, w // 2, h)
            continue
        if w > 3 * config.config['pc_single_char_width']:  # 如果是两个字符黏在一起的情况,将其从中间分开
            yield (x, y, w // 3, h)
            yield (x + w // 3, y, w // 3, h)
            yield (x + 2 * w // 3, y, w // 3, h)
            continue

        yield (x, y, w, h)

def cutImg(img):
    # 将绘制图片中的轮廓,并且找出最小矩形x,y,width,heigth
    _, contours, hier = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rects = sorted(contours2tuple(contours), key=lambda x: x[0])  # 按照box的x值sort
    return rects

def rects2Image(rects, img, filename):
    # 将最小矩形x,y,width,heigth转化成图片
    imglist = []
    for count, rect in enumerate(rects):
        imgROI = img[rect[1]:(rect[1] + rect[3]), rect[0]:(rect[0] + rect[2])]
        imglist.append(imgROI)
        sub_img = cv2.resize(imgROI, (120, 240), interpolation=cv2.INTER_CUBIC)
        if config.config['debug']:
            # 为训练集搜集数据
            cv2.imwrite('SingleCharForTrain/%s_%d.png' % (filename, count), sub_img)
    return imglist

def all(img, filename):
    imgExpression = cropImg(img)  # 切出来表达式图片
    img = binaryImg(imgExpression)  # 二制化，转成黑白的
    img1, img2, img3 = cropAgain(img)  # 对称切成三半

    # 将图片同样进行resize
    img2s = [cv2.resize(img2, (120, 240), interpolation=cv2.INTER_CUBIC)]
    if config.config['debug']:
        # 为训练集搜集数据
        cv2.imwrite('SingleCharForTrain/%s_com.png' % filename, img2s[0])

    rects1 = cutImg(img1)
    rects3 = cutImg(img3)

    img1s = rects2Image(rects1, img1, filename + '_1')
    img3s = rects2Image(rects3, img3, filename + '_2')

    return img1s, img2s, img3s

# 获取用于训练的单个字符(将ScreenShotForTrain字符分隔,存入SingleCharForTrain)
def get_char_for_train():
    if not os.path.exists('SingleCharForTrain'):
        os.mkdir('SingleCharForTrain')

    for f in os.listdir("ScreenShotForTrain"):
        srcImg = cv2.imread(os.path.join("ScreenShotForTrain", f), 0)
        all(srcImg, f)
    print("Done!")


def get_result(lr, img, filename):
    """根据图片的数据获取表达式,lr为逻辑回归模型"""
    res = []
    img1s, img2s, img3s = all(img, filename)
    for img in img1s:
        img = cv2.resize(img, (120, 240), interpolation=cv2.INTER_CUBIC)
        img = np.array(img).reshape(1, -1)
        y_hat = lr.predict(img)[0]
        if y_hat == 10:
            res.append('+')
        elif y_hat == 11:
            res.append('-')
        else:
            res.append(str(y_hat))

    img = cv2.resize(img2s[0], (120, 240), interpolation=cv2.INTER_CUBIC)
    img = np.array(img).reshape(1, -1)
    y_hat = lr.predict(img)[0]
    if y_hat == 12:
        res.append('>')
    elif y_hat == 13:
        res.append('<')
    else:
        res.append(" "+str(y_hat)+" ")

    for img in img3s:
        img = cv2.resize(img, (120, 240), interpolation=cv2.INTER_CUBIC)
        img = np.array(img).reshape(1, -1)
        y_hat = lr.predict(img)[0]
        if y_hat == 10:
            res.append('+')
        elif y_hat == 11:
            res.append('-')
        else:
            res.append(str(y_hat))
    res = ''.join(res)
    return res


if __name__ == '__main__':
    filename = 'false2.png'
    srcImg = cv2.imread('ScreenShotForTrain/'+filename, 0)

    imgExpression = cropImg(srcImg)  # 切出来表达式图片
    img1s, img2s, img3s = all(srcImg, filename)

    cv2.imshow("contours ", img3s[0])
    cv2.waitKey()
    cv2.destroyAllWindows()

    imgExpression = cropImg(srcImg)  # 切出来表达式图片
    img = binaryImg(imgExpression)  # 二制化，转成黑白的
    img1, img2, img3 = cropAgain(img)  # 对称切成三半
    _, contours, hier = cv2.findContours(img3, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        # find bounding box coordinates
        x, y, w, h = cv2.boundingRect(c)
        print((x, y, w, h))
        if w < config.config['pc_single_char_width_min']:  # 将边边角角筛掉
            continue
        if w > 2 * config.config['pc_single_char_width']:  # 如果是两个字符黏在一起的情况,将其从中间分开
            continue

    rects = sorted(contours2tuple(contours), key=lambda x: x[0])  # 按照box的x值sort
    for count, rect in enumerate(rects):
        imgROI = img[rect[1]:(rect[1] + rect[3]), rect[0]:(rect[0] + rect[2])]
        sub_img = cv2.resize(imgROI, (120, 240), interpolation=cv2.INTER_CUBIC)

    cv2.imshow("contours ", imgExpression)
    cv2.waitKey()
    cv2.destroyAllWindows()




