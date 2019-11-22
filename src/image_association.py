import os
import urllib.request
import cv2  
import numpy as np  
from collections import defaultdict
import json
import pandas as pd


class imageCropAssociation:
	num_crops = 0
	
	def __findMatchingCoordinates(self, imagePath, templatePath):
		image = cv2.imread(imagePath, cv2.IMREAD_GRAYSCALE)  
		template = cv2.imread(templatePath, cv2.IMREAD_GRAYSCALE)  

		w, h = template.shape[::-1] 
		
		image_w, image_h = image.shape[::-1]
		
		if(w > image_w or h > image_h):
			return []

		result = cv2.matchTemplate(image,template,cv2.TM_CCOEFF_NORMED)  
		threshold = 0.99
		loc = np.where( result >= threshold) 
		
		crop_image_name = templatePath.rsplit('/', 1)[-1]
		crop_image_name = crop_image_name.rsplit('.',1)[0]
		for pt in zip(*loc[::-1]): 
			return [crop_image_name, [int(pt[0]),int(pt[1]), int(pt[0] + w), int(pt[1] + h)]]
		return []


	def getFiles(self, filePath):
		filenames_list = [line.rstrip('\n') for line in open(filePath)]
		output_path = filePath.split('.txt')[0]
		outFileList = []
		for filename in filenames_list:
			out_file = output_path + "/" + filename.rsplit('/', 1)[-1]
			os.makedirs(os.path.dirname(out_file), exist_ok=True)
			urllib.request.urlretrieve(filename, out_file) 
			outFileList.append(out_file)
		print('Retrieved data files......')
		return outFileList
	
	
	def findAssociations(self, imagesFilePaths, cropsFilePaths, outputFilePath):
		print('Finding Image Associations... ')
		associations = defaultdict(list)
		assoc_crops = []

		for imagePath in imagesFilePaths:
			for cropPath in cropsFilePaths:
				assoc = self.__findMatchingCoordinates(imagePath, cropPath)
				image_name = imagePath.rsplit('/', 1)[-1]
				image_name = image_name.rsplit('.',1)[0]
				if assoc:
					associations[image_name].append(assoc)
					assoc_crops.append(cropPath)
			if image_name not in associations:
				associations[image_name] = []

		nonassoc_crops = list(set(cropsFilePaths) - set(assoc_crops))
		nonassoc_crops = [crop_path.rsplit('/', 1)[-1] for crop_path in nonassoc_crops]
		nonassoc_crops = [crop_path.rsplit('.', 1)[0] for crop_path in nonassoc_crops]

		associations['NA'] = nonassoc_crops
		
		os.makedirs(os.path.dirname(outputFilePath), exist_ok=True)

		with open(outputFilePath, 'w') as fp:
			json.dump(dict(associations), fp,indent=4, sort_keys=True)
		print('Successfully written to output file. Check output folder for the json files... ')

		
	def __calc_precision_recall(self, row):
		l1 = row['calc']
		l2 = row['ground_truth']
		
		l2_alias = []
		
		if type(l2) == list:
			l2_alias = l2
			
		tp = len([x for x in l2_alias if x in l1])
		fp =len([x for x in l1 if x not in l2_alias]) 
		fn = len([x for x in l2_alias if x not in l1])
		tn = self.num_crops - tp - fp - fn
		
		accuracy = (tp+tn)/self.num_crops
		recall = tp/(tp + fn) if tp else 0
		precision = tp/(tp + fp) if tp else 0
		
		return accuracy, recall, precision


	def evaluateAssociations(self, labelled_path, groundTruth_path):
		print('Evaluating the model, calculating Accuracy, Precision, Recall... ')
		calc_series = pd.read_json(labelled_path, typ='series')
		calc_df= pd.DataFrame(calc_series)
		calc_df = calc_df.rename(columns={0: "calc"})
		
		truth_series = pd.read_json(groundTruth_path, typ='series')
		truth_df= pd.DataFrame(truth_series)
		truth_df = truth_df.rename(columns={0: "ground_truth"})
		
		result_df = pd.concat([truth_df,calc_df], axis=1)
		
		result_df['accuracy'], result_df['recall'], result_df['precision'] = zip(*result_df.apply(self.__calc_precision_recall, axis=1))
		
		return result_df