######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.15.3.1+obcheckpoint(0.1.9);ob(v1)                                                    #
# Generated on 2025-03-03T22:55:42.044155                                                            #
######################################################################################################

from __future__ import annotations



class AzureDefaultClientProvider(object, metaclass=type):
    @staticmethod
    def create_cacheable_azure_credential(*args, **kwargs):
        """
        azure.identity.DefaultAzureCredential is not readily cacheable in a dictionary
        because it does not have a content based hash and equality implementations.
        
        We implement a subclass CacheableDefaultAzureCredential to add them.
        
        We need this because credentials will be part of the cache key in _ClientCache.
        """
        ...
    ...

cached_provider_class: None

def create_cacheable_azure_credential():
    ...

