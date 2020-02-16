import os
import cv2
import numpy as np
from xml.dom.minidom import *

def xml_write(img_name,path_dir,data_dict):
    doc=Document()
    root=doc.createElement('annotation')
    doc.appendChild(root)

    #创建二级节点
    folder = doc.createElement('folder')
    folder.appendChild(doc.createTextNode('images'))
    root.appendChild(folder)

    filename = doc.createElement('filename')
    filename.appendChild(doc.createTextNode(img_name+".jpg"))
    root.appendChild(filename)

    path = doc.createElement('path')
    path.appendChild(doc.createTextNode('D:\\images\\'+img_name+".jpg"))
    root.appendChild(path)

    source = doc.createElement('source')
    database = doc.createElement('database')
    database.appendChild(doc.createTextNode('Unknown'))
    source.appendChild(database)
    root.appendChild(source)

    size = doc.createElement('size')
    width = doc.createElement('width')
    width.appendChild(doc.createTextNode(str(data_dict["imageWidth"])))
    height = doc.createElement('height')
    height.appendChild(doc.createTextNode(str(data_dict["imageHeight"])))
    depth = doc.createElement('depth')
    depth.appendChild(doc.createTextNode('3'))
    size.appendChild(width)
    size.appendChild(height)
    size.appendChild(depth)
    root.appendChild(size)

    segmented = doc.createElement('segmented')
    segmented.appendChild(doc.createTextNode('0'))
    root.appendChild(segmented)

    for one in data_dict["bndbox"]:
        objects = doc.createElement('object')
        name = doc.createElement('name')
        name.appendChild(doc.createTextNode(data_dict["label"]))
        pose = doc.createElement('pose')
        pose.appendChild(doc.createTextNode('Unspecified'))
        truncated = doc.createElement('truncated')
        truncated.appendChild(doc.createTextNode('0'))
        difficult = doc.createElement('difficult')
        difficult.appendChild(doc.createTextNode('0'))
        bndbox = doc.createElement('bndbox')
        xmin = doc.createElement('xmin')
        xmin.appendChild(doc.createTextNode(str(one[0])))
        ymin = doc.createElement('ymin')
        ymin.appendChild(doc.createTextNode(str(one[1])))
        xmax = doc.createElement('xmax')
        xmax.appendChild(doc.createTextNode(str(one[2])))
        ymax = doc.createElement('ymax')
        ymax.appendChild(doc.createTextNode(str(one[3])))
        bndbox.appendChild(xmin)
        bndbox.appendChild(ymin)
        bndbox.appendChild(xmax)
        bndbox.appendChild(ymax)
        objects.appendChild(name)
        objects.appendChild(pose)
        objects.appendChild(truncated)
        objects.appendChild(difficult)
        objects.appendChild(bndbox)
        root.appendChild(objects)

    path_name = os.path.join(path_dir,img_name + ".xml")
    #存成xml文件
    fp=open(path_name,'w',encoding='utf-8')
    doc.writexml(fp,indent='',addindent='\t',newl='\n',encoding='utf-8')
    fp.close()
    
    
    
# if __name__ == '__main__':
    # img_name 是文件名
    # path_dir 是保存目录
    # res_list 是框坐标，相对于imageHeight和imageWidth的结果
#             res_list = []
#             for s, b in zip(scores[0], bboxes[0]):
#                 if s > 0.195:
#                     x0,y0,x1,y1= b.asnumpy()
#                     x0,y0,x1,y1 = int(x0),int(y0),int(x1),int(y1)
#                     x0 = int(x0 / ref_W * W)
#                     x1 = int(x1 / ref_W * W)
#                     y0 = int(y0 / ref_H * H)
#                     y1 = int(y1 / ref_H * H)
#                     res_list.append([x0,y0,x1,y1])


#     res_list = [[100,100, 200, 200],[300,300,400,400]]
#     xml_write(img_name='file_name'
#               ,path_dir='./'
#               ,data_dict={'label': 'head', 'imageHeight': 1440, 'imageWidth':1440, 'bndbox':res_list})
# 