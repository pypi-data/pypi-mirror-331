
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

class IMerger:
    '''Interface for the main class that controls the document merging process.'''
    
    @overload
    def join(self, document : io._IOBase) -> groupdocs.merger.IMerger:
        '''Joins the documents into one single document.'''
        raise NotImplementedError()
    
    @overload
    def join(self, document : io._IOBase, join_options : groupdocs.merger.domain.options.IJoinOptions) -> groupdocs.merger.IMerger:
        '''Joins the documents into one single document.'''
        raise NotImplementedError()
    
    @overload
    def join(self, document : io._IOBase, join_options : groupdocs.merger.domain.options.IPageJoinOptions) -> groupdocs.merger.IMerger:
        '''Joins the documents into one single document.'''
        raise NotImplementedError()
    
    @overload
    def join(self, document : io._IOBase, join_options : groupdocs.merger.domain.options.IImageJoinOptions) -> groupdocs.merger.IMerger:
        '''Joins the documents into one single document.'''
        raise NotImplementedError()
    
    @overload
    def join(self, file_path : str) -> groupdocs.merger.IMerger:
        '''Joins the documents into one single document.'''
        raise NotImplementedError()
    
    @overload
    def join(self, file_path : str, join_options : groupdocs.merger.domain.options.IImageJoinOptions) -> groupdocs.merger.IMerger:
        '''Joins the documents into one single document.'''
        raise NotImplementedError()
    
    @overload
    def join(self, file_path : str, join_options : groupdocs.merger.domain.options.IJoinOptions) -> groupdocs.merger.IMerger:
        '''Joins the documents into one single document.'''
        raise NotImplementedError()
    
    @overload
    def join(self, file_path : str, join_options : groupdocs.merger.domain.options.IPageJoinOptions) -> groupdocs.merger.IMerger:
        '''Joins the documents into one single document.'''
        raise NotImplementedError()
    
    @overload
    def split(self, split_options : groupdocs.merger.domain.options.ISplitOptions) -> groupdocs.merger.IMerger:
        '''Splits the single document to the multiple documents.'''
        raise NotImplementedError()
    
    @overload
    def split(self, split_options : groupdocs.merger.domain.options.ITextSplitOptions) -> groupdocs.merger.IMerger:
        '''Splits the single document to the multiple documents.'''
        raise NotImplementedError()
    
    @overload
    def save(self, document : io._IOBase) -> groupdocs.merger.IMerger:
        '''Saves the result document to the stream ``document``.'''
        raise NotImplementedError()
    
    @overload
    def save(self, file_path : str) -> groupdocs.merger.IMerger:
        '''Saves the result document file to ``filePath``.'''
        raise NotImplementedError()
    
    @overload
    def save(self, file_path : str, use_default_directory : bool) -> groupdocs.merger.IMerger:
        '''Saves the result document file to ``filePath``.'''
        raise NotImplementedError()
    
    def add_password(self, add_password_options : groupdocs.merger.domain.options.IAddPasswordOptions) -> groupdocs.merger.IMerger:
        '''Protects document with password.'''
        raise NotImplementedError()
    
    def update_password(self, update_password_options : groupdocs.merger.domain.options.IUpdatePasswordOptions) -> groupdocs.merger.IMerger:
        '''Updates existing password for document.'''
        raise NotImplementedError()
    
    def remove_password(self) -> groupdocs.merger.IMerger:
        '''Removes password from document.'''
        raise NotImplementedError()
    
    def import_document(self, import_document_options : groupdocs.merger.domain.options.IImportDocumentOptions) -> groupdocs.merger.IMerger:
        '''Imports the document as attachment or embedded via Ole.'''
        raise NotImplementedError()
    
    def extract_pages(self, extract_options : groupdocs.merger.domain.options.IExtractOptions) -> groupdocs.merger.IMerger:
        '''Makes a new document with some pages from the source document.'''
        raise NotImplementedError()
    
    def change_orientation(self, orientation_options : groupdocs.merger.domain.options.IOrientationOptions) -> groupdocs.merger.IMerger:
        '''Applies a new orientation mode for the specified pages.'''
        raise NotImplementedError()
    
    def move_page(self, move_options : groupdocs.merger.domain.options.IMoveOptions) -> groupdocs.merger.IMerger:
        '''Moves page to a new position within document of known format.'''
        raise NotImplementedError()
    
    def remove_pages(self, remove_options : groupdocs.merger.domain.options.IRemoveOptions) -> groupdocs.merger.IMerger:
        '''Removes pages from document of known format.'''
        raise NotImplementedError()
    
    def rotate_pages(self, rotate_options : groupdocs.merger.domain.options.IRotateOptions) -> groupdocs.merger.IMerger:
        '''Rotate pages of the document.'''
        raise NotImplementedError()
    
    def swap_pages(self, swap_options : groupdocs.merger.domain.options.ISwapOptions) -> groupdocs.merger.IMerger:
        '''Swaps two pages within document of known format.'''
        raise NotImplementedError()
    

class License:
    '''Provides methods to license the component. Learn more about licensing `here <https://purchase.groupdocs.com/faqs/licensing>`.'''
    
    def __init__(self) -> None:
        raise NotImplementedError()
    
    @overload
    def set_license(self, license_stream : io._IOBase) -> None:
        '''Licenses the component.
        
        :param license_stream: The license stream.'''
        raise NotImplementedError()
    
    @overload
    def set_license(self, license_path : str) -> None:
        '''Licenses the component.
        
        :param license_path: The license path.'''
        raise NotImplementedError()
    

class Merger(IMerger):
    '''Represents the main class that controls the document merging process.'''
    
    @overload
    def __init__(self, document : io._IOBase) -> None:
        '''Initializes new instance of :py:class:`groupdocs.merger.Merger` class.
        
        :param document: The readable stream.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, document : io._IOBase, load_options : groupdocs.merger.domain.options.ILoadOptions) -> None:
        '''Initializes new instance of :py:class:`groupdocs.merger.Merger` class.
        
        :param document: The readable stream.
        :param load_options: The document load options.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, document : io._IOBase, settings : groupdocs.merger.MergerSettings) -> None:
        '''Initializes new instance of :py:class:`groupdocs.merger.Merger` class.
        
        :param document: The readable stream.
        :param settings: The Merger settings.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, document : io._IOBase, load_options : groupdocs.merger.domain.options.ILoadOptions, settings : groupdocs.merger.MergerSettings) -> None:
        '''Initializes new instance of :py:class:`groupdocs.merger.Merger` class.
        
        :param document: The readable stream.
        :param load_options: The document load options.
        :param settings: The Merger settings.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_path : str) -> None:
        '''Initializes new instance of :py:class:`groupdocs.merger.Merger` class.
        
        :param file_path: The file path.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_path : str, load_options : groupdocs.merger.domain.options.ILoadOptions) -> None:
        '''Initializes new instance of :py:class:`groupdocs.merger.Merger` class.
        
        :param file_path: The file path.
        :param load_options: The document load options.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_path : str, settings : groupdocs.merger.MergerSettings) -> None:
        '''Initializes new instance of :py:class:`groupdocs.merger.Merger` class.
        
        :param file_path: The file path.
        :param settings: The Merger settings.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_path : str, load_options : groupdocs.merger.domain.options.ILoadOptions, settings : groupdocs.merger.MergerSettings) -> None:
        '''Initializes new instance of :py:class:`groupdocs.merger.Merger` class.
        
        :param file_path: The file path.
        :param load_options: The document load options.
        :param settings: The Merger settings.'''
        raise NotImplementedError()
    
    @overload
    def join(self, document : io._IOBase) -> groupdocs.merger.IMerger:
        '''Joins the documents into one single document.
        
        :param document: Joined document.'''
        raise NotImplementedError()
    
    @overload
    def join(self, document : io._IOBase, join_options : groupdocs.merger.domain.options.IJoinOptions) -> groupdocs.merger.IMerger:
        '''Joins the documents into one single document.
        
        :param document: Joined document.
        :param join_options: The join options.'''
        raise NotImplementedError()
    
    @overload
    def join(self, document : io._IOBase, join_options : groupdocs.merger.domain.options.IPageJoinOptions) -> groupdocs.merger.IMerger:
        '''Joins the documents into one single document.
        
        :param document: Joined document.
        :param join_options: The join options.'''
        raise NotImplementedError()
    
    @overload
    def join(self, document : io._IOBase, join_options : groupdocs.merger.domain.options.IImageJoinOptions) -> groupdocs.merger.IMerger:
        '''Joins the documents into one single document.
        
        :param document: Joined document.
        :param join_options: The image join options.'''
        raise NotImplementedError()
    
    @overload
    def join(self, file_path : str) -> groupdocs.merger.IMerger:
        '''Joins the documents into one single document.
        
        :param file_path: File path of the joined document.'''
        raise NotImplementedError()
    
    @overload
    def join(self, file_path : str, join_options : groupdocs.merger.domain.options.IJoinOptions) -> groupdocs.merger.IMerger:
        '''Joins the documents into one single document.
        
        :param file_path: File path of the joined document.
        :param join_options: The join options.'''
        raise NotImplementedError()
    
    @overload
    def join(self, file_path : str, join_options : groupdocs.merger.domain.options.IPageJoinOptions) -> groupdocs.merger.IMerger:
        '''Joins the documents into one single document.
        
        :param file_path: File path of the joined document.
        :param join_options: The join options.'''
        raise NotImplementedError()
    
    @overload
    def join(self, file_path : str, join_options : groupdocs.merger.domain.options.IImageJoinOptions) -> groupdocs.merger.IMerger:
        '''Joins the documents into one single document.
        
        :param file_path: File path of the joined document.
        :param join_options: The image join options.'''
        raise NotImplementedError()
    
    @overload
    def split(self, split_options : groupdocs.merger.domain.options.ISplitOptions) -> groupdocs.merger.IMerger:
        '''Splits the single document to the multiple documents.
        
        :param split_options: The page split options.'''
        raise NotImplementedError()
    
    @overload
    def split(self, split_options : groupdocs.merger.domain.options.ITextSplitOptions) -> groupdocs.merger.IMerger:
        '''Splits the single document to the multiple documents.
        
        :param split_options: The text split options.'''
        raise NotImplementedError()
    
    @overload
    def save(self, document : io._IOBase) -> groupdocs.merger.IMerger:
        '''Saves the result document to the stream ``document``.
        
        :param document: The document stream.'''
        raise NotImplementedError()
    
    @overload
    def save(self, file_path : str) -> groupdocs.merger.IMerger:
        '''Saves the result document file to ``filePath``.
        
        :param file_path: The file name or full file path.'''
        raise NotImplementedError()
    
    @overload
    def save(self, file_path : str, use_default_directory : bool) -> groupdocs.merger.IMerger:
        '''Saves the result document file to ``filePath``.
        
        :param file_path: The file path or name in case of default directory usage.
        :param use_default_directory: Use the default directory from settings.'''
        raise NotImplementedError()
    
    def import_document(self, import_document_options : groupdocs.merger.domain.options.IImportDocumentOptions) -> groupdocs.merger.IMerger:
        '''Imports the document as attachment or embedded via Ole.
        
        :param import_document_options: The embedded document import options.'''
        raise NotImplementedError()
    
    def create_page_builder(self, page_builder_options : groupdocs.merger.domain.options.PageBuilderOptions) -> groupdocs.merger.domain.builders.PageBuilder:
        '''Creates a new Page builder with predefined document collection.
        
        :returns: The created page builder.'''
        raise NotImplementedError()
    
    def apply_page_builder(self, page_builder : groupdocs.merger.domain.builders.PageBuilder) -> None:
        '''Applies page builder changes.
        
        :param page_builder: The page builder.'''
        raise NotImplementedError()
    
    def extract_pages(self, extract_options : groupdocs.merger.domain.options.IExtractOptions) -> groupdocs.merger.IMerger:
        '''Makes a new document with some pages from the source document.
        
        :param extract_options: The page options.'''
        raise NotImplementedError()
    
    def add_password(self, add_password_options : groupdocs.merger.domain.options.IAddPasswordOptions) -> groupdocs.merger.IMerger:
        '''Protects document with password.
        
        :param add_password_options: The options for specifying the password.'''
        raise NotImplementedError()
    
    def is_password_set(self) -> bool:
        '''Checks whether document is password protected.
        
        :returns: Returns a value indicating whether document is protected or not.'''
        raise NotImplementedError()
    
    def remove_password(self) -> groupdocs.merger.IMerger:
        '''Removes password from document.'''
        raise NotImplementedError()
    
    def update_password(self, update_password_options : groupdocs.merger.domain.options.IUpdatePasswordOptions) -> groupdocs.merger.IMerger:
        '''Updates existing password for document.
        
        :param update_password_options: The options for specifying the current/new passwords.'''
        raise NotImplementedError()
    
    def change_orientation(self, orientation_options : groupdocs.merger.domain.options.IOrientationOptions) -> groupdocs.merger.IMerger:
        '''Applies a new orientation mode for the specified pages.
        
        :param orientation_options: The change orientation options.'''
        raise NotImplementedError()
    
    def move_page(self, move_options : groupdocs.merger.domain.options.IMoveOptions) -> groupdocs.merger.IMerger:
        '''Moves page to a new position within document of known format.
        
        :param move_options: The move options.'''
        raise NotImplementedError()
    
    def remove_pages(self, remove_options : groupdocs.merger.domain.options.IRemoveOptions) -> groupdocs.merger.IMerger:
        '''Removes pages from document of known format.
        
        :param remove_options: The options for the numbers of pages to be removed.'''
        raise NotImplementedError()
    
    def swap_pages(self, swap_options : groupdocs.merger.domain.options.ISwapOptions) -> groupdocs.merger.IMerger:
        '''Swaps two pages within document of known format.
        
        :param swap_options: The swap options.'''
        raise NotImplementedError()
    
    def rotate_pages(self, rotate_options : groupdocs.merger.domain.options.IRotateOptions) -> groupdocs.merger.IMerger:
        '''Rotate pages of the document.
        
        :param rotate_options: The options for the page rotating.'''
        raise NotImplementedError()
    
    def get_document_info(self) -> groupdocs.merger.domain.result.IDocumentInfo:
        '''Gets information about document pages: their sizes, maximum page height, the width of a page with the maximum height.
        
        :returns: Information about document properties.'''
        raise NotImplementedError()
    
    def generate_preview(self, preview_options : groupdocs.merger.domain.options.IPreviewOptions) -> None:
        '''Generates document pages preview.
        
        :param preview_options: The preview options.'''
        raise NotImplementedError()
    

class MergerSettings:
    '''Defines settings for customizing :py:class:`groupdocs.merger.Merger` behaviour.'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes new instance of :py:class:`groupdocs.merger.MergerSettings` class.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, logger : groupdocs.merger.logging.ILogger) -> None:
        '''Initializes new instance of :py:class:`groupdocs.merger.MergerSettings` class.
        
        :param logger: The logger implementation.'''
        raise NotImplementedError()
    
    @property
    def logger(self) -> groupdocs.merger.logging.ILogger:
        '''The logger implementation that is used for tracking document processing workflow.'''
        raise NotImplementedError()
    
    @logger.setter
    def logger(self, value : groupdocs.merger.logging.ILogger) -> None:
        '''The logger implementation that is used for tracking document processing workflow.'''
        raise NotImplementedError()
    

class Metered:
    '''Provides methods for applying `Metered <https://purchase.groupdocs.com/faqs/licensing/metered>` license.'''
    
    def __init__(self) -> None:
        raise NotImplementedError()
    
    def set_metered_key(self, public_key : str, private_key : str) -> None:
        '''Activates product with Metered keys.
        
        :param public_key: The public key.
        :param private_key: The private key.'''
        raise NotImplementedError()
    
    @staticmethod
    def get_consumption_quantity() -> float:
        '''Retrieves amount of MBs processed.'''
        raise NotImplementedError()
    
    @staticmethod
    def get_consumption_credit() -> float:
        '''Retrieves amount of used credits'''
        raise NotImplementedError()
    

