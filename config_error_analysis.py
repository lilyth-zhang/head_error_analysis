#### 判断异常进入或出去的范围 ####
left = 0.1
right = 0.9
down = 0.1
up = 0.9

#### resize坐标时需要用到 ####
yolo_img_size = 416
re_size = 800

#### 错误出去，往前推帧的时候需要用到 ####
max_age = 30  # maxiumal count before discarding a track

#### 从视频流中截取的视频和信息文件路径 ###
root = './stream_fraction/2_1000/'

#### 存错误文件的路径 #####
save_root_path = '/data/zhangli/head_error_analysis/stream/'

#### 存数据库的路径 ######
src_images_path = '/data/zhangli/head_error_analysis/stream/allimages/'
src_video_path = '/data/zhangli/head_error_analysis/stream_fraction/2_1000/'  #待改
src_model_path = '/data/zhangli/head_error_analysis/model_weights/'
src_xml_error_vi = '/data/zhangli/head_error_analysis/stream/'

