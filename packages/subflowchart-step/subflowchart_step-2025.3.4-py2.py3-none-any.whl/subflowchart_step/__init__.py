# -*- coding: utf-8 -*-

"""
subflowchart_step
A SEAMM plug-in for subflowcharts
"""

# Bring up the classes so that they appear to be directly in
# the subflowchart_step package.

from .subflowchart import Subflowchart  # noqa: F401, E501
from .subflowchart_step import SubflowchartStep  # noqa: F401, E501
from .tk_subflowchart import TkSubflowchart  # noqa: F401, E501

# Handle versioneer
from ._version import get_versions

__author__ = "Paul Saxe"
__email__ = "psaxe@molssi.org"
versions = get_versions()
__version__ = versions["version"]
__git_revision__ = versions["full-revisionid"]
del get_versions, versions
