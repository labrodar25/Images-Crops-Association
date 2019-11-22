import os
import urllib.request



class imageCropAssociation:
	def getFiles(filePath):
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







