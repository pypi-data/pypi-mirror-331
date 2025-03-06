######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.15.4                                                                                 #
# Generated on 2025-03-05T12:14:55.370781                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.plugins.pypi.conda_environment

from .conda_environment import CondaEnvironment as CondaEnvironment

class PyPIEnvironment(metaflow.plugins.pypi.conda_environment.CondaEnvironment, metaclass=type):
    ...

