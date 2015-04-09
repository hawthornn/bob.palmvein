#!/usr/bin/env python

import xbob.db.verapalmroiTS
import facereclib

verapalm_directory = "/idiap/project/vera"

database = facereclib.databases.DatabaseXBob(
    database = xbob.db.verapalmroiTS.Database(),
    name = 'verapalmroiTS',
    original_directory = verapalm_directory,    
    original_extension = ".png",    
)
