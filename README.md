项目在Pytho 3.6.8版本, ubantu下运行。

# 人头检测错误分析

### 项目总体介绍

实时检测并跟踪视频流中的人头，并返回轨迹跟踪信息。通过分析画面中人头移动的轨迹来设计逻辑，判断是否出现了误检或者漏检。目前现在设计的错误逻辑有两种：（1）轨迹进入错误，即轨迹突然出现在画面中，然后开始移动；（2）轨迹离开错误，即轨迹离开的时候是在画面中间离开，而不是在画面边缘。找出出现这两类错误的帧，可视化错误帧上出现的错误框和轨迹，并将错误信息写入数据库。

### 项目前提条件

- 需要安装的库见 ```./requirements.txt```
- 全局变量设置见 ```./config_error_analysis.txt```

### 模块功能

1. ```trajectory.py```  从视频流中实时检测人头，当画面中出现超过min_head的人头数时，开始截取视频并保存轨迹信息
2. ```error_detection.py```  共有四个类
- Info_Extraction  对轨迹信息进行提取，获得每条轨迹出现的帧、每条轨迹的坐标信息等
- Error_Detection  根据轨迹信息，判断每条轨迹是否属于进入错误或出去错误，返回错误的帧和轨迹圆心
- SaveErrorImages  保存出现错误的图片，错误图片的检测框xml文件，错误可视化后的图片
- MysqlWriter  将错误图片所在的视频、错误帧、训练模型版本、错误类型等信息存入数据库

### 使用方法
- ```example.py```   可完成提取轨迹信息、错误分析、可视化错误图片并保存xml文件功能

