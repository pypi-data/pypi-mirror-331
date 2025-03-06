from typing import List, Optional, Dict, Iterable, Any, overload
import io
import collections.abc
from collections.abc import Sequence
from datetime import datetime
from aspose.pyreflection import Type
import aspose.pycore
import aspose.pydrawing
from uuid import UUID
import groupdocs.merger
import groupdocs.merger.domain
import groupdocs.merger.domain.builders
import groupdocs.merger.domain.options
import groupdocs.merger.domain.result
import groupdocs.merger.exceptions
import groupdocs.merger.logging

class FileCorruptedException(GroupDocsMergerException):
    '''The exception that is thrown when specified file could not be loaded because it appears to be corrupted.'''
    

class FileTypeNotSupportedException:
    '''The exception that is thrown when specified file type is not supported.'''
    
    def __init__(self, message : str) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.exceptions.FileTypeNotSupportedException` class.
        
        :param message: The message that describes the error.'''
        raise NotImplementedError()
    

class GroupDocsMergerException:
    '''Represents errors that occur during document processing.'''
    
    def __init__(self, message : str) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.exceptions.GroupDocsMergerException` class.
        
        :param message: The message that describes the error.'''
        raise NotImplementedError()
    

class IncorrectPasswordException(GroupDocsMergerException):
    '''The exception that is thrown when specified password is incorrect.'''
    

class PasswordRequiredException(GroupDocsMergerException):
    '''The exception that is thrown when password is required to load the document.'''
    

