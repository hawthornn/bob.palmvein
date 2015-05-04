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

import sys, os
import argparse

from facereclib.script.faceverify import parse_args, face_verify
from facereclib import utils

def main(command_line_parameters = sys.argv):
  """Executes the main function"""
  try:
    # do the command line parsing
    args = parse_args(command_line_parameters[1:], exclude_resources_from=['facereclib'])

    # perform face verification test
    face_verify(args, command_line_parameters)
  except Exception as e:
    # track any exceptions as error logs (i.e., to get a time stamp)
    utils.error("During the execution, an exception was raised: %s" % e)
    raise

if __name__ == "__main__":
  main()
