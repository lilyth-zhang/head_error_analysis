import cv2
import os
import re
import numpy as np

from collections import defaultdict
from config_error_analysis import *
from write_xml import *
from error_detection import *


if __name__ == '__main__':
    root = './example_assets'
    for f in os.listdir(root):
        if f.endswith('.txt'):
            fpath = os.path.join(root, f)
            src_path = fpath.replace('.txt','.avi')
            info = Info_Extraction(fpath)
            id_coordinates, id_centroids, id_frames, frame_ids, detect_xyxy, frames_num = info.fid_track_detect_decoding()

            error_detector = Error_Detection(id_centroids, id_frames, frame_ids, frames_num)
            error_detector.ignore_id()
            enter_frame_corr = error_detector.main_enter_error_frame_corr()
            out_frame_corr = error_detector.main_out_error_frame_corr()

    
            save_tool = SaveErrorImages(src_path, enter_frame_corr, out_frame_corr, detect_xyxy )      
            save_tool.save_all_imgs_xmls()