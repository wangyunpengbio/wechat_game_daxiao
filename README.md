# 用python玩转微信小游戏 大小猜猜看 #
## 游戏模式 ##
在微信小程序里搜索“大小猜猜看”，即可找到该游戏。 
游戏的目标比拼计算能力，找出谁大谁小，一共有40题，全部答对即挑战成功。
一开始答题时间充足，数字也比较简单，后面就需要特别快的计算速度。

![游戏界面](https://i.imgur.com/YISNUNC.png)![成功通关界面](https://i.imgur.com/sffTuQD.png)

## 项目地址 ##
本项目地址：https://github.com/wangyunpengbio/wechat_game_daxiao

## 工具介绍 ##
- Python 3.5
- OpenCV包`pip install opencv-python`
- win32gui, win32ui, win32con(Python调用windows的原生API)
- PyUserInput包`pip install PyUserInput` 模拟鼠标键盘

## 原理说明 ##
1. 首先使用ApowerMirror软件将手机屏幕投屏到电脑，
2. 手动答题，搜集训练集数据，调用OpenCV库，进行图片相关处理
3. 将图片导入逻辑回归模型，训练模型
4. 利用逻辑回归模型识别图片，得出答案
5. 模拟鼠标自动点击正确答案

## 使用方法 ##
1. 首先我们得安装ApowerMirror软件，软件下载链接：[ApowerMirror下载](https://software.airmore.cn/phone-mirror?bd) 。
2. 想办法获得表达式区域顶部和底部的y坐标相对于整个手机屏幕的高度的比例，然后将对应值填入根目录下的config.py文件中的 exp_area_top_rate 和 exp_area_bottom_rate 处
3. 打开ApowerMirror软件，将手机屏幕投影到电脑上，然后将ApowerMirror拉到桌面的一个固定位置，建议拉到左上角。使用QQ的截屏功能或者是其他方法获取以下参数并填入config.py的对应位置：从PC端截屏时，截取区域左上角相对桌面的x坐标:projection_x; 截取区域左上角相对桌面的y坐标:projection_y; 截取区域的宽度:projection_width; 从PC端截屏时，截取区域的高度:projection_height; 使用PC进行截图时点击手机屏幕区域的x坐标:pc_tap_x; 使用PC进行截图时点击手机屏幕上部分选项的y坐标:pc_tap_up_y; 使用PC进行截图时点击手机屏幕下部分选项的y坐标:pc_tap_down_y;
4. 将config.py中的 debug 参数设置为False，打开游戏界面，将ApowerMirror拉到桌面左上角，运行python程序

## 训练自己的模型 ##
1. 首先需要确保你已经按照说明配置好了config.py中的相关参数，整个手机屏幕的截图和表达式区域的截图都是正确的。
2. 将config.py中的 debug 参数设置为True，然后进入游戏，同时运行main.py，你需要手动进行答题，此时程序每隔0.3秒会截取一次手机屏幕。
3. 运行imageTools.py中的get_char_for_train()方法，获取到用于训练的单个字符储存到SingleCharForTrain文件夹中。
4. 运行ml.py中的cleanTrainChar()方法将TrainChar文件夹中原有的训练字符清空。
5. 手工将SingleCharForTrain文件夹中的训练字符移动到TrainChar中对应的子文件夹里面。
6. 调用ml.py中的dumpModel()方法训练自己的模型.

## 常见问题 ##
1. 训练模型中，全白色的图片代表着“减号”
2. 字符识别错误：建议认真检查截屏的相关参数设置，确定截取到正确的区域，重新训练数据。
其他问题请在本项目的ISSUE中给我留言。

### 致谢 ###
部分代码来源：[微信小游戏《加减大师》、《加减王者》系列游戏辅助](https://github.com/1033020837/WechatGameScript)