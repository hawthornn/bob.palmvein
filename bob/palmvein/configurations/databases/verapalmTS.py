#!/usr/bin/env python

import xbob.db.verapalmTS
import facereclib

verapalm_directory = "/idiap/project/vera"

database = facereclib.databases.DatabaseXBob(
    database = xbob.db.verapalmTS.Database(),
    name = 'verapalmTS',
    original_directory = verapalm_directory,    
    original_extension = ".png",    
)
