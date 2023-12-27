import os
import json
import cv2

def visualize_labeling(json_file, image_path, view_half_size = False):
	f = open(json_file)
	labeling = json.load(f)
	f.close()

	for image in labeling['images']:
		image_name = image['image_name']
		print(image_name)
		img = cv2.imread(os.path.join(image_path, image_name))

		for label in image['labels']:
			class_name = label['class_name']
			class_id = int(class_name[-1]) - 1
			bbox = label['bbox']
			if bbox == []:
				continue
			else:
				cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255, 0, 0), 3)

		if view_half_size:
			img_view = cv2.resize(img, (img.shape[1]//2, img.shape[0]//2))
		else:
			img_view = img


		cv2.imshow('img', img_view)
		cv2.waitKey(0)



if __name__ == '__main__':
	json_file = 'faultdetection_pattern_1_JSON_20210906_v2.json'
	image_path = 'pattern_1'
	visualize_labeling(json_file, image_path, view_half_size=True)