#!/usr/bin/env python

import xbob.db.verapalmroi
import facereclib

verapalm_directory = "/idiap/project/vera"

database = facereclib.databases.DatabaseXBob(
    database = xbob.db.verapalmroi.Database(),
    name = 'verapalmroi',
    original_directory = verapalm_directory,    
    original_extension = ".png",    
)
