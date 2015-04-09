#!/usr/bin/env python
# Pedro Tome <Pedro.Tome@idiap.ch>

import configurations
import tools
import preprocessing
import features
import tests
import script


def get_config():
  """Returns a string containing the configuration information.
  """

  import pkg_resources

  packages = pkg_resources.require(__name__)
  this = packages[0]
  deps = packages[1:]

  retval =  "%s: %s (%s)\n" % (this.key, this.version, this.location)
  retval += "  - python dependencies:\n"
  for d in deps: retval += "    - %s: %s (%s)\n" % (d.key, d.version, d.location)

  return retval.strip()


# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]