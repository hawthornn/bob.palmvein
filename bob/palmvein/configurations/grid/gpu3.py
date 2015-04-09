#!/usr/bin/env python

import facereclib

# setup of the grid parameters
# define a queue with demanding parameters
grid = facereclib.utils.GridParameters(
  training_queue = '8G',
  # preprocessing
  number_of_preprocessings_per_job = 1000,
  preprocessing_queue = {},
  # feature extraction
  number_of_extracted_features_per_job = 1000,
  extraction_queue = {},
  # feature projection
  number_of_projected_features_per_job = 1000,
  projection_queue = {},
  # model enrollment
  number_of_enrolled_models_per_job = 100,
  enrollment_queue = '2G',
  # scoring
  number_of_models_per_scoring_job = 1500,
  scoring_queue = {'queue': 'q_gpu'},
)

