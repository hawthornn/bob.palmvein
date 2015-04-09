#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Pedro Tome <Pedro.Tome@idiap.ch>

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
