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

"""This script generate the spoofing score for genuine scores of 
the experiment to compute the SFAR rate."""

import sys
import argparse
import numpy, math
import os
from facereclib import utils

def command_line_arguments(command_line_parameters):
  """Parse the program options"""

  # set up command line parser
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  
  parser.add_argument('-d', '--dev-file', required=True, help = "The score file of the Normal Operation Mode (NOM: real vs real images) of the system.")
  parser.add_argument('-s', '--spoofing-file', required=True, help = "The score file of the Spoofing Attack (SpoofingAttack: real vs spoofing images) of the system.")
  parser.add_argument('-o', '--output-file', required=False, help = "(Optional) The filename of the genuine spoofing score distribution to compute the SFAR, by default is save as --spoofing-file+_spoof.")

  utils.add_logger_command_line_option(parser)

  # parse arguments
  args = parser.parse_args(command_line_parameters)

  #import ipdb; ipdb.set_trace()

  utils.set_verbosity_level(args.verbose)

  # some sanity checks:
  #if len(args.dev_file) != len(args.spoofing_file):
  #  utils.error("The number of --dev-file (%d) and --spoofing-file (%d) are not identical!" % (len(args.dev_file), len(args.spoofing_file)))

  return args


def main(command_line_parameters=None):
  """Reads score files, computes the score file from spoofing genuine distribution."""
  
  args = command_line_arguments(command_line_parameters)
      
  #print 'Number of arguments:', len(sys.argv), 'arguments.'
  #print 'Argument List:', str(sys.argv)
  
  scoresFileNOM = args.dev_file
  scoresFileSpoof = args.spoofing_file
  scoresFileOut = args.output_file
  if scoresFileOut == None:
    scoresFileOut = scoresFileSpoof + '_spoof'
  
  #For debugging    
  #import ipdb; ipdb.set_trace()    
  
  with open(scoresFileSpoof, 'r') as fin, open(scoresFileOut, 'w') as fout:
    while True:
      tline = fin.readline()
      if not tline:
        break
      token1 = tline.find(' ')
      model = tline[0:token1]
      token2 = tline.find(' ',token1+1)
      mreal = tline[token1+1:token2] 
      token3 = tline.find(' ',token2+1)
      filemodel = tline[token2+1:token3] 
      score = tline[token3+1:]
    
      if ( model.find(mreal) == 0 ):
        newline = model + ' attack ' + tline[token2+1:]
        fout.write(newline)  
      
  with open(scoresFileNOM, 'r') as fin, open(scoresFileOut, 'a') as fout:
    while True:
      tline = fin.readline()
      if not tline:
        break
      token1 = tline.find(' ')
      model = tline[0:token1]
      token2 = tline.find(' ',token1+1)
      mreal = tline[token1+1:token2] 
      token3 = tline.find(' ',token2+1)
      filemodel = tline[token2+1:token3] 
      score = tline[token3+1:]
    
      if ( model.find(mreal) == 0 ):
        fout.write(tline)  
   
   
