#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Pedro Tome <Pedro.Tome@idiap.ch>
#
# Copyright (C) 2015 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import bob.ip.base
import bob.io.base
import numpy
import math
#from math import pi 
#from mumpy import sqrt
import scipy.signal
from facereclib.features.Extractor import Extractor
from .. import utils
#from facereclib.utils import histogram

class LocalBinaryPatterns (Extractor):
  
  """LBP feature extractor, paramters fixed based on 
     L. Mirmohamadsadeghi and A. Drygajlo. Palm vein recognition uisng local texture patterns, IET Biometrics, pp. 1-9, 2013.
  """

  def __init__(
      self,
      # Block setup
      block_size = 59,    # one or two parameters for block size
      block_overlap = 15, # one or two parameters for block overlap
      # LBP parameters
      lbp_radius = 7,
      lbp_neighbor_count = 16,
      lbp_uniform = True,
      lbp_circular = True,
      lbp_rotation_invariant = False,
      lbp_compare_to_average = False,
      lbp_add_average = False,
      # histogram options
      sparse_histogram = False,
      split_histogram = None
      
  ):

    # call base class constructor
    Extractor.__init__(
        self,
        # Block setup
        block_size = block_size,
        block_overlap = block_overlap,
        #LBP parameters
        lbp_radius = lbp_radius,
        lbp_neighbor_count = lbp_neighbor_count,
        lbp_uniform = lbp_uniform,
        lbp_circular = lbp_circular,
        lbp_rotation_invariant = lbp_rotation_invariant,
        lbp_compare_to_average = lbp_compare_to_average,
        lbp_add_average = lbp_add_average,
        sparse_histogram = sparse_histogram,
        split_histogram = split_histogram
    )
    
    # block parameters
    self.m_block_size = block_size if isinstance(block_size, (tuple, list)) else (block_size, block_size)
    self.m_block_overlap = block_overlap if isinstance(block_overlap, (tuple, list)) else (block_overlap, block_overlap)
    if self.m_block_size[0] < self.m_block_overlap[0] or self.m_block_size[1] < self.m_block_overlap[1]:
      raise ValueError("The overlap is bigger than the block size. This won't work. Please check your setup!")
    
    self.m_lbp = bob.ip.base.LBP(
        neighbors = lbp_neighbor_count,
        radius = float(lbp_radius),
        circular = lbp_circular,
        to_average = lbp_compare_to_average,
        add_average_bit = lbp_add_average,
        uniform = lbp_uniform,
        rotation_invariant = lbp_rotation_invariant,
        border_handling = 'wrap'
    )


    self.m_split = split_histogram
    self.m_sparse = sparse_histogram
    if self.m_sparse and self.m_split:
      raise ValueError("Sparse histograms cannot be split! Check your setup!")


  def __fill__(self, lbphs_array, lbphs_blocks, j):
    """Copies the given array into the given blocks"""
    # fill array in the desired shape
    #For debugging    
    #import ipdb; ipdb.set_trace()    
    for b in range(self.m_n_blocks):
      lbphs_array[b * self.m_n_bins : (b+1) * self.m_n_bins] = lbphs_blocks[b][:]
    

  def lbp_features(self, palm_image):
    """Computes and returns the LBP features for the given input palmvein image"""
   
    # For debugging    
    #import ipdb; ipdb.set_trace()    
        
    palm_image = palm_image.astype(numpy.float64)
    
    # Computes LBP histograms
    abs_blocks = bob.ip.base.lbphs(palm_image, self.m_lbp, self.m_block_size, self.m_block_overlap)

    # Converts to Blitz array (of different dimensionalities)
    self.m_n_bins = abs_blocks.shape[1]
    self.m_n_blocks = abs_blocks.shape[0]
    
    shape = self.m_n_bins * self.m_n_blocks
    
    # create new array 
    lbphs_array = numpy.zeros(shape, 'float64')
    
    #For debugging    
    #import ipdb; ipdb.set_trace()                
    
    # fill the array with the absolute values of the Gabor wavelet transform
    self.__fill__(lbphs_array, abs_blocks, 0)
    
    # return the concatenated list of all histograms
    return lbphs_array
    
    
  def __call__(self, image):    
    """Reads the input image, extract the features based on LBP of the palmvein image, and writes the resulting template"""
    #For debugging    
        
    #palm_image = image[0]  #Image original
    palm_image = image[1]   #Normalized image with histogram equalization
        
    return self.lbp_features(palm_image)  
    
    
  def save_feature(self, feature, feature_file):
    f = bob.io.base.HDF5File(feature_file, 'w')
    f.set('feature', feature)
    
  def read_feature(self, feature_file):
    f = bob.io.base.HDF5File(feature_file, 'r')
    image = f.read('feature')
    return (image)