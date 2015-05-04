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

import bob
import numpy
import math
import scipy.signal

from facereclib.tools.Tool import Tool

class HammingDistance (Tool):
  """Finger vein matching: match ratio based on
     Iris recognition algorithems
  """

  def __init__(
      self,
      shifts = 8,   # shift template left and right
      nscales = 8,     
  ):

    # call base class constructor
    Tool.__init__(
        self,

        shifts = shifts,
        nscales = nscales,

        multiple_model_scoring = None,
        multiple_probe_scoring = None
    )

    self.shifts = shifts
    self.nscales = nscales
    
  def enroll(self, enroll_features):
    """Enrolls the model by computing an average graph for each model"""
    # return the generated model
    return numpy.vstack(enroll_features)


  def __shiftbits__(template, noshifts, nscales):

    templatenew = numpy.zeros(template.shape)

    width = template.shape[1]
    s = round(2 * nscales * abs(noshifts) )
    p = round(width - s)

    if noshifts == 0:
      templatenew = template
      # if noshifts is negatite then shift towards the left
    elif noshifts < 0:
      x = range(0,p)
      templatenew[:,x] = template[:,s+x]
      x = range(p,width)
      templatenew[:,x] = template[:,x-p]
    else:
      x=range(s,width)
      templatenew[:,x] = template[:,x-s]
      x=range(0,s)
      templatenew[:,x] = template[:,p+x]
    
    return templatenew
    
  def score(self, model, probe):
    """Computes the score of the probe and the model
         Return score - Value between 0 and 0.5, larger value is better match
    """
    template1 = probe.astype(numpy.bool)
    mask1 = numpy.zeros(probe.shape, numpy.bool)

    n_models = model.shape[0]
    scores = []
    for i in range(n_models):
      template2 = model[i,:].astype(numpy.bool)
      mask2 = numpy.zeros(model[i,:].shape, numpy.bool)

      hd = numpy.NaN
      # shift template left and right, use the lowest Hamming distance
      for shifts in range(-self.shifts,self.shifts+1):
      
        template1s = __shiftbits__(template1, shifts, self.scales)
        mask1s = __shiftbits__(mask1, shifts, self.scales)
        
        mask = numpy.logical_or(mask1s, mask2)
        
        nummaskbits = sum(sum(mask == 1))
        
        totalbits = (template1s.shape[0]*template1s.shape[1]) - nummaskbits
        C = numpy.logical_xor(template1s,template2)
        C = C and numpy.logical_not(mask)
        bitsdiff = sum(sum(C == 1))
        if totalbits == 0:
          hd = numpy.NaN
        else:
          hd1 = bitsdiff / totalbits
          if  hd1 < hd or numpy.isnan(hd):
              hd = hd1
              
      scores.append(hd)

    return numpy.mean(scores)
    
