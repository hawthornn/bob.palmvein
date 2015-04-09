#!/usr/bin/env python

import facereclib

# setup of the grid parameters
# define a queue with demanding parameters
grid = facereclib.utils.GridParameters(
  training_queue = '8G',
  # preprocessing
  number_of_preprocessing_jobs = 32,
  preprocessing_queue = '4G-io-big',
  # feature extraction
  number_of_extraction_jobs = 32,
  extraction_queue = '4G-io-big',
  # feature projection
  number_of_projection_jobs = 32,
  projection_queue = {},
  # model enrollment
  number_of_enrollment_jobs = 32,
  enrollment_queue = {},
  # scoring
  number_of_scoring_jobs = 32,
  scoring_queue = {'queue': 'q_gpu'},
)

