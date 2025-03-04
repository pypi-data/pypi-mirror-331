######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.15.3.1+obcheckpoint(0.1.9);ob(v1)                                                    #
# Generated on 2025-03-03T22:55:42.054878                                                            #
######################################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import metaflow.mf_extensions.obcheckpoint.plugins.machine_learning_utilities.datastructures

from ......metadata_provider.metadata import MetaDatum as MetaDatum
from ..datastructures import CheckpointArtifact as CheckpointArtifact
from .core import CheckpointReferenceResolver as CheckpointReferenceResolver

TYPE_CHECKING: bool

def checkpoint_load_related_metadata(checkpoint: metaflow.mf_extensions.obcheckpoint.plugins.machine_learning_utilities.datastructures.CheckpointArtifact, current_attempt):
    ...

def trace_lineage(flow, checkpoint: metaflow.mf_extensions.obcheckpoint.plugins.machine_learning_utilities.datastructures.CheckpointArtifact):
    """
    Trace the lineage of the checkpoint by tracing the previous paths.
    """
    ...

