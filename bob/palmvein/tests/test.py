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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


"""Test Units
"""

import unittest
import bob.io.base
import bob.io.matlab
import os
import pkg_resources

def F_pre(name, f):
  """Returns the test file on the "data" subdirectory"""
  return pkg_resources.resource_filename(name, os.path.join('preprocessing', f))

def F_feat(name, f):
  """Returns the test file on the "data" subdirectory"""
  return pkg_resources.resource_filename(name, os.path.join('features', f))

def F_mat(name, f):
  """Returns the test file on the "data" subdirectory"""
  return pkg_resources.resource_filename(name, os.path.join('matching', f))


class PalmveinTests(unittest.TestCase):

  def test_palm_crop(self):
    """Test palm vein image preprocessing"""
    #import numpy
    #input_filename = F_pre(__name__, '0019_3_1_120509-160517.png')
    #output_img_filename  = F_pre(__name__, '0019_3_1_120509-160517_img_lee_huang.mat')
    #output_fvr_filename  = F_pre(__name__, '0019_3_1_120509-160517_fvr_lee_huang.mat')
        
    #img = bob.io.base.load(input_filename)
    
    #from bob.palmvein.preprocessing.PalmCrop import PalmCrop
    #PC = PalmCrop(4, 40, False, False)
    #output_img, palm_mask_norm, palm_mask2 = PC(img)

    # Load Matlab reference
    #output_img_ref = bob.io.base.load(output_img_filename)
    #output_fvr_ref = bob.io.base.load(output_fvr_filename)
    
    # Compare output of python's implementation to matlab reference
    # (loose comparison!)
    #For debugging    
    #import ipdb; ipdb.set_trace()    
       
    #self.assertTrue(numpy.mean(numpy.abs(output_img - output_img_ref)) < 1e2)

    return True

  

