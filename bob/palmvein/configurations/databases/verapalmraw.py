#!/usr/bin/env python

import xbob.db.verapalm
import facereclib

verapalm_directory = "/idiap/project/vera"

database = facereclib.databases.DatabaseXBob(
    database = xbob.db.verapalm.Database(),
    name = 'verapalm',
    original_directory = verapalm_directory,
    original_extension = ".png",    
)
