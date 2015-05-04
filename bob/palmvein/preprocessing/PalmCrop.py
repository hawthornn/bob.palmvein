#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: # Pedro Tome <Pedro.Tome@idiap.ch>
# @date: Wen Jun 18 14:21:42 CEST 2014
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

import bob.core
import bob.io.base
import bob.ip.base
import bob.ip.color
import bob.sp
import numpy
import math
from facereclib.preprocessing.Preprocessor import Preprocessor
from .. import utils
from PIL import Image
#import matplotlib.pyplot
import cv2
import scipy.ndimage
import time    

class PalmCrop (Preprocessor):
  """Palmvein segmentation:
      
    """

  def __init__(
      self,
      heq = True,
      padding_offset = 5,     #Always the same
      padding_threshold = 0,  
      roi = False,
      gpu = False,
      rotate = False,
      color_channel = 'gray',    # the color channel to extract from colored images, if colored images are in the database
      **kwargs                   # parameters to be written in the __str__ method
  ):
    """Parameters of the constructor of this preprocessor:

    color_channel
      In case of color images, which color channel should be used?
        
    """

    # call base class constructor
    Preprocessor.__init__(
        self,
        heq = heq,        
        padding_offset = padding_offset,    
        padding_threshold = padding_threshold,
        roi = roi,
        gpu = gpu,
        color_channel = color_channel,
        **kwargs
    )

    self.heq = heq
    self.padding_offset = padding_offset    
    self.padding_threshold = padding_threshold    
    self.roi = roi 
    self.gpu = gpu
    self.rotate = rotate
    self.color_channel = color_channel
      
    
  def __padding_palm__(self, image):
    
    image_new = bob.core.convert(image,numpy.float64,(0,1),(0,255))    
    
    img_h, img_w = image_new.shape
    
    padding_w = self.padding_threshold * numpy.ones((self.padding_offset, img_w))     
    # up and down    
    image_new = numpy.concatenate((padding_w,image_new),axis=0)
    image_new = numpy.concatenate((image_new,padding_w),axis=0)
        
    img_h, img_w = image_new.shape
    padding_h = self.padding_threshold * numpy.ones((img_h,self.padding_offset))        
    # left and right        
    image_new = numpy.concatenate((padding_h,image_new),axis=1)
    image_new = numpy.concatenate((image_new,padding_h),axis=1)
       
    return bob.core.convert(image_new,numpy.uint8,(0,255),(0,1))
  

  def __handsegmentation__(self, image):
    #For debugging    
    #import ipdb; ipdb.set_trace()    
   
    image_roi1 = image < 45
    #image_roi1_1 = image > 140
    
    #Removing spotlights 
    image_roi1_1 = image > 250
    image_roi1_1 = scipy.ndimage.binary_dilation(image_roi1_1, structure=numpy.ones((16,16))).astype(int)
    image_roi2 = image - 255 * image_roi1 - 255 * image_roi1_1
      
    #else:
    # image_roi2 = image - 255 * image_roi1 #- 255 * image_roi1_1
    
    image_roi3 = image_roi2 > 10
           
    # filter to smoothen hand contour: h = fspecial('average', [5,5])
    h = (1./25) * numpy.ones([5,5])
    #EXCLUDED HERE next for CASIA db
    #image_roi3 = utils.imfilter(image_roi3.astype(numpy.float64), h, self.gpu)
    
    #matplotlib.pyplot.imshow(image_roi3, cmap = matplotlib.cm.Greys_r)    
    #import ipdb; ipdb.set_trace()    
    #Selection of the hand region
    labeled_array, num_features = scipy.ndimage.label(image_roi3)
    
    sel = 1
    if (num_features > 1): 
      sel = numpy.argmax([len(numpy.argwhere(labeled_array==i)) for i in range(1,num_features+1)])+1
      
    ind = numpy.array([])
    ind = numpy.argwhere(labeled_array==sel)
            
    segmented_hand = numpy.zeros(labeled_array.shape)
    segmented_hand[ind[:,0],ind[:,1]] = 1
    
    #matplotlib.pyplot.imshow(segmented_hand, cmap = matplotlib.cm.Greys_r)    
    #import ipdb; ipdb.set_trace()    
    
    segmented_hand = scipy.ndimage.binary_fill_holes(segmented_hand).astype(int)
            
    # Apertura morfologica (usando como elemento estructurante un rectangulo de
    # 5x5 pixeles) para rellenar huecos y eliminar componentes muy peque�as
    # provienentes de la iluminaci�n o ruido del background
    segmented_hand = scipy.ndimage.binary_opening(segmented_hand, structure=numpy.ones((5,5))).astype(int)
    
    # Apertura seguida de cierre morfologico (usando como elemento estructurante un rectangulo de 
    # 8x1 pixeles y 4x1 pixeles, respectivamente) para rellenar huecos debidos a anillos o iluminaci�n no
    # constante (sobre todo en los pliegues entre dedos).
    segmented_hand = scipy.ndimage.binary_opening(segmented_hand, structure=numpy.ones((8,1))).astype(int)
    segmented_hand = scipy.ndimage.binary_closing(segmented_hand, structure=numpy.ones((16,1))).astype(int)
    
    #matplotlib.pyplot.figure(0)
    #matplotlib.pyplot.clf()
    #matplotlib.pyplot.imshow(segmented_hand, cmap = matplotlib.cm.Greys_r)
    #import ipdb; ipdb.set_trace()    

    return segmented_hand
   
  def __palmqualityextraction__(self, maximum_peaks, hand_landmarks):
    #For debugging    
    p_1 = hand_landmarks[0,:]
    p_2 = hand_landmarks[1,:]
    p_3 = hand_landmarks[2,:]

    # Checking the number of points (some times the thumb finger is missming in the image)
    if maximum_peaks.shape[0] == 5: 
        d_0 = maximum_peaks[0,:]
        d_1 = maximum_peaks[1,:]
        d_2 = maximum_peaks[2,:]
        d_3 = maximum_peaks[3,:]
        d_4 = maximum_peaks[4,:]

        #Angles of each inter-finger region (Theorem of the Cosaine c2 = b2 + a2 - 2ba cos(angle))
        a = numpy.linalg.norm(p_1-d_1) 
        b = numpy.linalg.norm(p_1-d_0) 
        c = numpy.linalg.norm(d_0-d_1) 
        alpha1 = math.degrees(math.acos( ((b**2+a**2)-c**2)/(2*a*b) ))

        #Angles of each inter-finger region (Theorem of the Cosaine c2 = b2 + a2 - 2ba cos(angle))
        a = numpy.linalg.norm(p_3-d_4) 
        b = numpy.linalg.norm(p_3-d_3) 
        c = numpy.linalg.norm(d_3-d_4) 
        alpha2 = math.degrees(math.acos( ((b**2+a**2)-c**2)/(2*a*b) ))        
        
        #Identification of left or right hand
        if (alpha1 > alpha2):
            h=0 # Left hand identifier
            #d_0 discarded
            d_1 = maximum_peaks[1,:]
            d_2 = maximum_peaks[2,:]
            d_3 = maximum_peaks[3,:]
            d_4 = maximum_peaks[4,:]
        else:
            h=1 # Right hand identifier
            #d_4 discarded
            d_1 = maximum_peaks[0,:]
            d_2 = maximum_peaks[1,:]
            d_3 = maximum_peaks[2,:]
            d_4 = maximum_peaks[3,:]
    else:
        ### Here is by default assigned left hand, maybe will be wrong with CASIA db it is OK
        h=0 # Left hand identifier
        d_1 = maximum_peaks[0,:]
        d_2 = maximum_peaks[1,:]
        d_3 = maximum_peaks[2,:]
        d_4 = maximum_peaks[3,:]
    

    #Area between fingers calculation based on determinants:
    q1 =  0.5 * abs( d_1[0]*p_1[1]*1 + d_1[1]*1*d_2[0] + p_1[0]*d_2[1]*1 - d_2[0]*p_1[1]*1 - p_1[0]*d_1[1]*1 - d_2[1]*1*d_1[0] )
    q2 =  0.5 * abs( d_2[0]*p_2[1]*1 + d_2[1]*1*d_3[0] + p_2[0]*d_3[1]*1 - d_3[0]*p_2[1]*1 - p_2[0]*d_2[1]*1 - d_3[1]*1*d_2[0] )
    q3 =  0.5 * abs( d_3[0]*p_3[1]*1 + d_3[1]*1*d_4[0] + p_3[0]*d_4[1]*1 - d_4[0]*p_3[1]*1 - p_3[0]*d_3[1]*1 - d_4[1]*1*d_3[0] )


    #Angles of each inter-finger region (Theorem of the Cosaine c2 = b2 + a2 - 2ba cos(angle))
    a = numpy.linalg.norm(p_1-d_2) 
    b = numpy.linalg.norm(p_1-d_1) 
    c = numpy.linalg.norm(d_1-d_2) 
    a1 = math.degrees(math.acos( ((b**2+a**2)-c**2)/(2*a*b) ))

    a = numpy.linalg.norm(p_2-d_3) 
    b = numpy.linalg.norm(p_2-d_2) 
    c = numpy.linalg.norm(d_2-d_3) 
    a2 = math.degrees(math.acos( ((b**2+a**2)-c**2)/(2*a*b) ))

    a = numpy.linalg.norm(p_3-d_4) 
    b = numpy.linalg.norm(p_3-d_3) 
    c = numpy.linalg.norm(d_3-d_4) 
    a3 = math.degrees(math.acos( ((b**2+a**2)-c**2)/(2*a*b) ))

    quality_value = numpy.array((h,q1,q2,q3,a1,a2,a3))
    
    return quality_value


  def __handlandmarksextraction__(self, image, segmented_hand):   
    
    mass_c = numpy.array(scipy.ndimage.center_of_mass(segmented_hand))
    massC_hand = numpy.array(mass_c) #Center of the hand
    mass_c[0] = mass_c[0] + 100 #Center of reference - close to the wrist of the hand    
    
    mass_c = scipy.flipud(mass_c)
    massC_hand = scipy.flipud(massC_hand)
                  
    # Upper part of the segmented hand image
    image_up = segmented_hand[0:mass_c[1],:]
    
    contours,hierarchy = cv2.findContours(image_up.astype(numpy.uint8),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    sel = numpy.argmax([len(i) for i in contours])
    ind = contours[sel]     
    
    mass_c[1] = mass_c[1] + 100     
    dist = numpy.zeros(ind.shape[0])
    dist = numpy.sum(numpy.abs(ind-mass_c)**2, axis=-1)**(1./2) #Idem to math.sqrt((ind[i,0]-mass_c[0])**2 + (ind[i,1]-mass_c[1])**2) or numpy.linalg.norm(ind[i,0]-mass_c)
    dist = dist[:,0]
    
    #Smoothing of a 1D signal to extract the minimum local peaks  
    dist = utils.smooth(dist)
    
    ### CHECK               
    #matplotlib.pyplot.figure(1)
    #matplotlib.pyplot.clf()
    #matplotlib.pyplot.plot(dist,'r')
    #minimum_peaks = utils.argrelmin(dist,axis=0, order=14)
    #for p in minimum_peaks:
    #  matplotlib.pyplot.plot(p,dist[p],'go')
    #matplotlib.pyplot.draw()    

    ### CHECK
    #matplotlib.pyplot.figure(2)
    #matplotlib.pyplot.clf()
    #matplotlib.pyplot.imshow(image, cmap = matplotlib.cm.Greys_r)
    #matplotlib.pyplot.plot(mass_c[0],mass_c[1],'ro')
    #matplotlib.pyplot.plot(massC_hand[0],massC_hand[1],'g*')
    ### CHECK
    
    minimum_peaks = ind[utils.argrelmin(dist,axis=0, order=14),0][0]    
    maximum_peaks = ind[utils.argrelmax(dist,axis=0, order=14, mode='wrap'),0][0]  #Mode='wrap' to include the first  

    #Organize the maximum_peaks based on the x coord  
    p_aux = numpy.take(maximum_peaks,numpy.where(maximum_peaks[:,1]!=0),0)[0]
    order = p_aux[:, 0].argsort()
    maximum_peaks = numpy.take(p_aux, order, 0)
    
    #Organize the minimum_peaks based on the y coord  
    p_aux = numpy.take(minimum_peaks,numpy.where(minimum_peaks[:,1]!=0),0)[0]
    order = minimum_peaks[:, 1].argsort()
    minimum_peaksALL = numpy.take(p_aux, order, 0)
    #Selection of the 3 last with highest y coord
    minimum_peaks = minimum_peaksALL[0:3]
    
    #Organize the minimum_peaks based on the x coord  
    p_aux = numpy.take(minimum_peaks,numpy.where(minimum_peaks[:,1]!=0),0)[0]
    order = p_aux[:, 0].argsort()
    minimum_peaks = numpy.take(p_aux, order, 0)

    ##Distance between the central hand landmarks and the other two
    dleft = numpy.linalg.norm(minimum_peaks[1]-minimum_peaks[0]) 
    dright = numpy.linalg.norm(minimum_peaks[1]-minimum_peaks[2]) 
    if dleft > 2 * (dright-10) or dright > 2 * (dleft-10):
        #Selection of the next with highest y coord and the first two
        minimum_peaks = minimum_peaksALL[0:4]
        minimum_peaks = numpy.take(minimum_peaks, [0,1,3], 0)

        #Again: Organize the minimum_peaks based on the x coord  
        p_aux = numpy.take(minimum_peaks,numpy.where(minimum_peaks[:,1]!=0),0)[0]
        order = p_aux[:, 0].argsort()
        minimum_peaks = numpy.take(p_aux, order, 0)
    
    hand_landmarks = minimum_peaks
    
    ## To obtain the quality of the segmentation based on areas and angles between fingers
    #quality_value = self.__palmqualityextraction__(maximum_peaks, minimum_peaks)
    
    ###    ### CHECK
    #for p in minimum_peaks: matplotlib.pyplot.plot(p[0],p[1],'ro')
    #for p in maximum_peaks: matplotlib.pyplot.plot(p[0],p[1],'yo')
    #matplotlib.pyplot.draw()
    #matplotlib.pyplot.plot(minimum_peaks[0][0],minimum_peaks[0][1],'bo')
    #matplotlib.pyplot.plot(minimum_peaks[1][0],minimum_peaks[1][1],'go')
    #for p in ind[:,0]: matplotlib.pyplot.plot(p[0],p[1],'r*')
    #radius = numpy.sum(numpy.abs(minimum_peaks[0]-massC_hand)**2, axis=-1)**(1./2)
    #circle=matplotlib.pyplot.Circle((massC_hand[0],massC_hand[1]), radius ,color='r',fill=False)
    #matplotlib.pyplot.figure(2).gca().add_artist(circle)
    #import ipdb; ipdb.set_trace()     
    ###    ### CHECK
   

    #import ipdb; ipdb.set_trace() 
    ###############################
    ### Hand landmarks comprobation
    ###############################
        

    ## Next comprobation is not necessary depending the palm region extraction
    #Comprobation    
    #Angles between the three selected hand landmarks (Theorem of the Cosaine c2 = b2 + a2 - 2ba cos(angle))
    #a = numpy.linalg.norm(hand_landmarks[0]-hand_landmarks[2]) 
    #b = numpy.linalg.norm(hand_landmarks[0]-hand_landmarks[1]) 
    #c = numpy.linalg.norm(hand_landmarks[1]-hand_landmarks[2]) 
    
    #angle_landmarks = math.acos( ((b**2+c**2)-a**2)/(2*b*c) )   
    #print math.degrees(angle_landmarks)   
    
    #if math.degrees(angle_landmarks) < 120:
    #  import ipdb; ipdb.set_trace()   
    #  print '......ERRORRRRRRRRRR'
    
    #return mass_c, hand_landmarks, quality_value
    return mass_c, hand_landmarks
  

  def __palmextraction1__(self, image, segmented_hand, ref_c, hand_landmarks):
    #For debugging    
    
    image_hand = image * segmented_hand
    
    p_1 = hand_landmarks[0,:]
    p_2 = hand_landmarks[1,:]
    p_3 = hand_landmarks[2,:]
    
    p_roi1 = p_1 + (p_1 - p_2) * 0.5
    p_roi2 = p_3 + (p_3 - p_2) * 0.5
    
    p_n = p_roi2.copy()
    p_n[1] = p_roi1[1]

    ### CHECK
    #matplotlib.pyplot.plot(p_roi1[0],p_roi1[1],'b*')
    #matplotlib.pyplot.plot(p_roi2[0],p_roi2[1],'b*')
    #matplotlib.pyplot.plot(p_n[0],p_n[1],'r*')
    ### CHECK    

    angle = math.atan( (numpy.linalg.norm(p_roi2-p_n)) / (numpy.linalg.norm(p_roi1-p_n)) )
    #Rotation in counterclockwise    
    if p_n[1] > p_roi2[1]:
      angle = -angle    
              
    l_roi = int(round(numpy.linalg.norm(p_roi1-p_roi2))) 
    
    geoNorm = bob.ip.base.GeomNorm(math.degrees(angle), 1, (l_roi, l_roi), (0, 0))
    palm_region = numpy.zeros((l_roi,l_roi))
    geoNorm(image_hand.astype(numpy.float), palm_region, (int(p_roi1[1]), int(p_roi1[0])))

    ### CHECK
    #matplotlib.pyplot.figure(3)
    #matplotlib.pyplot.clf()
    #matplotlib.pyplot.imshow(segmented_hand, cmap = matplotlib.cm.Greys_r)
    #matplotlib.pyplot.plot(p_roi1[0],p_roi1[1],'r*')
    #matplotlib.pyplot.plot(p_roi2[0],p_roi2[1],'r*')
    
    #Center of mass of the hand                   
    #mass_c_hand = numpy.array(scipy.ndimage.center_of_mass(segmented_hand))
    #mass_c_hand = scipy.flipud(mass_c_hand)                       
    #matplotlib.pyplot.plot(mass_c_hand[0],mass_c_hand[1],'ro')

    #matplotlib.pyplot.figure(4)
    #matplotlib.pyplot.clf()
    #matplotlib.pyplot.imshow(palm_region, cmap = matplotlib.cm.Greys_r)
    ### CHECK          

    return palm_region


  def __palmextraction2__(self, image, segmented_hand, ref_c, hand_landmarks):
    #For debugging    
    
    image_hand = image * segmented_hand
    
    p_1 = hand_landmarks[0,:]
    p_2 = hand_landmarks[1,:]
    p_3 = hand_landmarks[2,:]
    
    p_roi1 = p_1
    p_roi2 = p_3 
    
    p_n = p_roi2.copy()
    p_n[1] = p_roi1[1]

    ### CHECK
    #matplotlib.pyplot.plot(p_roi1[0],p_roi1[1],'b*')
    #matplotlib.pyplot.plot(p_roi2[0],p_roi2[1],'b*')
    #matplotlib.pyplot.plot(p_n[0],p_n[1],'r*')
    ### CHECK    

    angle = math.atan( (numpy.linalg.norm(p_roi2-p_n)) / (numpy.linalg.norm(p_roi1-p_n)) )
    #Rotation in counterclockwise    
    if p_n[1] > p_roi2[1]:
      angle = -angle    
              
    l_roi = int(round(numpy.linalg.norm(p_roi1-p_roi2))) 
        
    geoNorm = bob.ip.base.GeomNorm(math.degrees(angle), 1, (l_roi, l_roi), (-20, 0))
    palm_region = numpy.zeros((l_roi,l_roi))
    geoNorm(image_hand.astype(numpy.float), palm_region, (int(p_roi1[1]), int(p_roi1[0])))
    

    ### CHECK
    #matplotlib.pyplot.figure(3)
    #matplotlib.pyplot.clf()
    #matplotlib.pyplot.imshow(segmented_hand, cmap = matplotlib.cm.Greys_r)
    #matplotlib.pyplot.plot(p_roi1[0],p_roi1[1],'r*')
    #matplotlib.pyplot.plot(p_roi2[0],p_roi2[1],'r*')
    
    #Center of mass of the hand                   
    #mass_c_hand = numpy.array(scipy.ndimage.center_of_mass(segmented_hand))
    #mass_c_hand = scipy.flipud(mass_c_hand)                       
    #matplotlib.pyplot.plot(mass_c_hand[0],mass_c_hand[1],'ro')

    #matplotlib.pyplot.figure(4)
    #matplotlib.pyplot.clf()
    #matplotlib.pyplot.imshow(palm_region, cmap = matplotlib.cm.Greys_r)
    ### CHECK          

    return palm_region
    

  def __CLAHE__(self, image):
    """  Contrast-limited adaptive histogram equalization (CLAHE).
    """

    return true

  def __AHE__(self, image):
    #Umbralization based on the pixels non zero
    imageEnhance = bob.ip.base.histogram_equalization(image.astype(numpy.uint8))   

    return imageEnhance

  def __circularGabor__(self, image, bw, sigma):
    """ CIRCULARGABOR Construct a circular gabor filter
    Parameters:
        bw    = bandwidth, (1.12 octave)
        sigma = standard deviation, (5  pixels)
    """
    #Convert image to doubles        
    image_new = bob.core.convert(image,numpy.float64,(0,1),(0,255))    
    img_h, img_w = image_new.shape
    
    fc = (1/math.pi * math.sqrt(math.log(2)/2) * (2**bw+1)/(2**bw-1))/sigma

    sz = numpy.fix(8*numpy.max([sigma,sigma]))

    if numpy.mod(sz,2) == 0: 
      sz = sz+1
    # alternatively, use a fixed size
    # sz = 60;

    #Construct filter kernel
    winsize = numpy.fix(sz/2)
    
    x = numpy.arange(-winsize, winsize+1)
    y = numpy.arange(winsize, numpy.fix(-sz/2)-1, -1)
    X, Y = numpy.meshgrid(x, y)
    # X (right +)
    # Y (up +)

    gaborfilter = numpy.exp(-0.5*(X**2/sigma**2+Y**2/sigma**2))*numpy.cos(2*math.pi*fc*numpy.sqrt(X**2+Y**2))*(1/(2*math.pi*sigma))

    # Without normalisation
    #gaborfilter = numpy.exp(-0.5*(X**2/sigma**2+Y**2/sigma**2))*numpy.cos(2*math.pi*fc*numpy.sqrt(X**2+Y**2))
    
    imageEnhance = utils.imfilter(image, gaborfilter, self.gpu, conv=False)
    imageEnhance = numpy.abs(imageEnhance)
    
    return imageEnhance

  def __HFE__(self,image):
    """ High Frequency Enphasis Filtering (HFE)

    """
    ### Parameters
    D0 = 0.025
    a = 0.6
    b = 1.2
    n = 2.0
    
    #Convert image to doubles        
    image_new = bob.core.convert(image,numpy.float64,(0,1),(0,255))    
    img_h, img_w = image_new.shape
    
    # DFT
    Ffreq = bob.sp.fftshift(bob.sp.fft(image_new.astype(numpy.complex128))/math.sqrt(img_h*img_w))    
        
    row = numpy.arange(1,img_w+1)
    x = (numpy.tile(row,(img_h,1)) - (numpy.fix(img_w/2)+1)) /img_w
    col = numpy.arange(1,img_h+1)
    y =  (numpy.tile(col,(img_w,1)).T - (numpy.fix(img_h/2)+1))/img_h

    #D  is  the  distance  from  point  (u,v)  to  the  centre  of the frequency rectangle.
    radius = numpy.sqrt(x**2 + y**2)
    
    f = a + b / (1.0 + (D0 / radius)**(2*n))
    Ffreq = Ffreq * f
    #Inverse DFT
    imageEnhance = bob.sp.ifft(bob.sp.ifftshift(Ffreq))
    #Skip complex part
    imageEnhance = numpy.abs(imageEnhance)
    
    return imageEnhance
    

  def __palmnormalization__(self, palm_region, palm_size):
    #import ipdb; ipdb.set_trace()                       
    palm_region_norm = Image.fromarray(palm_region).resize((palm_size, palm_size), Image.ANTIALIAS) # best down-sizing filter        
    palm_region_norm = numpy.array(palm_region_norm, numpy.float64)
    #Some values can be negative, we solve it putting to zero
    palm_region_norm[palm_region_norm<0] = 0
    palm_region_norm[palm_region_norm>255] = 255

    #5) Palm region enhancement (adapthisteq-CLAHE, histeq-AHE, HFE, circularGabor)
    ###TODO
    #palm_region_norm = self.__CLAHE__(palm_region_norm) 
    #palm_region_norm = self.__AHE__(palm_region_norm) 
    #palm_region_norm = self.__HFE__(palm_region_norm) 
    #palm_region_norm = self.__circularGabor__(palm_region_norm, 1.12, 5) 
   
    #Kinds of normalization: 
    #im3 = im.resize((width, height), Image.NEAREST) # use nearest neighbour
    #im3 = im.resize((width, height), Image.BILINEAR) # linear interpolation in a 2x2 environment
    #im4 = im.resize((width, height), Image.BICUBIC) # cubic spline interpolation in a 4x4 environment
    #im5 = im.resize((width, height), Image.ANTIALIAS) # best down-sizing filter    
        
    #create a CLAHE object (Arguments are optional).
    #clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    #palm_region_norm = numpy.array(clahe.apply(Image.fromarray(palm_region_norm)))
        
    return palm_region_norm.astype(numpy.float64)    


  def crop_palm(self, image):
    #start = time.clock()
    
    #0) Image color conversion: RGB to Grayscale
    if image.shape[0] == 3:
      #image_hand = image_hand[0,:,:]
      gray_image = numpy.ndarray( image.shape[1:3], dtype = image.dtype)
      bob.ip.color.rgb_to_gray(image, gray_image)
      image_hand = gray_image
    else:
      if self.rotate == True:    
        image_hand = Image.fromarray(image)
        image_hand = image_hand.rotate(-90)

    #For final version write next and remove the else.
    #if self.rotate == True:    #IMPORTANT hand must to be frontal
    #  image_hand = Image.fromarray(image)
    #  image_hand = image_hand.rotate(-90)    

    image_hand = numpy.array(image_hand)   
    
    #0.A) Improvement - Rectangle cropping before 
    ### NOT NECESSARY FOR VERA database
    #offset = 50
    #rows, cols = image_hand.shape
    #image_hand_cropped = image_hand[offset:rows-offset,offset:cols-offset]
    
    #image_hand = image_hand_cropped
       
    if self.roi == False:
        #1) Padding array of black pixels to solve the problem of cutted fingers in the image
        image_hand = self.__padding_palm__(image_hand)
        
        #2) Hand region localization and segmentation
        segmented_hand = self.__handsegmentation__(image_hand)    
        
        #3) Hand landmarks localization and extraction
        #ref_c, hand_landmarks, quality_value = self.__handlandmarksextraction__(image_hand, segmented_hand)    
        ref_c, hand_landmarks = self.__handlandmarksextraction__(image_hand, segmented_hand)    
        
        #4) Palm region extraction based on hand landmarks
        #palm_region = self.__palmextraction1__(image_hand, segmented_hand, ref_c, hand_landmarks)    
        palm_region = self.__palmextraction2__(image_hand, segmented_hand, ref_c, hand_landmarks)    
    
    elif self.roi == True:
        palm_region = image_hand
        #quality_value = numpy.array((-1))
    
    #5) Palm region normalization on size
    palm_region_norm = self.__palmnormalization__(palm_region, 233) #200 CASIA, 300 VERA   
    

    ### CHECK
    #matplotlib.pyplot.clf()
    #matplotlib.pyplot.imshow(segmented_hand, cmap = matplotlib.cm.Greys_r)
    #for p in hand_landmarks:
    #  matplotlib.pyplot.plot(p[0],p[1],'go')  
    #matplotlib.pyplot.plot(ref_c[0],ref_c[1],'ro')
    #matplotlib.pyplot.draw()    
    
    #matplotlib.pyplot.figure(5)
    #matplotlib.pyplot.clf()
    #matplotlib.pyplot.imshow(palm_region_norm, cmap = matplotlib.cm.Greys_r)
        
    ##Check the time    
    #elapsed = (time.clock() - start)
    #print 'Time of CPU: ', elapsed
    
    #import ipdb; ipdb.set_trace()   
    return (image_hand, palm_region_norm)
    #return (image_hand, palm_region_norm, quality_value)
    

  def __call__(self, image, annotations=None):
    """Reads the input image, extract the Lee mask of the fingervein, and writes the resulting image"""
    return self.crop_palm(image)

  def save_data(self, image, image_file):
    f = bob.io.base.HDF5File(image_file, 'w')
    f.set('image', image[0])
    f.set('palm_region', image[1])
    #f.set('quality', image[2])
    
  def read_data(self, image_file):
    print image_file
    f = bob.io.base.HDF5File(image_file, 'r')
    image = f.read('image')
    palm_region = f.read('palm_region') 
    #quality = f.read('quality') 
    return (image, palm_region)
