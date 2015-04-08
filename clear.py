#!/usr/bin/env python
import os
from config import *
for post_file in os.listdir(postsDir):
	os.remove(postsDir+post_file)
for post_file in os.listdir(postsFileDir):
	os.remove(postsFileDir+post_file)