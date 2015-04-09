#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Pedro Tome <Pedro.Tome@idiap.ch>

import bob.palmvein

# Parameters

BLOCK_SIZE = 59    # one or two parameters for block size
BLOCK_OVERLAP = 15 # one or two parameters for block overlap


# LBP parameters
LBP_RADIUS = 7
LBP_NEIGHBOR_COUNT = 16
LBP_UNIFORM = True
LBP_CIRCULAR = True
LBP_ROTATION_INVARIANT = False
LBP_COMPARE_TO_AVERAGE = False
LBP_ADD_AVERAGE = False
# histogram options
SPARSE_HISTOGRAM = False
SPLIT_HISTOGRAM = None
      


#Define feature extractor
feature_extractor = bob.palmvein.features.LocalBinaryPatterns(
  block_size = BLOCK_SIZE,    # one or two parameters for block size
  block_overlap = BLOCK_OVERLAP, # one or two parameters for block overlap
  lbp_radius = LBP_RADIUS,
  lbp_neighbor_count = LBP_NEIGHBOR_COUNT,
  lbp_uniform = LBP_UNIFORM,
  lbp_circular = LBP_CIRCULAR,
  lbp_rotation_invariant = LBP_ROTATION_INVARIANT,
  lbp_compare_to_average = LBP_COMPARE_TO_AVERAGE,
  lbp_add_average = LBP_ADD_AVERAGE,
  # histogram options
  sparse_histogram = SPARSE_HISTOGRAM,
  split_histogram = SPLIT_HISTOGRAM,
)

