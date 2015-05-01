#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Pedro Tome <Pedro.Tome@idiap.ch>

import bob.palmvein

HISTOGRAM_EQUALIZATION = False

PADDING_OFFSET = 5
PADDING_THRESHOLD = 0 #Threshold for padding black zones

ROI_REGION = False

IMG_ROTATE = True

GPU_ACCELERATION = False

# define the preprocessor
preprocessor = bob.palmvein.preprocessing.PalmCrop(
	heq = HISTOGRAM_EQUALIZATION,
	padding_offset = PADDING_OFFSET,
	padding_threshold = PADDING_THRESHOLD,
    roi = ROI_REGION,
    rotate = IMG_ROTATE,
	gpu = GPU_ACCELERATION
)

