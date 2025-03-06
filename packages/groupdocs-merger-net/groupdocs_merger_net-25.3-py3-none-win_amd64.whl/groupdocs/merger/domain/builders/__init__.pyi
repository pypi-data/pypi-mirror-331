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

class PageBuilder:
    '''PageInfo builder for getting the page collection from the documents.'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.builders.PageBuilder` class.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, options : groupdocs.merger.domain.options.PageBuilderOptions) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.builders.PageBuilder` class.
        
        :param options: The page builder options.'''
        raise NotImplementedError()
    
    @overload
    def add_page(self, document_index : int, page_number : int) -> None:
        '''Add page to the page collection.
        
        :param document_index: DocumentInfo index.
        :param page_number: PageInfo number.'''
        raise NotImplementedError()
    
    @overload
    def add_page(self, page : groupdocs.merger.domain.result.IPageInfo) -> None:
        '''Add page to the page collection.
        
        :param page: PageInfo instance.'''
        raise NotImplementedError()
    
    def add_page_range(self, pages : List[groupdocs.merger.domain.result.IPageInfo]) -> None:
        '''Add pages to the page collection.
        
        :param pages: Pages array.'''
        raise NotImplementedError()
    
    def clear(self) -> None:
        '''Clear the internal collections.'''
        raise NotImplementedError()
    
    @property
    def options(self) -> groupdocs.merger.domain.options.PageBuilderOptions:
        '''The page builder options.'''
        raise NotImplementedError()
    
    @property
    def pages(self) -> Sequence[groupdocs.merger.domain.result.PageInfo]:
        '''The page collection.'''
        raise NotImplementedError()
    

