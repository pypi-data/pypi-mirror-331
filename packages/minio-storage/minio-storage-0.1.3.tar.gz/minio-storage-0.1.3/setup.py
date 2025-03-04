# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 11:52:58 2024

@author: yangl
"""

from setuptools import setup, find_packages

# with open('minio_storage.minio_storage API documentation.html', 'r') as f:
#     long_description = f.read()

setup(
      name="minio-storage",
      version="0.1.3",
      author="holmeschang",
      author_email="yangloong@live.com.my",
      description="minio simplified",
      # long_description=long_description,  # Add HTML docs here
      # long_description_content_type='text/markdown',  # Specify that it is HTML      
      packages=find_packages(),
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
      ],
      python_requires=">=3.6",
      install_requires=[
        "minio>=7.2.7",  
        "neuon>=0.0.1",     
      ],
      )
