import logging
import threading
import time
import requests
import os
import json
import glob
from concurrent.futures import ProcessPoolExecutor
import shutil
import tarfile
import gdown

url = "https://api.facemorph.me/api"
encode_image = "/encodeimage"
generate_image = "/face"
hash_list = []
dataset_id = "1hYIZadxcPG27Fo7mQln0Ey7uqw1DoBvM"
output = "CACD2000.tar.gz"


def img_format(image):
	os.makedirs("preprocessed", exist_ok=True)
	logging.info("Thread %s: starting", image)
	data = {'usrimg': open(image, 'rb')}
	j = {'tryalign': True }
	r = requests.post(url + encode_image, files = data, data = j)
	values = {'guid': json.loads(r.content)['guid']}
	r = requests.get(url + generate_image, params = values, stream=True)
	with open("preprocessed/" + image, 'wb') as out_file:
		shutil.copyfileobj(r.raw, out_file)
	logging.info("Thread %s: finishing", image)


format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

logging.info("Downloading Dataset")
gdown.download(id=dataset_id, output=output, quiet=False)

logging.info("Extracting Dataset")
dataset = tarfile.open(output)
dataset.extractall()
dataset.close

logging.info("Deleting first half")
os.chdir('CACD2000')
images = glob.glob('*.jpg')
images = images[79500:158400]
print("Now Processing: ", len(images))

logging.info("Pre-Processing Start")
pool = ProcessPoolExecutor(max_workers=35)

results = pool.map(img_format, images)
pool.shutdown(wait=True)
