import sys
import argparse
import os

from image_association import imageCropAssociation

def main():
	parser = argparse.ArgumentParser()
	group_images = parser.add_mutually_exclusive_group(required=True)
	group_images.add_argument("--images", help="Path to images folder")
	group_images.add_argument("--image_url_file", help="Path to images URL file")
	
	crop_images = parser.add_mutually_exclusive_group(required=True)
	crop_images.add_argument("--crops", help="Path to crops images folder")
	crop_images.add_argument("--crops_url_file", help="Path to crops URL file")
	
	parser.add_argument("--output", required=True, help="Path to save output results")
	parser.add_argument('-g', "--groundtruth", default=None, help="Give path to groundtruth file")
	args = vars(parser.parse_args())
		
	image_association_obj = imageCropAssociation()
	
	if args['image_url_file'] and args['crops_url_file'] is not None:
		imagesFilePaths = image_association_obj.getFiles(args.image_url_file)
		cropsFilePaths = image_association_obj.getFiles(args.crops_url_file)
	elif args['images'] and args['crops']:
		imagesFilePaths = os.listdir(args['images'])
		cropsFilePaths = os.listdir(args['crops'])

		imagesFilePaths = [args['images'] + filename for filename in imagesFilePaths]
		cropsFilePaths = [args['crops'] + filename for filename in cropsFilePaths]
		
	
	image_association_obj.findAssociations(imagesFilePaths, cropsFilePaths, args['output'])
	
	if args['groundtruth']:
		image_association_obj.num_crops = len([name for name in os.listdir(args['crops'])])
		result_df = image_association_obj.evaluateAssociations(args['output'], args['groundtruth'])
		print("Average Accuracy is : ", result_df['accuracy'].mean())
		print("Average Recall is : ", result_df['recall'].mean())
		print("Average Precision is : ", result_df['precision'].mean())
	
	print("Successfully matched the crops to their associated Images............")

if __name__ == '__main__':
    main()