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

import numpy.random
import scipy.ndimage
import scipy.signal
import bob.ip.base
import bob.sp
import bob.core

def imfilter(a, b, gpu=False, conv=True):
  """imfilter function based on MATLAB implementation."""
  if (a.dtype == numpy.uint8):
      #a = a.astype(numpy.float64)
      a= bob.core.convert(a,numpy.float64,(0,1))    
  M, N = a.shape
  if conv == True:
      b = bob.ip.base.rotate(b, 180)    
  shape = numpy.array((0,0))
  shape[0] = a.shape[0] + b.shape[0] - 1
  shape[1] = a.shape[1] + b.shape[1] - 1
  a_ext = numpy.ndarray(shape=shape, dtype=numpy.float64)
  bob.sp.extrapolate_nearest(a, a_ext)
  
  if gpu == True:
    import xbob.cusp
    return xbob.cusp.conv(a_ext, b)
    
  else:
    return scipy.signal.convolve2d(a_ext, b, 'valid')
    #return scipy.signal.convolve2d(a_ext, br, 'valid')
    #return = self.convfft(a_ext, b)


def smooth(x,window_len=11,window='hanning'):
    """smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
        
    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)
    
    see also: 
    
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"


    s=numpy.r_[x[window_len/2-1:0:-1],x,x[-1:-window_len/2:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=numpy.ones(window_len,'d')
    else:
        w=eval('numpy.'+window+'(window_len)')

    #import ipdb; ipdb.set_trace()  
    y=numpy.convolve(w/w.sum(),s,mode='valid')
    return y

def _boolrelextrema(data, comparator,
                  axis=0, order=1, mode='clip'):
    """
Calculate the relative extrema of `data`.

Relative extrema are calculated by finding locations where
``comparator(data[n], data[n+1:n+order+1])`` is True.

Parameters
----------
data : ndarray
Array in which to find the relative extrema.
comparator : callable
Function to use to compare two data points.
Should take 2 numbers as arguments.
axis : int, optional
Axis over which to select from `data`. Default is 0.
order : int, optional
How many points on each side to use for the comparison
to consider ``comparator(n,n+x)`` to be True.
mode : str, optional
How the edges of the vector are treated. 'wrap' (wrap around) or
'clip' (treat overflow as the same as the last (or first) element).
Default 'clip'. See numpy.take

Returns
-------
extrema : ndarray
Boolean array of the same shape as `data` that is True at an extrema,
False otherwise.

See also
--------
argrelmax, argrelmin

Examples
--------
>>> testdata = numpy.array([1,2,3,2,1])
>>> _boolrelextrema(testdata, numpy.greater, axis=0)
array([False, False, True, False, False], dtype=bool)

"""
    if((int(order) != order) or (order < 1)):
        raise ValueError('Order must be an int >= 1')

    datalen = data.shape[axis]
    locs = numpy.arange(0, datalen)
    
    results = numpy.ones(data.shape, dtype=bool)
    main = data.take(locs, axis=axis, mode=mode)
    for shift in xrange(1, order + 1):
        plus = data.take(locs + shift, axis=axis, mode=mode)
        minus = data.take(locs - shift, axis=axis, mode=mode)
        results &= comparator(main, plus)
        results &= comparator(main, minus)
        if(~results.any()):
            return results
    return results


def argrelmin(data, axis=0, order=1, mode='clip'):
    """
Calculate the relative minima of `data`.

.. versionadded:: 0.11.0

Parameters
----------
  data : ndarray
    Array in which to find the relative minima.
  axis : int, optional
    Axis over which to select from `data`. Default is 0.
  order : int, optional
    How many points on each side to use for the comparison
    to consider ``comparator(n, n+x)`` to be True.
  mode : str, optional
    How the edges of the vector are treated.
    Available options are 'wrap' (wrap around) or 'clip' (treat overflow
    as the same as the last (or first) element).
Default 'clip'. See numpy.take

Returns
-------
extrema : tuple of ndarrays
Indices of the minima in arrays of integers. ``extrema[k]`` is
the array of indices of axis `k` of `data`. Note that the
return value is a tuple even when `data` is one-dimensional.

See Also
--------
argrelextrema, argrelmax

Notes
-----
This function uses `argrelextrema` with numpy.less as comparator.

Examples
--------
>>> x = numpy.array([2, 1, 2, 3, 2, 0, 1, 0])
>>> argrelmin(x)
(array([1, 5]),)
>>> y = numpy.array([[1, 2, 1, 2],
... [2, 2, 0, 0],
... [5, 3, 4, 4]])
...
>>> argrelmin(y, axis=1)
(array([0, 2]), array([2, 1]))

"""
    return argrelextrema(data, numpy.less, axis, order, mode)


def argrelmax(data, axis=0, order=1, mode='clip'):
    """
Calculate the relative maxima of `data`.

.. versionadded:: 0.11.0

Parameters
----------
data : ndarray
Array in which to find the relative maxima.
axis : int, optional
Axis over which to select from `data`. Default is 0.
order : int, optional
How many points on each side to use for the comparison
to consider ``comparator(n, n+x)`` to be True.
mode : str, optional
How the edges of the vector are treated.
Available options are 'wrap' (wrap around) or 'clip' (treat overflow
as the same as the last (or first) element).
Default 'clip'. See `numpy.take`.

Returns
-------
extrema : tuple of ndarrays
Indices of the maxima in arrays of integers. ``extrema[k]`` is
the array of indices of axis `k` of `data`. Note that the
return value is a tuple even when `data` is one-dimensional.

See Also
--------
argrelextrema, argrelmin

Notes
-----
This function uses `argrelextrema` with numpy.greater as comparator.

Examples
--------
>>> x = numpy.array([2, 1, 2, 3, 2, 0, 1, 0])
>>> argrelmax(x)
(array([3, 6]),)
>>> y = numpy.array([[1, 2, 1, 2],
... [2, 2, 0, 0],
... [5, 3, 4, 4]])
...
>>> argrelmax(y, axis=1)
(array([0]), array([1]))
"""
    return argrelextrema(data, numpy.greater, axis, order, mode)


def argrelextrema(data, comparator, axis=0, order=1, mode='clip'):
    """
Calculate the relative extrema of `data`.

.. versionadded:: 0.11.0

Parameters
----------
data : ndarray
Array in which to find the relative extrema.
comparator : callable
Function to use to compare two data points.
Should take 2 numbers as arguments.
axis : int, optional
Axis over which to select from `data`. Default is 0.
order : int, optional
How many points on each side to use for the comparison
to consider ``comparator(n, n+x)`` to be True.
mode : str, optional
How the edges of the vector are treated. 'wrap' (wrap around) or
'clip' (treat overflow as the same as the last (or first) element).
Default is 'clip'. See `numpy.take`.

Returns
-------
extrema : tuple of ndarrays
Indices of the maxima in arrays of integers. ``extrema[k]`` is
the array of indices of axis `k` of `data`. Note that the
return value is a tuple even when `data` is one-dimensional.

See Also
--------
argrelmin, argrelmax

Examples
--------
>>> x = numpy.array([2, 1, 2, 3, 2, 0, 1, 0])
>>> argrelextrema(x, numpy.greater)
(array([3, 6]),)
>>> y = numpy.array([[1, 2, 1, 2],
... [2, 2, 0, 0],
... [5, 3, 4, 4]])
...
>>> argrelextrema(y, numpy.less, axis=1)
(array([0, 2]), array([2, 1]))

"""
    results = _boolrelextrema(data, comparator,
                              axis, order, mode)
    return numpy.where(results)