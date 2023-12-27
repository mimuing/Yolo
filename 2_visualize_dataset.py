import os
import cv2
import re
import pandas as pd
import numpy as np

def visualize_dataset(image_path, label_path, view_half_size = False):
	def sorted_Is(image_path):
		mtime = lambda f: os.stat(os.path.join(image_path, f)).st_mtime
		return list(sorted(os.listdir(image_path), key=mtime))

	img_name = sorted_Is(image_path)
	img_name_only = [re.sub('.jpg', '', i) for i in img_name]


	for img in img_name:
		image = cv2.imread(os.path.join(image_path, img))
		img_hei, img_wid, channel = image.shape

		label_name = re.sub('.jpg', '.txt', img)
		f = open(os.path.join(label_path, label_name), 'r')
		with open(os.path.join(label_path,label_name), 'r') as file:
			line = None # 변수 line 을 None 으로 초기화
			while line != '':
				line = file.readline()
				line_list = line.split()
				if line_list == []:
					continue
				else:
					line_list = list(map(float, line_list))
					line_list[0] = int(line_list[0])
					label_list = line_list
					# bbox_list = [x_start, y_start, wid, hei]
					bbox_list = [label_list[1]-label_list[3]/2, label_list[2]-label_list[4]/2, label_list[3], label_list[4]]
					bbox_list[0] = bbox_list[0] * img_wid
					bbox_list[1] = bbox_list[1] * img_hei
					bbox_list[2] = bbox_list[2] * img_wid
					bbox_list[3] = bbox_list[3] * img_hei
					bbox_list = list(map(int, bbox_list))
					cv2.rectangle(image, (bbox_list[0], bbox_list[1]), (bbox_list[0]+bbox_list[2], bbox_list[1]+bbox_list[3]), (255, 0, 0), 3)
		if view_half_size:
			img_view = cv2.resize(image, (image.shape[1] // 2, image.shape[0] // 2))
		else:
			img_view = image

		cv2.imshow('image', img_view)
		cv2.waitKey(0)
		cv2.waitKey(0)

	pass


if __name__ == '__main__':
	image_path = 'dataset\\pattern_2\\test\\images'
	label_path = 'dataset\\pattern_2\\test\\labels'
	visualize_dataset(image_path, label_path, view_half_size=True)