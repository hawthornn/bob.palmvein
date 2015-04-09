#!/usr/bin/env python

import bob.db.casiapalm
import facereclib

casiapalm_directory = "/idiap/project/vera/"

database = facereclib.databases.DatabaseBob(
    database = bob.db.casiapalm.Database(
      original_directory = casiapalm_directory,
      original_extension = ".jpg"
    ),
    name = 'casiapalm',
    
)
