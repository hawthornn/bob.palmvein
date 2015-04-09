#!/usr/bin/env python

import bob.db.verapalm
import facereclib

verapalm_directory = "/idiap/project/vera"

database = facereclib.databases.DatabaseBob(
    database = bob.db.verapalm.Database(
      original_directory = verapalm_directory,
      original_extension = ".png",    
    ),
    name = 'verapalm',
    
)
