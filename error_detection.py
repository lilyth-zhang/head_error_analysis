import cv2
import os
import re
import numpy as np

from collections import defaultdict
from config_error_analysis import *
from write_xml import *


class Info_Extraction(object):
    def __init__(self, file_path):
        self.file_path = file_path
        self.id_coordinates = defaultdict(list)  #### 生成每个id对应的轨迹列表 {id:每帧轨迹的坐标} ###
        self.id_centroid = defaultdict(list)  #### {id:每帧轨迹的圆心坐标}
        self.id_frames = defaultdict(list)  ### 生成每个id存在的frame列表 ####
        self.frame_ids = defaultdict(list)  ### 生成每帧存在的id列表 {帧：id } ####
        self.detect_xyxy = defaultdict(list)  ### 生成{帧：框框坐标} 


    def tracker_info(self):
        for each in self.track_item:
            track_id = each.split(', ')[0]
            track_coor = [float(i) for i in each.split(', ')[1:]]
            self.id_coordinates[track_id].append(track_coor)  # {id:每帧轨迹的四个坐标}
            track_xcen = (float(each.split(', ')[1]) + float(each.split(', ')[2])) / 2
            track_ycen = (float(each.split(', ')[3]) + float(each.split(', ')[4])) / 2
            self.id_centroid[track_id].append([track_xcen, track_ycen])  # {id:每帧轨迹的圆心坐标}
            self.id_frames[track_id].append(self.frame_id)
            self.frame_ids[self.frame_id].append(track_id)

    def detection_info(self):
        detect_list = np.array([int(float(coor) / yolo_img_size * re_size) for coor in self.detection])
        detect_list = detect_list.reshape(-1, 4)
        self.detect_xyxy[self.frame_id] = detect_list.tolist()  # 标xml需要
        

    def fid_track_detect_decoding(self):
        file = open(self.file_path, mode='r').readlines()
        frames_nums = len(file)
        print('总共有 %d 帧'%len(file))
        minus_idx = int(file[0].split('  ')[0])
        for f in file:
            self.frame_id = str(int(f.split('  ')[0]) - minus_idx + 1)
            
            track = f.split('  ')[1]
            remove = re.compile('(\d+), (\d+), (\d+)')
            self.track_item = remove.sub('', track).replace(r", (), 'active'", "")[2:-2].split('), (')
            if self.track_item[0]:
                self.tracker_info()
                
            self.detection = f.split('  ')[2]
            self.detection = self.detection.replace('[','').replace(']','').replace(' \n','').split(',')
            if self.detection[0]:
                self.detection_info()
        print('总共有 %d 条轨迹' % len(self.id_coordinates))
        print('检测框的帧数有 %d'%len(self.detect_xyxy))
#         print('第 728 帧的检测框坐标是：', self.detect_xyxy['728'])
        return self.id_coordinates, self.id_centroid, self.id_frames, self.frame_ids, self.detect_xyxy, frames_nums

    
class Error_Detection(object):
    def __init__(self, id_centroids, id_frames, frame_ids, frames_num):
        self.id_centroids = id_centroids
        self.id_frames = id_frames
        self.frame_ids = frame_ids
        self.frames_num = frames_num
        self.idxs = id_frames.keys()   # 拿到所有的轨迹id
        self.enter_frame_corr = defaultdict(list)  # 进入错误的 {帧：圆心}
        self.out_frame_corr = defaultdict(list)   # 出去错误的 {帧：圆心}
        
    def enter_error(self):  # 输入每条轨迹的圆心和轨迹id，判断是不是进入错误
        enter_x = self.id_centroids[self.idx][0][0]
        enter_y = self.id_centroids[self.idx][0][1]
        if enter_x > edge_min and enter_x < edge_max and enter_y < edge_max and enter_y > edge_min:
            return True
        else:
            return False

    def out_error(self):
        out_x = self.id_centroids[self.idx][-1][0]
        out_y = self.id_centroids[self.idx][-1][1]
        if out_x > edge_min and out_x < edge_max and out_y < edge_max and out_y > edge_min:
            return True
        else:
            return False

    def ignore_id(self):  ### 给mozi单个的视频
        self.beignore_id = []
        idx_first_frame = self.frame_ids['1']   #自己调整
        idx_last_frame = self.frame_ids[str(self.frames_num)]
        self.beignore_id = idx_first_frame + idx_last_frame
#         print('出现在视频开始和结尾的非错误id是 ', self.beignore_id)
    
    def main_enter_error_frame_corr(self):
        for self.idx in self.idxs:
            if self.enter_error() and self.idx not in self.beignore_id:
                efc_key = self.id_frames[self.idx][0]
                tgt_centroid = self.id_centroids[self.idx][0]
                efc_value = tuple(int(ctrid*re_size) for ctrid in tgt_centroid)
                self.enter_frame_corr[efc_key].append(efc_value)
        print('进入有问题的帧数有 ', len(self.enter_frame_corr))
        print('进入有问题的帧 ', self.enter_frame_corr)
        return self.enter_frame_corr
    
    def main_out_error_frame_corr(self):
        for self.idx in self.idxs:
            if self.out_error() and self.idx not in self.beignore_id:
                ofc_key = str(int(self.id_frames[self.idx][-1]) - max_age)
                tgt_centroid = self.id_centroids[self.idx][-1 - max_age]
                ofc_value = tuple(int(ctrid*re_size) for ctrid in tgt_centroid)
                self.out_frame_corr[ofc_key].append(ofc_value)
        print('出去有问题的帧数有 ', len(self.out_frame_corr))
        print('出去有问题的帧 ', self.out_frame_corr)
        return self.out_frame_corr
    
    
class SaveErrorImages(object):
    def __init__(self, src_path, enter_frame_corr, out_frame_corr, detect_xyxy):
        self.src_path = src_path
        self.enter_frame_corr = enter_frame_corr
        self.out_frame_corr = out_frame_corr
        self.detect_xyxy = detect_xyxy 
        self.video_name = src_path.split('/')[-1][:-4]
    
    def get_frames(self):
        cap = cv2.VideoCapture(self.src_path)
        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if ret:
                frame_idx += 1
                yield frame, frame_idx
            else:
                break
                
    def tgt_path(self, flag, fid):
        self.tgt_error_imgs_path = os.path.join(root_path, '{}_error_images'.format(flag), '{}_{}.jpg'.format(self.video_name,fid))
        self.tgt_visual_path = os.path.join(root_path, '{}_visualization'.format(flag), '{}_{}.jpg'.format(self.video_name,fid))
        self.tgt_xml_path = os.path.join(root_path, '{}_xml'.format(flag))
        
    
    def save_single_img_xml(self, frame, fid, error_corr):
        cv2.imwrite(self.tgt_error_imgs_path, frame)  # 存有问题的图片
        res_list = self.detect_xyxy[fid]  # 把有问题的那一帧的框框坐标存下来
        xml_write(img_name = "{}_{}".format(self.video_name, fid)
                        ,path_dir = self.tgt_xml_path
                        ,data_dict = {'label':'head', 'imageHeight':re_size, 'imageWidth':re_size, 'bndbox':res_list})
        for i in range(len(self.detect_xyxy[fid])):  
            xmin, ymin, xmax, ymax = self.detect_xyxy[fid][i]
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0,255,0), 2)
            for j in range(len(error_corr[fid])):
                cv2.circle(frame, error_corr[fid][j],10,(0,0,213), -1)
                cv2.imwrite(self.tgt_visual_path, frame)    #存画好框和点的图像
    
    def save_all_imgs_xmls(self):
        print(enter_frame_corr.keys())
        for frame, frame_idx in self.get_frames():
            if frame_idx % 200 == 0:
                print('Finish saving error images in {} frames in {}.avi'.format(frame_idx, self.video_name))
            frame = cv2.resize(frame, (re_size, re_size))
            if str(frame_idx) in self.enter_frame_corr.keys():
                flag = 'enter'
                self.tgt_path(flag, str(frame_idx))
                self.save_single_img_xml(frame, str(frame_idx), self.enter_frame_corr)
                
            if str(frame_idx) in self.out_frame_corr.keys():
                flag = 'out'
                self.tgt_path(flag, str(frame_idx))
                self.save_single_img_xml(frame, str(frame_idx), self.out_frame_corr)

class MysqlWriter(object):
    def __init__(self, enter_frame_corr, out_frame_corr, frames_num):
        self.enter_frame_corr = enter_frame_corr
        self.out_frame_corr = out_frame_corr
        self.frames_num = frames_num
        
    def add_main(self, video_name, model_name):
        add2main = []
        enter_error_fid = self.enter_frame_corr.keys()
        out_error_fid = self.out_frame_corr.keys()
        fid = 1
        while (fid <= file_len):
            if str(fid) in enter_error_fid and str(fid) in out_error_fid:
                add2main.append((video_name, str(fid), model_name, 'Y', 'Y'))
            elif str(fid) in enter_error_fid:
                add2main.append((video_name, str(fid), model_name, 'Y', 'N'))
            elif str(fid) in out_error_fid:
                add2main.append((video_name, str(fid), model_name, 'N', 'Y'))
            else:
                add2main.append((video_name, str(fid), model_name, 'N', 'N'))
            fid += 1
        return add2main
    
    def add_video_path(self):
        add2video = []
        videos = os.listdir(src_video_path)
        for v_name in videos:
            if not v.startswith('.'):
                v_path = os.path.join(src_video_path + v_name)
                add2video.append((v_name, v_path))
        return add2video
    
    def add_pic_path(self):   # video+fid+path
        add2pic = []
        pics = []
        for pic in os.listdir(src_images_path):
            if not pic.startswith('.'):
                pics.append(pic)
        for p in pics:
            video_name = p.split('_')[0] + '.mp4'
            fid = p.split('_')[1][:-4]
            pic_path = os.join.path(src_images_path, p)
            add2pic.append((v_name, fid, pic_path))
        return add2pic
            
            
    def add_xml_error_visualization(self):  #按模型存每次出错的帧/有轨迹帧/xml
        add2xml_error_vi = []
        flags = ['enter','out']
        for flag in flags:
            xml_path = os.path.join(src_xml_error_vi, '{}_xml/'.format(flag))
            xml_data = sorted([i for i in os.listdir(xml_path) if not i.startswith('.')])[:3]
            error_images_path = os.path.join(src_xml_error_vi, '{}_error_images/'.format(flag))
            error_images_data = sorted([i for i in os.listdir(error_images_path) if not i.startswith('.')])[:3]
            visualization_path = os.path.join(src_xml_error_vi, '{}_visualization/'.format(flag))
            visualization_data = sorted([i for i in os.listdir(visualization_path) if not i.startswith('.')])[:3]
            for x, e_imgs, vi in zip(xml_data, error_images_data, visualization_data):
                video = e_imgs.split('_')[0] + '.mp4'
                fid = e_imgs.split('_')[1]
                model = 'm2'
                xml = os.path.join(xml_path, x)
                error_images = os.path.join(error_images_path, e_imgs)
                visualization = os.path.join(visualization_path, vi)
                add2xml_error_vi.append((video,fid,model,xml,error_images,visualization))
        return add2xml_error_vi
                
                
