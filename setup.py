from setuptools import setup
from setuptools import find_packages

setup(name='Images-Crops-Association',
      version='1.0',
      description='Find association for Images and Crops',
      author='Vijay Balaji',
      install_requires=[
                        'os',
                        'urllib.request',
						'cv2',
						'numpy',
						'collections',
						'json',
						'pandas',
						'argparse',
						'sys',
                        ],
      packages=find_packages())