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

import bob.sp
import bob.ip.base

import numpy
import math
import scipy.signal

from facereclib.tools.Tool import Tool

class MiuraMatch (Tool):
  """Finger vein matching: match ratio based on
     N. Miura, A. Nagasaka, and T. Miyatake. Feature extraction of finger vein patterns based on repeated line tracking and its application 
     to personal identification. Machine Vision and Applications, Vol. 15, Num. 4, pp. 194--203, 2004
  """

  def __init__(
      self,
      # some similarity functions might need a GaborWaveletTransform class, so we have to provide the parameters here as well...
      ch = 8,       # Maximum search displacement in y-direction
      cw = 5,       # Maximum search displacement in x-direction
      gpu = False,
  ):

    # call base class constructor
    Tool.__init__(
        self,

        ch = ch,
        cw = cw,

        multiple_model_scoring = None,
        multiple_probe_scoring = None
    )

    self.ch = ch
    self.cw = cw
    self.gpu = gpu

  def enroll(self, enroll_features):
    """Enrolls the model by computing an average graph for each model"""
    # return the generated model
    #import ipdb; ipdb.set_trace()
    return numpy.array(enroll_features)


  def convfft(self, t, a):
    # Determine padding size in x and y dimension
    size_t  = numpy.array(t.shape)
    size_a  = numpy.array(a.shape)
    outsize = size_t + size_a - 1
    
    # Determine 2D cross correlation in Fourier domain
    taux = numpy.zeros(outsize)
    taux[0:size_t[0],0:size_t[1]] = t
    Ft = bob.sp.fft(taux.astype(numpy.complex128))
    aaux = numpy.zeros(outsize)
    aaux[0:size_a[0],0:size_a[1]] = a
    Fa = bob.sp.fft(aaux.astype(numpy.complex128))
    
    convta = numpy.real(bob.sp.ifft(Ft*Fa))
    
    [w, h] = size_t-size_a+1
    output = convta[size_a[0]-1:size_a[0]-1+w, size_a[1]-1:size_a[1]-1+h]
        
    return output


  def score(self, model, probe):
    """Computes the score of the probe and the model
         Return score - Value between 0 and 0.5, larger value is better match
    """
    #print model.shape
    #print probe.shape
    
    I=probe.astype(numpy.float64)
    
    if len(model.shape) == 2: 
      model = numpy.array([model])
    
    n_models = model.shape[0]

    scores = []
    for i in range(n_models):
      R=model[i,:].astype(numpy.float64)
      h, w = R.shape
      crop_R = R[self.ch:h-self.ch, self.cw:w-self.cw]
      rotate_R = numpy.zeros((crop_R.shape[0], crop_R.shape[1]))
      bob.ip.base.rotate(crop_R, rotate_R, 180)
      #FFT for scoring!   
      #Nm=bob.sp.ifft(bob.sp.fft(I)*bob.sp.fft(rotate_R))
      if self.gpu == True:
          Nm = self.convfft(I, rotate_R)
          #import xbob.cusp
          #Nm = xbob.cusp.conv(I, rotate_R);
      else:
          Nm = self.convfft(I, rotate_R)
          #Nm2 = scipy.signal.convolve2d(I, rotate_R, 'valid')
          
      t0, s0 = numpy.unravel_index(Nm.argmax(), Nm.shape)
      Nmm = Nm[t0,s0]
      #Nmm = Nm.max()
      #mi = numpy.argwhere(Nmm == Nm) 
      #t0, s0 = mi.flatten()[:2]
      scores.append(Nmm/(sum(sum(crop_R)) + sum(sum(I[t0:t0+h-2*self.ch, s0:s0+w-2*self.cw]))))
        
    return numpy.mean(scores)
    
