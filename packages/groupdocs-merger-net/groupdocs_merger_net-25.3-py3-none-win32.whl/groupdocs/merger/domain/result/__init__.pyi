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

class DocumentInfo(IDocumentInfo):
    '''Defines document description properties.'''
    
    def __init__(self, file_type : groupdocs.merger.domain.FileType, pages : List[groupdocs.merger.domain.result.IPageInfo], size : int) -> None:
        '''Initializes new instance of :py:class:`groupdocs.merger.domain.result.DocumentInfo` class.
        
        :param file_type: The type of the file.
        :param pages: The list of pages to view.
        :param size: The size of the file.'''
        raise NotImplementedError()
    
    @property
    def type(self) -> groupdocs.merger.domain.FileType:
        '''Gets the file type.'''
        raise NotImplementedError()
    
    @property
    def pages(self) -> List[groupdocs.merger.domain.result.IPageInfo]:
        '''Defines document pages collection.'''
        raise NotImplementedError()
    
    @property
    def page_count(self) -> int:
        '''The document pages count.'''
        raise NotImplementedError()
    
    @property
    def size(self) -> int:
        '''Document size in bytes'''
        raise NotImplementedError()
    

class IDocumentInfo:
    '''Interface for the document description properties.'''
    
    @property
    def type(self) -> groupdocs.merger.domain.FileType:
        '''Gets the file type.'''
        raise NotImplementedError()
    
    @property
    def pages(self) -> List[groupdocs.merger.domain.result.IPageInfo]:
        '''Defines document pages collection.'''
        raise NotImplementedError()
    
    @property
    def page_count(self) -> int:
        '''The document pages count.'''
        raise NotImplementedError()
    
    @property
    def size(self) -> int:
        '''Document size in bytes.'''
        raise NotImplementedError()
    

class IPageInfo:
    '''Interface for the page description properties.'''
    
    @property
    def document(self) -> groupdocs.merger.domain.result.DocumentInfo:
        '''Gets the document info.'''
        raise NotImplementedError()
    
    @document.setter
    def document(self, value : groupdocs.merger.domain.result.DocumentInfo) -> None:
        '''Gets the document info.'''
        raise NotImplementedError()
    
    @property
    def number(self) -> int:
        '''Gets the page number.'''
        raise NotImplementedError()
    
    @property
    def visible(self) -> bool:
        '''Indicates whether page is visibile or not.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> int:
        '''Gets page width in pixels when converted to image.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        '''Gets page height in pixels when converted to image.'''
        raise NotImplementedError()
    

class PageInfo(IPageInfo):
    '''Defines page description properties.'''
    
    @overload
    def __init__(self, number : int, visible : bool) -> None:
        '''Initializes new instance of :py:class:`groupdocs.merger.domain.result.PageInfo` class.
        
        :param number: The page number.
        :param visible: The page visibility indicator.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, number : int, visible : bool, width : int, height : int) -> None:
        '''Initializes new instance of :py:class:`groupdocs.merger.domain.result.PageInfo` class.
        
        :param number: The page number.
        :param visible: The page visibility indicator.
        :param width: The width of the page in pixels when viewing as JPG or PNG.
        :param height: The height of the page in pixels when viewing as JPG or PNG.'''
        raise NotImplementedError()
    
    @property
    def document(self) -> groupdocs.merger.domain.result.DocumentInfo:
        '''Gets the document info.'''
        raise NotImplementedError()
    
    @document.setter
    def document(self, value : groupdocs.merger.domain.result.DocumentInfo) -> None:
        '''Gets the document info.'''
        raise NotImplementedError()
    
    @property
    def number(self) -> int:
        '''Gets the page number.'''
        raise NotImplementedError()
    
    @property
    def visible(self) -> bool:
        '''Indicates whether page is visibile or not.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> int:
        '''Gets page width in pixels when converted to image.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        '''Gets page height in pixels when converted to image.'''
        raise NotImplementedError()
    

