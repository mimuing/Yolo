import os
import json
import shutil
import random
import math

def make_dataset(json_file, total_image_path, train_image_path, train_label_path, val_image_path, val_label_path,
                 test_image_path, test_label_path, val_proportion, test_proportion, num_trials):
	f = open(json_file)
	labeling = json.load(f)
	f.close()

	num_cls = len(labeling['label_classes'])
	print('num_cls:', num_cls)

	total_num_labels_for_cls = [0]* num_cls

	for image in labeling['images']:
		for label in image['labels']:
			cls_id = int(label['class_name'][-1]) - 1
			total_num_labels_for_cls[cls_id] += 1

	desired_val_num_labels_for_cls = [round(num_labels * val_proportion) for num_labels in total_num_labels_for_cls]
	desired_test_num_labels_for_cls = [round(num_labels * test_proportion) for num_labels in total_num_labels_for_cls]

	list_of_list_of_images = []
	for i in range(num_trials):
		random.shuffle(labeling['images'])
		list_of_list_of_images.append(labeling['images'].copy())

	val_margin = 1 if val_proportion > 0 else 0
	test_margin = 1 if test_proportion > 0 else 0
	num_label_errors_for_cls = []

	for list_of_images in list_of_list_of_images:
		train_num_labels_for_cls = [0] * num_cls
		val_num_labels_for_cls = [0] * num_cls
		test_num_labels_for_cls = [0] * num_cls

		for image in list_of_images:
			num_labels_for_cls_in_image = [0] * num_cls

			for label in image['labels']:
				cls_id = int(label['class_name'][-1]) - 1
				num_labels_for_cls_in_image[cls_id] += 1

			label_exist = sum(num_labels_for_cls_in_image) > 0
			add_to_test = label_exist
			add_to_val = label_exist

			for cls_id in range(num_cls):
				add_to_test = add_to_test and test_num_labels_for_cls[cls_id] + num_labels_for_cls_in_image[cls_id]\
				              <= desired_test_num_labels_for_cls[cls_id] + test_margin
				add_to_val = add_to_val and val_num_labels_for_cls[cls_id] + num_labels_for_cls_in_image[cls_id]\
				             <= desired_val_num_labels_for_cls[cls_id] + val_margin

			dst_num_labels_for_cls = train_num_labels_for_cls
			if add_to_test: dst_num_labels_for_cls = test_num_labels_for_cls
			elif add_to_val: dst_num_labels_for_cls = val_num_labels_for_cls

			for label in image['labels']:
				cls_id = int(label['class_name'][-1]) - 1
				dst_num_labels_for_cls[cls_id] += 1

		test_num_errors = [(x-y)*(x-y) for x, y in zip(test_num_labels_for_cls, desired_test_num_labels_for_cls)]
		val_num_errors = [(x-y)*(x-y) for x, y in zip(val_num_labels_for_cls, desired_val_num_labels_for_cls)]
		num_label_errors_for_cls.append(sum(test_num_errors) + sum(val_num_errors))

	best_list_of_images = list_of_list_of_images[num_label_errors_for_cls.index(min(num_label_errors_for_cls))]

	train_num_labels_for_cls = [0] * num_cls
	val_num_labels_for_cls = [0] * num_cls
	test_num_labels_for_cls = [0] * num_cls

	for image in best_list_of_images:
		num_labels_for_cls_in_image = [0] * num_cls

		for label in image['labels']:
			cls_id = int(label['class_name'][-1]) - 1
			num_labels_for_cls_in_image[cls_id] += 1

		label_exist = sum(num_labels_for_cls_in_image) > 0
		add_to_test = label_exist
		add_to_val = label_exist

		for cls_id in range(num_cls):
			add_to_test = add_to_test and test_num_labels_for_cls[cls_id] + num_labels_for_cls_in_image[cls_id] \
			              <= desired_test_num_labels_for_cls[cls_id] + test_margin
			add_to_val = add_to_val and val_num_labels_for_cls[cls_id] + num_labels_for_cls_in_image[cls_id] \
			             <= desired_val_num_labels_for_cls[cls_id] + val_margin

		dst_image_path = train_image_path
		dst_label_path = train_label_path
		dst_num_labels_for_cls = train_num_labels_for_cls

		if add_to_test:
			dst_image_path = test_image_path
			dst_label_path = test_label_path
			dst_num_labels_for_cls = test_num_labels_for_cls
		elif add_to_val:
			dst_image_path = val_image_path
			dst_label_path = val_label_path
			dst_num_labels_for_cls = val_num_labels_for_cls

		image_name = image['image_name']
		label_name = os.path.splitext(image_name)[0] + '.txt'
		shutil.copy(os.path.join(total_image_path, image_name), os.path.join(dst_image_path, image_name))

		with open(os.path.join(dst_label_path, label_name), 'w') as f:
			for label in image['labels']:
				cls_id = int(label['class_name'][-1]) - 1 # 문자를 숫자로 변환해서 적용
				dst_num_labels_for_cls[cls_id] += 1
				bbox = label['bbox']
				# code 작성 시작
				img_hei = image['height']
				img_wid = image['width']
				x_center = bbox[0] + (bbox[2] - bbox[0]) / 2
				y_center = bbox[1] + (bbox[3] - bbox[1]) / 2
				width = (bbox[2] - bbox[0]) 
				height = (bbox[3] - bbox[1])
				x_center_nor = x_center/img_wid 
				y_center_nor = y_center/img_hei 
				width_nor = width/img_wid  
				height_nor = height/img_hei 
				f.write(f'{cls_id} {x_center_nor} {y_center_nor} {width_nor} {height_nor}\n')

	print('total_num_labels_for_cls:', total_num_labels_for_cls)
	print('desired_val_num_labels_for_cls:', desired_val_num_labels_for_cls)
	print('        val_num_labels_for_cls:', val_num_labels_for_cls)
	print('desired_test_num_labels_for_cls:', desired_test_num_labels_for_cls)
	print('        test_num_labels_for_cls:', test_num_labels_for_cls)
	test_num_errors = [(x - y) * (x - y) for x, y in zip(test_num_labels_for_cls, desired_test_num_labels_for_cls)]
	val_num_errors = [(x - y) * (x - y) for x, y in zip(val_num_labels_for_cls, desired_val_num_labels_for_cls)]
	rms_test_num_error = math.sqrt(sum(test_num_errors)/len(test_num_errors))
	rms_val_num_error = math.sqrt(sum(val_num_errors)/len(val_num_errors))
	print('rms_test_num_error:', rms_test_num_error)
	print('rms_val_num_error:', rms_val_num_error)


if __name__ == '__main__':
	json_file = 'faultdetection_pattern_2_JSON_20210906_v2.json'
	total_image_path = 'pattern_2'
	train_image_path = 'dataset/pattern_2/train/images'
	train_label_path = 'dataset/pattern_2/train/labels'
	val_image_path = 'dataset/pattern_2/val/images'
	val_label_path = 'dataset/pattern_2/val/labels'
	test_image_path = 'dataset/pattern_2/test/images'
	test_label_path = 'dataset/pattern_2/test/labels'
	val_proportion = 0.2
	test_proportion = 0.1
	num_trials = 5000

	if os.path.exists(train_image_path): shutil.rmtree(train_image_path)
	if os.path.exists(train_label_path): shutil.rmtree(train_label_path)
	if os.path.exists(val_image_path): shutil.rmtree(val_image_path)
	if os.path.exists(val_label_path): shutil.rmtree(val_label_path)
	if os.path.exists(test_image_path): shutil.rmtree(test_image_path)
	if os.path.exists(test_label_path): shutil.rmtree(test_label_path)

	os.makedirs(train_image_path)
	os.makedirs(train_label_path)
	os.makedirs(val_image_path)
	os.makedirs(val_label_path)
	os.makedirs(test_image_path)
	os.makedirs(test_label_path)

	make_dataset(json_file, total_image_path, train_image_path, train_label_path, val_image_path, val_label_path,
	             test_image_path, test_label_path, val_proportion, test_proportion, num_trials)