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

class ConsoleLogger(ILogger):
    '''Writes log messages to the console.'''
    
    def __init__(self) -> None:
        raise NotImplementedError()
    
    def trace(self, message : str) -> None:
        '''Writes trace message to the console.
        Trace log messages provides generally useful information about application flow.
        
        :param message: The trace message.'''
        raise NotImplementedError()
    
    def warning(self, message : str) -> None:
        '''Writes warning message to the console.
        Warning log messages provides information about unexpected and recoverable event in application flow.
        
        :param message: The warning message.'''
        raise NotImplementedError()
    

class ILogger:
    '''Defines the methods that are used to perform logging.'''
    
    def trace(self, message : str) -> None:
        '''Writes trace log message;
        Trace log messages provides generally useful information about application flow.
        
        :param message: The trace message.'''
        raise NotImplementedError()
    
    def warning(self, message : str) -> None:
        '''Writes warning log message;
        Warning log messages provides information about unexpected and recoverable event in application flow.
        
        :param message: The warning message.'''
        raise NotImplementedError()
    

