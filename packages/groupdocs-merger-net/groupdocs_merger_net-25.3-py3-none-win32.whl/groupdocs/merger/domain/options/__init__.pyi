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

class AddPasswordOptions(IAddPasswordOptions):
    '''Provides options for adding document password.'''
    
    def __init__(self, password : str) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.AddPasswordOptions` class.
        
        :param password: The password.'''
        raise NotImplementedError()
    
    @property
    def password(self) -> str:
        '''The password for document protection.'''
        raise NotImplementedError()
    

class ExtractOptions(PageOptions):
    '''Provides options to extract the document pages.'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.ExtractOptions` class.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, page_numbers : List[int]) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.ExtractOptions` class.
        
        :param page_numbers: Page numbers.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, start_number : int, end_number : int) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.ExtractOptions` class.
        
        :param start_number: The start page number.
        :param end_number: The end page number.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, start_number : int, end_number : int, mode : groupdocs.merger.domain.options.RangeMode) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.ExtractOptions` class.
        
        :param start_number: The start page number.
        :param end_number: The end page number.
        :param mode: The range mode.'''
        raise NotImplementedError()
    
    @property
    def pages(self) -> List[int]:
        '''Get page numbers collection.'''
        raise NotImplementedError()
    

class IAddPasswordOptions(IOptions):
    '''Interface for the password adding options.'''
    
    @property
    def password(self) -> str:
        '''The password for document protection.'''
        raise NotImplementedError()
    

class IExtractOptions(IPageOptions):
    '''Interface for options to extract the document pages.'''
    
    @property
    def pages(self) -> List[int]:
        '''Page numbers for the page options.'''
        raise NotImplementedError()
    

class IImageJoinOptions(IJoinOptions):
    '''Interface for the image joining options.'''
    
    @property
    def mode(self) -> groupdocs.merger.domain.options.ImageJoinMode:
        '''The image join mode.'''
        raise NotImplementedError()
    
    @property
    def type(self) -> groupdocs.merger.domain.FileType:
        '''The type of the file to join.'''
        raise NotImplementedError()
    

class IImportDocumentOptions(IOptions):
    '''Interface for import of the embedded document.'''
    
    @property
    def object_data(self) -> List[int]:
        '''The data of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def extension(self) -> str:
        '''The extension of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def page_number(self) -> int:
        '''The page number for inserting of the embedded object.'''
        raise NotImplementedError()
    

class IJoinOptions(IOptions):
    '''Interface for the document joining options.'''
    
    @property
    def type(self) -> groupdocs.merger.domain.FileType:
        '''The type of the file to join.'''
        raise NotImplementedError()
    

class ILoadOptions(IOptions):
    '''Interface for the document loading options.'''
    
    @property
    def type(self) -> groupdocs.merger.domain.FileType:
        '''The type of the file to open.'''
        raise NotImplementedError()
    
    @property
    def extension(self) -> str:
        '''The extension of the file to open.'''
        raise NotImplementedError()
    
    @property
    def password(self) -> str:
        '''The password for opening password-protected file.'''
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        '''The encoding used when opening text-based files such as :py:attr:`groupdocs.merger.domain.FileType.CSV` or :py:attr:`groupdocs.merger.domain.FileType.TXT`.
        Default value is :py:attr:`str.Default`.'''
        raise NotImplementedError()
    

class IMoveOptions(IOptions):
    '''Interface for the moving page options.'''
    
    @property
    def page_number_to_move(self) -> int:
        '''Gets the page number to move.'''
        raise NotImplementedError()
    
    @property
    def new_page_number(self) -> int:
        '''Gets the new page number.'''
        raise NotImplementedError()
    

class IOleDiagramOptions(IImportDocumentOptions):
    '''Interface for import options of the embedded document to Diagram via OLE.'''
    
    @property
    def x(self) -> int:
        '''The X coordinate of the embedded object shape\'s pin (center of rotation) in relation to the page.'''
        raise NotImplementedError()
    
    @x.setter
    def x(self, value : int) -> None:
        '''The X coordinate of the embedded object shape\'s pin (center of rotation) in relation to the page.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> int:
        '''The Y coordinate of the embedded object shape\'s pin (center of rotation) in relation to the page.'''
        raise NotImplementedError()
    
    @y.setter
    def y(self, value : int) -> None:
        '''The Y coordinate of the embedded object shape\'s pin (center of rotation) in relation to the page.'''
        raise NotImplementedError()
    
    @property
    def image_data(self) -> List[int]:
        '''The image data of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def object_data(self) -> List[int]:
        '''The data of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def extension(self) -> str:
        '''The extension of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def page_number(self) -> int:
        '''The page number for inserting of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> int:
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : int) -> None:
        raise NotImplementedError()
    

class IOlePresentationOptions(IImportDocumentOptions):
    '''Interface for import options of the embedded document to Presentation via OLE.'''
    
    @property
    def x(self) -> int:
        '''The X coordinate of the embedded object frame.'''
        raise NotImplementedError()
    
    @x.setter
    def x(self, value : int) -> None:
        '''The X coordinate of the embedded object frame.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> int:
        '''The Y coordinate of the embedded object frame.'''
        raise NotImplementedError()
    
    @y.setter
    def y(self, value : int) -> None:
        '''The Y coordinate of the embedded object frame.'''
        raise NotImplementedError()
    
    @property
    def object_data(self) -> List[int]:
        '''The data of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def extension(self) -> str:
        '''The extension of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def page_number(self) -> int:
        '''The page number for inserting of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> int:
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : int) -> None:
        raise NotImplementedError()
    

class IOleSpreadsheetOptions(IImportDocumentOptions):
    '''Interface for import options of the embedded document to Spreadsheet via OLE.'''
    
    @property
    def row_index(self) -> int:
        '''The upper left row index.'''
        raise NotImplementedError()
    
    @row_index.setter
    def row_index(self, value : int) -> None:
        '''The upper left row index.'''
        raise NotImplementedError()
    
    @property
    def column_index(self) -> int:
        '''The upper left column index.'''
        raise NotImplementedError()
    
    @column_index.setter
    def column_index(self, value : int) -> None:
        '''The upper left column index.'''
        raise NotImplementedError()
    
    @property
    def image_data(self) -> List[int]:
        '''The data of the Ole object image.'''
        raise NotImplementedError()
    
    @property
    def object_data(self) -> List[int]:
        '''The data of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def extension(self) -> str:
        '''The extension of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def page_number(self) -> int:
        '''The page number for inserting of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> int:
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : int) -> None:
        raise NotImplementedError()
    

class IOleWordProcessingOptions(IImportDocumentOptions):
    '''Interface for import options of the embedded document to Word processing via OLE.'''
    
    @property
    def left(self) -> int:
        '''The left coordinate of the Ole object image.'''
        raise NotImplementedError()
    
    @left.setter
    def left(self, value : int) -> None:
        '''The left coordinate of the Ole object image.'''
        raise NotImplementedError()
    
    @property
    def top(self) -> int:
        '''The top coordinate of the Ole object image.'''
        raise NotImplementedError()
    
    @top.setter
    def top(self, value : int) -> None:
        '''The top coordinate of the Ole object image.'''
        raise NotImplementedError()
    
    @property
    def image_data(self) -> List[int]:
        '''The data of the Ole object image.'''
        raise NotImplementedError()
    
    @property
    def object_data(self) -> List[int]:
        '''The data of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def extension(self) -> str:
        '''The extension of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def page_number(self) -> int:
        '''The page number for inserting of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> int:
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : int) -> None:
        raise NotImplementedError()
    

class IOptions:
    '''Interface for the base options.'''
    

class IOrientationOptions(IPageOptions):
    '''Interface for the page orientation options.'''
    
    @property
    def mode(self) -> groupdocs.merger.domain.options.OrientationMode:
        '''Gets the mode for the page orientation.'''
        raise NotImplementedError()
    
    @property
    def pages(self) -> List[int]:
        '''Page numbers for the page options.'''
        raise NotImplementedError()
    

class IPageBuilderOptions(IOptions):
    '''Interface for the page builder options'''
    
    @property
    def load_document_info(self) -> bool:
        '''Specifies if each document info should load all its pages info.'''
        raise NotImplementedError()
    
    @load_document_info.setter
    def load_document_info(self, value : bool) -> None:
        '''Specifies if each document info should load all its pages info.'''
        raise NotImplementedError()
    

class IPageJoinOptions(IPageOptions):
    '''Interface for the document page joining options.'''
    
    @property
    def pages(self) -> List[int]:
        '''Page numbers for the page options.'''
        raise NotImplementedError()
    
    @property
    def type(self) -> groupdocs.merger.domain.FileType:
        raise NotImplementedError()
    

class IPageOptions(IOptions):
    '''Interface for the page options'''
    
    @property
    def pages(self) -> List[int]:
        '''Page numbers for the page options.'''
        raise NotImplementedError()
    

class IPager:
    '''Interface for apply option (pages, range and etc.)'''
    
    @property
    def pages(self) -> List[int]:
        '''List of page number on which operation will be applied. Note: first page have number 1.'''
        raise NotImplementedError()
    

class IPdfAttachmentOptions(IImportDocumentOptions):
    '''Interface for options of the embedded document to PDF as attachment.'''
    
    @property
    def object_data(self) -> List[int]:
        '''The data of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def extension(self) -> str:
        '''The extension of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def page_number(self) -> int:
        '''The page number for inserting of the embedded object.'''
        raise NotImplementedError()
    

class IPreviewOptions(IPageOptions):
    '''Interface for the preview options.'''
    
    def validate(self, file_type : groupdocs.merger.domain.FileType) -> None:
        '''Validates the split options.
        
        :param file_type: The file type of :py:class:`groupdocs.merger.domain.FileType` class.'''
        raise NotImplementedError()
    
    def get_path_by_page_number(self, page_number : int, extension : str) -> str:
        '''Gets the full file path of previewed document by page number with defined extension.
        
        :param page_number: Page number of preview.
        :param extension: Extension of file.
        :returns: The full file path.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> int:
        '''Preview width.'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : int) -> None:
        '''Preview width.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        '''Preview height.'''
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : int) -> None:
        '''Preview height.'''
        raise NotImplementedError()
    
    @property
    def resolution(self) -> int:
        '''Image resolution.'''
        raise NotImplementedError()
    
    @resolution.setter
    def resolution(self, value : int) -> None:
        '''Image resolution.'''
        raise NotImplementedError()
    
    @property
    def mode(self) -> groupdocs.merger.domain.options.PreviewMode:
        '''Gets the mode for preview.'''
        raise NotImplementedError()
    
    @property
    def pages(self) -> List[int]:
        '''Page numbers for the page options.'''
        raise NotImplementedError()
    

class IRemoveOptions(IPageOptions):
    '''Interface for the page removing options.'''
    
    @property
    def pages(self) -> List[int]:
        '''Page numbers for the page options.'''
        raise NotImplementedError()
    

class IRotateOptions(IPageOptions):
    '''Interface for the page rotating options.'''
    
    @property
    def mode(self) -> groupdocs.merger.domain.options.RotateMode:
        '''Gets the mode for rotating (90, 180 or 270 degrees).'''
        raise NotImplementedError()
    
    @property
    def pages(self) -> List[int]:
        '''Page numbers for the page options.'''
        raise NotImplementedError()
    

class ISaveOptions(IOptions):
    '''Interface for the document saving options.'''
    
    @property
    def type(self) -> groupdocs.merger.domain.FileType:
        '''File type.'''
        raise NotImplementedError()
    

class ISizeOptions:
    '''Interface for adding embedded object.'''
    
    @property
    def width(self) -> int:
        '''The width of the embedded object size.'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : int) -> None:
        '''The width of the embedded object size.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        '''The height of the embedded object size.'''
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : int) -> None:
        '''The height of the embedded object size.'''
        raise NotImplementedError()
    

class ISplitOptions(IPageOptions):
    '''Interface for the page splitting options.'''
    
    def validate(self, file_type : groupdocs.merger.domain.FileType) -> None:
        '''Validates the split options.
        
        :param file_type: The file type of :py:class:`groupdocs.merger.domain.FileType` class.'''
        raise NotImplementedError()
    
    def get_path_by_index(self, index : int, extension : str) -> str:
        '''Gets the full file path of splitted document by index with defined extension.
        
        :param index: Index of splitted document.
        :param extension: Extension of file.
        :returns: The full file path.'''
        raise NotImplementedError()
    
    @property
    def mode(self) -> groupdocs.merger.domain.options.SplitMode:
        '''Gets the mode for page splitting.'''
        raise NotImplementedError()
    
    @property
    def pages(self) -> List[int]:
        '''Page numbers for the page options.'''
        raise NotImplementedError()
    

class ISwapOptions(IOptions):
    '''Interface for the page swapping options.'''
    
    @property
    def first_page_number(self) -> int:
        '''First page number to exchange.'''
        raise NotImplementedError()
    
    @property
    def second_page_number(self) -> int:
        '''Second page number to exchange.'''
        raise NotImplementedError()
    

class ITextSplitOptions(IOptions):
    '''Interface for the text splitting options.'''
    
    def validate(self, file_type : groupdocs.merger.domain.FileType) -> None:
        '''Validates the split options.
        
        :param file_type: The file type of :py:class:`groupdocs.merger.domain.FileType` class.'''
        raise NotImplementedError()
    
    def get_path_by_index(self, index : int, extension : str) -> str:
        '''Gets the full file path of splitted document by index with defined extension.
        
        :param index: Index of splitted document.
        :param extension: Extension of file.
        :returns: The full file path.'''
        raise NotImplementedError()
    
    @property
    def line_numbers(self) -> List[int]:
        '''Line numbers for text splitting.'''
        raise NotImplementedError()
    
    @property
    def mode(self) -> groupdocs.merger.domain.options.TextSplitMode:
        '''Mode for text splitting.'''
        raise NotImplementedError()
    

class IUpdatePasswordOptions(IOptions):
    '''Interface for the password updating options.'''
    
    @property
    def new_password(self) -> str:
        '''The new password for document protection.'''
        raise NotImplementedError()
    

class ImageJoinOptions(IImageJoinOptions):
    '''The image join options.'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes new instance of :py:class:`groupdocs.merger.domain.options.ImageJoinOptions` class.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_type : groupdocs.merger.domain.FileType) -> None:
        '''Initializes new instance of :py:class:`groupdocs.merger.domain.options.ImageJoinOptions` class.
        
        :param file_type: The image file type.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, image_join_mode : groupdocs.merger.domain.options.ImageJoinMode) -> None:
        '''Initializes new instance of :py:class:`groupdocs.merger.domain.options.ImageJoinOptions` class.
        
        :param image_join_mode: The image join mode.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_type : groupdocs.merger.domain.FileType, image_join_mode : groupdocs.merger.domain.options.ImageJoinMode) -> None:
        '''Initializes new instance of :py:class:`groupdocs.merger.domain.options.ImageJoinOptions` class.
        
        :param file_type: The image file type.
        :param image_join_mode: The image join mode.'''
        raise NotImplementedError()
    
    @property
    def type(self) -> groupdocs.merger.domain.FileType:
        '''The image file type.'''
        raise NotImplementedError()
    
    @property
    def mode(self) -> groupdocs.merger.domain.options.ImageJoinMode:
        '''The image join mode.'''
        raise NotImplementedError()
    

class ImportDocumentOptions(IImportDocumentOptions):
    '''Provides options for the embedded document import.'''
    
    @property
    def object_data(self) -> List[int]:
        '''The data of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def extension(self) -> str:
        '''The extension of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def page_number(self) -> int:
        '''The page number for inserting of the embedded object.'''
        raise NotImplementedError()
    

class JoinOptions(IJoinOptions):
    '''Provides options for the document joining.'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.JoinOptions` class.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_type : groupdocs.merger.domain.FileType) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.JoinOptions` class.
        
        :param file_type: The type of the file to join.'''
        raise NotImplementedError()
    
    @property
    def type(self) -> groupdocs.merger.domain.FileType:
        '''The type of the file to join.'''
        raise NotImplementedError()
    

class LoadOptions(ILoadOptions):
    '''Provides options for the document loading.'''
    
    @overload
    def __init__(self, file_type : groupdocs.merger.domain.FileType) -> None:
        '''Initializes new instance of :py:class:`groupdocs.merger.domain.options.LoadOptions` class.
        
        :param file_type: The type of the file to load.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, password : str) -> None:
        '''Initializes new instance of :py:class:`groupdocs.merger.domain.options.LoadOptions` class.
        
        :param password: The password for opening password-protected file.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, password : str, encoding : str) -> None:
        '''Initializes new instance of :py:class:`groupdocs.merger.domain.options.LoadOptions` class.
        
        :param password: The password for opening password-protected file.
        :param encoding: The encoding used when opening text-based files such as :py:attr:`groupdocs.merger.domain.FileType.CSV` or :py:attr:`groupdocs.merger.domain.FileType.TXT`.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_type : groupdocs.merger.domain.FileType, password : str) -> None:
        '''Initializes new instance of :py:class:`groupdocs.merger.domain.options.LoadOptions` class.
        
        :param file_type: The type of the file to load.
        :param password: The password for opening password-protected file.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_type : groupdocs.merger.domain.FileType, password : str, encoding : str) -> None:
        '''Initializes new instance of :py:class:`groupdocs.merger.domain.options.LoadOptions` class.
        
        :param file_type: The type of the file to load.
        :param password: The password for opening password-protected file.
        :param encoding: The encoding used when opening text-based files such as :py:attr:`groupdocs.merger.domain.FileType.CSV` or :py:attr:`groupdocs.merger.domain.FileType.TXT`.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, extension : str, file_type : groupdocs.merger.domain.FileType, password : str, encoding : str) -> None:
        '''Initializes new instance of :py:class:`groupdocs.merger.domain.options.LoadOptions` class.
        
        :param extension: The extension of the file to load.
        :param file_type: The type of the file to load.
        :param password: The password for opening password-protected file.
        :param encoding: The encoding used when opening text-based files such as :py:attr:`groupdocs.merger.domain.FileType.CSV` or :py:attr:`groupdocs.merger.domain.FileType.TXT`.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, ini_file_type : groupdocs.merger.domain.FileType, file_type : groupdocs.merger.domain.FileType, password : str, encoding : str) -> None:
        '''Initializes new instance of :py:class:`groupdocs.merger.domain.options.LoadOptions` class.
        
        :param ini_file_type: The type of the file to init.
        :param file_type: The type of the file to load.
        :param password: The password for opening password-protected file.
        :param encoding: The encoding used when opening text-based files such as :py:attr:`groupdocs.merger.domain.FileType.CSV` or :py:attr:`groupdocs.merger.domain.FileType.TXT`.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, ini_file_type : groupdocs.merger.domain.FileType, file_type : groupdocs.merger.domain.FileType, password : str) -> None:
        '''Initializes new instance of :py:class:`groupdocs.merger.domain.options.LoadOptions` class.
        
        :param ini_file_type: The type of the file to init.
        :param file_type: The type of the file to load.
        :param password: The password for opening password-protected file.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, ini_file_type : groupdocs.merger.domain.FileType, file_type : groupdocs.merger.domain.FileType) -> None:
        '''Initializes new instance of :py:class:`groupdocs.merger.domain.options.LoadOptions` class.
        
        :param ini_file_type: The type of the file to init.
        :param file_type: The type of the file to load.'''
        raise NotImplementedError()
    
    @property
    def type(self) -> groupdocs.merger.domain.FileType:
        '''The type of the file to load.'''
        raise NotImplementedError()
    
    @property
    def extension(self) -> str:
        '''The extension of the file to init.'''
        raise NotImplementedError()
    
    @property
    def password(self) -> str:
        '''The password for opening password-protected file.'''
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        '''The encoding used when opening text-based files such as :py:attr:`groupdocs.merger.domain.FileType.CSV` or :py:attr:`groupdocs.merger.domain.FileType.TXT`.
        Default value is :py:attr:`str.Default`.'''
        raise NotImplementedError()
    

class MoveOptions(IMoveOptions):
    '''Provides options for moving document page.'''
    
    def __init__(self, page_number_to_move : int, new_page_number : int) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.MoveOptions` class.
        
        :param page_number_to_move: The page number to move.
        :param new_page_number: The new page number.'''
        raise NotImplementedError()
    
    @property
    def page_number_to_move(self) -> int:
        '''Gets the page number to move.'''
        raise NotImplementedError()
    
    @property
    def new_page_number(self) -> int:
        '''Gets the new page number.'''
        raise NotImplementedError()
    

class OleDiagramOptions(ImportDocumentOptions):
    '''Provides options for import of the embedded document to Diagram via OLE.'''
    
    @overload
    def __init__(self, object_data : List[int], image_data : List[int], extension : str, page_number : int) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.OleDiagramOptions` class.
        
        :param object_data: The data of the embedded object.
        :param image_data: The image data of the embedded object.
        :param extension: The extension of the embedded object.
        :param page_number: The page number for adding embedded object.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_path : str, image_data : List[int], page_number : int) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.OleDiagramOptions` class.
        
        :param file_path: The file path of the embedded object.
        :param image_data: The image data of the embedded object.
        :param page_number: The page number for adding embedded object.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_path : str, page_number : int) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.OleDiagramOptions` class.
        
        :param file_path: The file path of the embedded object.
        :param page_number: The page number for adding embedded object.'''
        raise NotImplementedError()
    
    @property
    def object_data(self) -> List[int]:
        '''The data of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def extension(self) -> str:
        '''The extension of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def page_number(self) -> int:
        '''The page number for inserting of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> int:
        '''The X coordinate of the embedded object shape\'s pin (center of rotation) in relation to the page.'''
        raise NotImplementedError()
    
    @x.setter
    def x(self, value : int) -> None:
        '''The X coordinate of the embedded object shape\'s pin (center of rotation) in relation to the page.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> int:
        '''The Y coordinate of the embedded object shape\'s pin (center of rotation) in relation to the page.'''
        raise NotImplementedError()
    
    @y.setter
    def y(self, value : int) -> None:
        '''The Y coordinate of the embedded object shape\'s pin (center of rotation) in relation to the page.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> int:
        '''The width of the embedded object shape in inches.'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : int) -> None:
        '''The width of the embedded object shape in inches.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        '''The height of the embedded object shape in inches.'''
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : int) -> None:
        '''The height of the embedded object shape in inches.'''
        raise NotImplementedError()
    
    @property
    def image_data(self) -> List[int]:
        '''The image data of the embedded object.'''
        raise NotImplementedError()
    

class OlePresentationOptions(ImportDocumentOptions):
    '''Provides options for import of the embedded document to Presentation via OLE.'''
    
    @overload
    def __init__(self, object_data : List[int], extension : str, page_number : int) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.OlePresentationOptions` class.
        
        :param object_data: The data of the embedded object.
        :param extension: The extension of the embedded object.
        :param page_number: The page number for adding embedded object.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_path : str, page_number : int) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.OlePresentationOptions` class.
        
        :param file_path: The file path of the embedded object.
        :param page_number: The page number for adding embedded object.'''
        raise NotImplementedError()
    
    @property
    def object_data(self) -> List[int]:
        '''The data of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def extension(self) -> str:
        '''The extension of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def page_number(self) -> int:
        '''The page number for inserting of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> int:
        '''The X coordinate of the embedded object frame.'''
        raise NotImplementedError()
    
    @x.setter
    def x(self, value : int) -> None:
        '''The X coordinate of the embedded object frame.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> int:
        '''The Y coordinate of the embedded object frame.'''
        raise NotImplementedError()
    
    @y.setter
    def y(self, value : int) -> None:
        '''The Y coordinate of the embedded object frame.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> int:
        '''The width of the embedded object frame.'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : int) -> None:
        '''The width of the embedded object frame.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        '''The height of the embedded object frame.'''
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : int) -> None:
        '''The height of the embedded object frame.'''
        raise NotImplementedError()
    

class OleSpreadsheetOptions(ImportDocumentOptions):
    '''Provides options for import of the embedded document to Spreadsheet via OLE.'''
    
    @overload
    def __init__(self, object_data : List[int], image_data : List[int], extension : str, page_number : int) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.OleSpreadsheetOptions` class.
        
        :param object_data: The data of the embedded object.
        :param image_data: The image data of the embedded object.
        :param extension: The extension of the embedded object.
        :param page_number: The page number for adding embedded object.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_path : str, image_data : List[int], page_number : int) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.OleSpreadsheetOptions` class.
        
        :param file_path: The file path of the embedded object.
        :param image_data: The image data of the embedded object.
        :param page_number: The page number for adding embedded object.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_path : str, page_number : int) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.OleSpreadsheetOptions` class.
        
        :param file_path: The file path of the embedded object.
        :param page_number: The page number for adding embedded object.'''
        raise NotImplementedError()
    
    @property
    def object_data(self) -> List[int]:
        '''The data of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def extension(self) -> str:
        '''The extension of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def page_number(self) -> int:
        '''The page number for inserting of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def row_index(self) -> int:
        '''The upper left row index.'''
        raise NotImplementedError()
    
    @row_index.setter
    def row_index(self, value : int) -> None:
        '''The upper left row index.'''
        raise NotImplementedError()
    
    @property
    def column_index(self) -> int:
        '''The upper left column index.'''
        raise NotImplementedError()
    
    @column_index.setter
    def column_index(self, value : int) -> None:
        '''The upper left column index.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> int:
        '''The width of the Ole object image.'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : int) -> None:
        '''The width of the Ole object image.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        '''The height of the Ole object image.'''
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : int) -> None:
        '''The height of the Ole object image.'''
        raise NotImplementedError()
    
    @property
    def image_data(self) -> List[int]:
        '''The data of the Ole object image.'''
        raise NotImplementedError()
    

class OleWordProcessingOptions(ImportDocumentOptions):
    '''Provides options for import of the embedded document to Word processing via OLE.'''
    
    @overload
    def __init__(self, object_data : List[int], image_data : List[int], extension : str, page_number : int) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.OleWordProcessingOptions` class.
        
        :param object_data: The data of the embedded object.
        :param image_data: The image data of the embedded object.
        :param extension: The extension of the embedded object.
        :param page_number: The page number for adding embedded object.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_path : str, image_data : List[int], page_number : int) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.OleWordProcessingOptions` class.
        
        :param file_path: The file path of the embedded object.
        :param image_data: The image data of the embedded object.
        :param page_number: The page number for adding embedded object.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_path : str, page_number : int) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.OleWordProcessingOptions` class.
        
        :param file_path: The file path of the embedded object.
        :param page_number: The page number for adding embedded object.'''
        raise NotImplementedError()
    
    @property
    def object_data(self) -> List[int]:
        '''The data of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def extension(self) -> str:
        '''The extension of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def page_number(self) -> int:
        '''The page number for inserting of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def left(self) -> int:
        '''The left coordinate of the Ole object image.'''
        raise NotImplementedError()
    
    @left.setter
    def left(self, value : int) -> None:
        '''The left coordinate of the Ole object image.'''
        raise NotImplementedError()
    
    @property
    def top(self) -> int:
        '''The top coordinate of the Ole object image.'''
        raise NotImplementedError()
    
    @top.setter
    def top(self, value : int) -> None:
        '''The top coordinate of the Ole object image.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> int:
        '''The width of the Ole object image.'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : int) -> None:
        '''The width of the Ole object image.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        '''The height of the Ole object image.'''
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : int) -> None:
        '''The height of the Ole object image.'''
        raise NotImplementedError()
    
    @property
    def image_data(self) -> List[int]:
        '''The data of the Ole object image.'''
        raise NotImplementedError()
    

class OrientationOptions(PageOptions):
    '''Provides options for the page orientation.'''
    
    @overload
    def __init__(self, orientation_mode : groupdocs.merger.domain.options.OrientationMode) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.OrientationOptions` class.
        
        :param orientation_mode: The orientation mode of :py:class:`groupdocs.merger.domain.options.OrientationMode`'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, orientation_mode : groupdocs.merger.domain.options.OrientationMode, page_numbers : List[int]) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.OrientationOptions` class.
        
        :param orientation_mode: The orientation mode of :py:class:`groupdocs.merger.domain.options.OrientationMode`
        :param page_numbers: Page numbers.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, orientation_mode : groupdocs.merger.domain.options.OrientationMode, start_number : int, end_number : int) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.OrientationOptions` class.
        
        :param orientation_mode: The orientation mode of :py:class:`groupdocs.merger.domain.options.OrientationMode`
        :param start_number: The start page number.
        :param end_number: The end page number.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, orientation_mode : groupdocs.merger.domain.options.OrientationMode, start_number : int, end_number : int, mode : groupdocs.merger.domain.options.RangeMode) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.OrientationOptions` class.
        
        :param orientation_mode: The orientation mode of :py:class:`groupdocs.merger.domain.options.OrientationMode`
        :param start_number: The start page number.
        :param end_number: The end page number.
        :param mode: The range mode.'''
        raise NotImplementedError()
    
    @property
    def pages(self) -> List[int]:
        '''Get page numbers collection.'''
        raise NotImplementedError()
    
    @property
    def mode(self) -> groupdocs.merger.domain.options.OrientationMode:
        '''Gets the mode for the page orientation.'''
        raise NotImplementedError()
    

class PageBuilderOptions(IPageBuilderOptions):
    '''Provides options for specifying the page builder.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.PageBuilderOptions` class.'''
        raise NotImplementedError()
    
    @property
    def load_document_info(self) -> bool:
        '''Specifies if each document info should load all its pages info.'''
        raise NotImplementedError()
    
    @load_document_info.setter
    def load_document_info(self, value : bool) -> None:
        '''Specifies if each document info should load all its pages info.'''
        raise NotImplementedError()
    

class PageJoinOptions(PageOptions):
    '''Provides options for the document joining.'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.PageJoinOptions` class.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, page_numbers : List[int]) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.PageJoinOptions` class.
        
        :param page_numbers: Page numbers.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, start_number : int, end_number : int) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.PageJoinOptions` class.
        
        :param start_number: The start page number.
        :param end_number: The end page number.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, start_number : int, end_number : int, mode : groupdocs.merger.domain.options.RangeMode) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.PageJoinOptions` class.
        
        :param start_number: The start page number.
        :param end_number: The end page number.
        :param mode: The range mode.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_type : groupdocs.merger.domain.FileType) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.PageJoinOptions` class.
        
        :param file_type: The type of the file to join.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_type : groupdocs.merger.domain.FileType, page_numbers : List[int]) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.PageJoinOptions` class.
        
        :param file_type: The type of the file to join.
        :param page_numbers: Page numbers.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_type : groupdocs.merger.domain.FileType, start_number : int, end_number : int) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.PageJoinOptions` class.
        
        :param file_type: The type of the file to join.
        :param start_number: The start page number.
        :param end_number: The end page number.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_type : groupdocs.merger.domain.FileType, start_number : int, end_number : int, mode : groupdocs.merger.domain.options.RangeMode) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.PageJoinOptions` class.
        
        :param file_type: The type of the file to join.
        :param start_number: The start page number.
        :param end_number: The end page number.
        :param mode: The range mode.'''
        raise NotImplementedError()
    
    @property
    def pages(self) -> List[int]:
        '''Get page numbers collection.'''
        raise NotImplementedError()
    
    @property
    def type(self) -> groupdocs.merger.domain.FileType:
        '''The type of the file to join.'''
        raise NotImplementedError()
    

class PageOptions(IPageOptions):
    '''Provides options for specifying page or pages range.'''
    
    @property
    def pages(self) -> List[int]:
        '''Get page numbers collection.'''
        raise NotImplementedError()
    

class PdfAttachmentOptions(ImportDocumentOptions):
    '''Provides options to attach the embedded object to Pdf.'''
    
    @overload
    def __init__(self, object_data : List[int], extension : str) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.PdfAttachmentOptions` class.
        
        :param object_data: The data of the embedded object.
        :param extension: The extension of the embedded object.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_path : str) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.PdfAttachmentOptions` class.
        
        :param file_path: The file path of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def object_data(self) -> List[int]:
        '''The data of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def extension(self) -> str:
        '''The extension of the embedded object.'''
        raise NotImplementedError()
    
    @property
    def page_number(self) -> int:
        '''The page number for inserting of the embedded object.'''
        raise NotImplementedError()
    

class PdfJoinOptions(PageJoinOptions):
    '''The Pdf join options.'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.PdfJoinOptions` class.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, page_numbers : List[int]) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.PdfJoinOptions` class.
        
        :param page_numbers: Page numbers.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, start_number : int, end_number : int) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.PdfJoinOptions` class.
        
        :param start_number: The start page number.
        :param end_number: The end page number.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, start_number : int, end_number : int, mode : groupdocs.merger.domain.options.RangeMode) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.PdfJoinOptions` class.
        
        :param start_number: The start page number.
        :param end_number: The end page number.
        :param mode: The range mode.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_type : groupdocs.merger.domain.FileType) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.PdfJoinOptions` class.
        
        :param file_type: The type of the file to join.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_type : groupdocs.merger.domain.FileType, page_numbers : List[int]) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.PdfJoinOptions` class.
        
        :param file_type: The type of the file to join.
        :param page_numbers: Page numbers.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_type : groupdocs.merger.domain.FileType, start_number : int, end_number : int) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.PdfJoinOptions` class.
        
        :param file_type: The type of the file to join.
        :param start_number: The start page number.
        :param end_number: The end page number.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_type : groupdocs.merger.domain.FileType, start_number : int, end_number : int, mode : groupdocs.merger.domain.options.RangeMode) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.PdfJoinOptions` class.
        
        :param file_type: The type of the file to join.
        :param start_number: The start page number.
        :param end_number: The end page number.
        :param mode: The range mode.'''
        raise NotImplementedError()
    
    @property
    def pages(self) -> List[int]:
        '''Get page numbers collection.'''
        raise NotImplementedError()
    
    @property
    def type(self) -> groupdocs.merger.domain.FileType:
        '''The type of the file to join.'''
        raise NotImplementedError()
    
    @property
    def use_bookmarks(self) -> bool:
        '''Indicates if all the bookmarks will be copied by default.'''
        raise NotImplementedError()
    
    @use_bookmarks.setter
    def use_bookmarks(self, value : bool) -> None:
        '''Indicates if all the bookmarks will be copied by default.'''
        raise NotImplementedError()
    

class PdfSecurityOptions(AddPasswordOptions):
    '''Contains the PDF document security options.'''
    
    def __init__(self, password : str) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.PdfSecurityOptions` class.
        
        :param password: The password.'''
        raise NotImplementedError()
    
    @property
    def password(self) -> str:
        '''The password for document protection.'''
        raise NotImplementedError()
    
    @property
    def owner_password(self) -> str:
        '''The password required to change permission settings.
        Using a permissions password you can restrict printing, modification and data extraction.'''
        raise NotImplementedError()
    
    @owner_password.setter
    def owner_password(self, value : str) -> None:
        '''The password required to change permission settings.
        Using a permissions password you can restrict printing, modification and data extraction.'''
        raise NotImplementedError()
    
    @property
    def permissions(self) -> groupdocs.merger.domain.options.PdfSecurityPermissions:
        '''The PDF document permissions such as printing, modification and data extraction.'''
        raise NotImplementedError()
    
    @permissions.setter
    def permissions(self, value : groupdocs.merger.domain.options.PdfSecurityPermissions) -> None:
        '''The PDF document permissions such as printing, modification and data extraction.'''
        raise NotImplementedError()
    

class PreviewOptions(PageOptions):
    '''Represents document preview options.'''
    
    def validate(self, file_type : groupdocs.merger.domain.FileType) -> None:
        '''Validates the preview options.
        
        :param file_type: The file type.'''
        raise NotImplementedError()
    
    def get_path_by_page_number(self, page_number : int, extension : str) -> str:
        '''Gets the full file path of previewed document by page number with defined extension.
        
        :param page_number: Page number of preview.
        :param extension: Extension of file.
        :returns: The full file path.'''
        raise NotImplementedError()
    
    @property
    def pages(self) -> List[int]:
        '''Get page numbers collection.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> int:
        '''Preview width.'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : int) -> None:
        '''Preview width.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        '''Preview height.'''
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : int) -> None:
        '''Preview height.'''
        raise NotImplementedError()
    
    @property
    def resolution(self) -> int:
        '''Image resolution.'''
        raise NotImplementedError()
    
    @resolution.setter
    def resolution(self, value : int) -> None:
        '''Image resolution.'''
        raise NotImplementedError()
    
    @property
    def mode(self) -> groupdocs.merger.domain.options.PreviewMode:
        '''Mode for preview.'''
        raise NotImplementedError()
    

class RemoveOptions(PageOptions):
    '''Provides options for the page removing.'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.RemoveOptions` class.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, page_numbers : List[int]) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.RemoveOptions` class.
        
        :param page_numbers: Page numbers.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, start_number : int, end_number : int) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.RemoveOptions` class.
        
        :param start_number: The start page number.
        :param end_number: The end page number.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, start_number : int, end_number : int, mode : groupdocs.merger.domain.options.RangeMode) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.RemoveOptions` class.
        
        :param start_number: The start page number.
        :param end_number: The end page number.
        :param mode: The range mode.'''
        raise NotImplementedError()
    
    @property
    def pages(self) -> List[int]:
        '''Get page numbers collection.'''
        raise NotImplementedError()
    

class RotateOptions(PageOptions):
    '''Provides options for the page rotation.'''
    
    @overload
    def __init__(self, rotate_mode : groupdocs.merger.domain.options.RotateMode) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.RotateOptions` class.
        
        :param rotate_mode: The rotating mode of :py:attr:`groupdocs.merger.domain.options.RotateOptions.mode`'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, rotate_mode : groupdocs.merger.domain.options.RotateMode, page_numbers : List[int]) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.RotateOptions` class.
        
        :param rotate_mode: The rotating mode of :py:attr:`groupdocs.merger.domain.options.RotateOptions.mode`
        :param page_numbers: Page numbers.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, rotate_mode : groupdocs.merger.domain.options.RotateMode, start_number : int, end_number : int) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.RotateOptions` class.
        
        :param rotate_mode: The rotating mode of :py:attr:`groupdocs.merger.domain.options.RotateOptions.mode`
        :param start_number: The start page number.
        :param end_number: The end page number.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, rotate_mode : groupdocs.merger.domain.options.RotateMode, start_number : int, end_number : int, mode : groupdocs.merger.domain.options.RangeMode) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.RotateOptions` class.
        
        :param rotate_mode: The rotating mode of :py:attr:`groupdocs.merger.domain.options.RotateOptions.mode`
        :param start_number: The start page number.
        :param end_number: The end page number.
        :param mode: The range mode.'''
        raise NotImplementedError()
    
    @property
    def pages(self) -> List[int]:
        '''Get page numbers collection.'''
        raise NotImplementedError()
    
    @property
    def mode(self) -> groupdocs.merger.domain.options.RotateMode:
        '''Gets the mode for rotating (90, 180 or 270 degrees).'''
        raise NotImplementedError()
    

class SaveOptions(ISaveOptions):
    '''Provides options for the document saving.'''
    
    def __init__(self, file_type : groupdocs.merger.domain.FileType) -> None:
        '''Initializes new instance of :py:class:`groupdocs.merger.domain.options.SaveOptions` class.
        
        :param file_type: The type of the file.'''
        raise NotImplementedError()
    
    @property
    def type(self) -> groupdocs.merger.domain.FileType:
        '''File type.'''
        raise NotImplementedError()
    

class SplitOptions(PageOptions):
    '''Provides options for the document page splitting.'''
    
    @overload
    def __init__(self, file_path_format : str, page_numbers : List[int]) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.SplitOptions` class.
        
        :param file_path_format: The file path format e.g. \'c:/split{0}.doc\' or \'c:/split{0}.{1}\' with already pre-defined extension.
        :param page_numbers: Page numbers.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_path_format : str, page_numbers : List[int], split_mode : groupdocs.merger.domain.options.SplitMode) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.SplitOptions` class.
        
        :param file_path_format: The file path format e.g. \'c:/split{0}.doc\' or \'c:/split{0}.{1}\' with already pre-defined extension.
        :param page_numbers: Page numbers.
        :param split_mode: The splitting mode of :py:attr:`groupdocs.merger.domain.options.SplitOptions.mode`.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_path_format : str, start_number : int, end_number : int) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.SplitOptions` class.
        
        :param file_path_format: The file path format e.g. \'c:/split{0}.doc\' or \'c:/split{0}.{1}\' with already pre-defined extension.
        :param start_number: The start page number.
        :param end_number: The end page number.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_path_format : str, start_number : int, end_number : int, mode : groupdocs.merger.domain.options.RangeMode) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.SplitOptions` class.
        
        :param file_path_format: The file path format e.g. \'c:/split{0}.doc\' or \'c:/split{0}.{1}\' with already pre-defined extension.
        :param start_number: The start page number.
        :param end_number: The end page number.
        :param mode: The range mode.'''
        raise NotImplementedError()
    
    def validate(self, file_type : groupdocs.merger.domain.FileType) -> None:
        '''Validates the split options.
        
        :param file_type: The file type of :py:class:`groupdocs.merger.domain.FileType` class.'''
        raise NotImplementedError()
    
    def get_path_by_index(self, index : int, extension : str) -> str:
        '''Gets the full file path of splitted document by index with pre-defined extension.
        
        :param index: Index of splitted document.
        :param extension: Extension of file.
        :returns: The full file path.'''
        raise NotImplementedError()
    
    @property
    def pages(self) -> List[int]:
        '''Get page numbers collection.'''
        raise NotImplementedError()
    
    @property
    def mode(self) -> groupdocs.merger.domain.options.SplitMode:
        '''Gets the mode for page splitting.'''
        raise NotImplementedError()
    

class SwapOptions(ISwapOptions):
    '''Provides options for swapping document pages.'''
    
    def __init__(self, first_page_number : int, second_page_number : int) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.SwapOptions` class.
        
        :param first_page_number: The first page number.
        :param second_page_number: The second page number.'''
        raise NotImplementedError()
    
    @property
    def first_page_number(self) -> int:
        '''First page number to exchange.'''
        raise NotImplementedError()
    
    @property
    def second_page_number(self) -> int:
        '''Second page number to exchange.'''
        raise NotImplementedError()
    

class TextSplitOptions(ITextSplitOptions):
    '''Provides options for the document text splitting.'''
    
    @overload
    def __init__(self, file_path_format : str, line_numbers : List[int]) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.TextSplitOptions` class.
        
        :param file_path_format: The file path format e.g. \'c:/split{0}.doc\' or \'c:/split{0}.{1}\' with already defined extension.
        :param line_numbers: Line numbers for text splitting.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_path_format : str, mode : groupdocs.merger.domain.options.TextSplitMode, line_numbers : List[int]) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.TextSplitOptions` class.
        
        :param file_path_format: The file path format e.g. \'c:/split{0}.doc\' or \'c:/split{0}.{1}\' with already defined extension.
        :param mode: Mode for text splitting.
        :param line_numbers: Line numbers for text splitting.'''
        raise NotImplementedError()
    
    def validate(self, file_type : groupdocs.merger.domain.FileType) -> None:
        '''Validates the split options.
        
        :param file_type: The file type of :py:class:`groupdocs.merger.domain.FileType` class.'''
        raise NotImplementedError()
    
    def get_path_by_index(self, index : int, extension : str) -> str:
        '''Gets the full file path of splitted document by index with defined extension.
        
        :param index: Index of splitted document.
        :param extension: Extension of file.
        :returns: The full file path.'''
        raise NotImplementedError()
    
    @property
    def mode(self) -> groupdocs.merger.domain.options.TextSplitMode:
        '''Mode for text splitting.'''
        raise NotImplementedError()
    
    @property
    def line_numbers(self) -> List[int]:
        '''Line numbers for text splitting.'''
        raise NotImplementedError()
    

class UpdatePasswordOptions(IUpdatePasswordOptions):
    '''Provides options for updating document password.'''
    
    def __init__(self, new_password : str) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.UpdatePasswordOptions` class.
        
        :param new_password: The new password.'''
        raise NotImplementedError()
    
    @property
    def new_password(self) -> str:
        '''A new password for the document protection.'''
        raise NotImplementedError()
    

class WordJoinOptions(PageJoinOptions):
    '''The Word join options.'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.WordJoinOptions` class.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, page_numbers : List[int]) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.WordJoinOptions` class.
        
        :param page_numbers: Page numbers.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, start_number : int, end_number : int) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.WordJoinOptions` class.
        
        :param start_number: The start page number.
        :param end_number: The end page number.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, start_number : int, end_number : int, mode : groupdocs.merger.domain.options.RangeMode) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.WordJoinOptions` class.
        
        :param start_number: The start page number.
        :param end_number: The end page number.
        :param mode: The range mode.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_type : groupdocs.merger.domain.FileType) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.WordJoinOptions` class.
        
        :param file_type: The type of the file to join.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_type : groupdocs.merger.domain.FileType, page_numbers : List[int]) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.WordJoinOptions` class.
        
        :param file_type: The type of the file to join.
        :param page_numbers: Page numbers.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_type : groupdocs.merger.domain.FileType, start_number : int, end_number : int) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.WordJoinOptions` class.
        
        :param file_type: The type of the file to join.
        :param start_number: The start page number.
        :param end_number: The end page number.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_type : groupdocs.merger.domain.FileType, start_number : int, end_number : int, mode : groupdocs.merger.domain.options.RangeMode) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.merger.domain.options.WordJoinOptions` class.
        
        :param file_type: The type of the file to join.
        :param start_number: The start page number.
        :param end_number: The end page number.
        :param mode: The range mode.'''
        raise NotImplementedError()
    
    @property
    def pages(self) -> List[int]:
        '''Get page numbers collection.'''
        raise NotImplementedError()
    
    @property
    def type(self) -> groupdocs.merger.domain.FileType:
        '''The type of the file to join.'''
        raise NotImplementedError()
    
    @property
    def mode(self) -> groupdocs.merger.domain.options.WordJoinMode:
        '''The Word join mode.'''
        raise NotImplementedError()
    
    @mode.setter
    def mode(self, value : groupdocs.merger.domain.options.WordJoinMode) -> None:
        '''The Word join mode.'''
        raise NotImplementedError()
    
    @property
    def compliance(self) -> groupdocs.merger.domain.options.WordJoinCompliance:
        '''Compliance mode for the Word Ooxml format'''
        raise NotImplementedError()
    
    @compliance.setter
    def compliance(self, value : groupdocs.merger.domain.options.WordJoinCompliance) -> None:
        '''Compliance mode for the Word Ooxml format'''
        raise NotImplementedError()
    

class ImageJoinMode:
    '''Possible modes for the image joining.'''
    
    HORIZONTAL : ImageJoinMode
    '''Specifies Horizontal image joining.'''
    VERTICAL : ImageJoinMode
    '''Specifies Vertical image joining.'''

class OrientationMode:
    '''Defines page orientation.'''
    
    PORTRAIT : OrientationMode
    '''Portrait page mode.'''
    LANDSCAPE : OrientationMode
    '''Landscape page mode.'''

class PdfSecurityPermissions:
    '''Defines PDF document permissions.'''
    
    ALLOW_ALL : PdfSecurityPermissions
    '''Allow printing, modification and data extraction.'''
    DENY_PRINTING : PdfSecurityPermissions
    '''Deny printing.'''
    DENY_MODIFICATION : PdfSecurityPermissions
    '''Deny content modification, filling in forms, adding or modifying annotations.'''
    DENY_DATA_EXTRACTION : PdfSecurityPermissions
    '''Deny text and graphics extraction.'''
    DENY_ALL : PdfSecurityPermissions
    '''Deny printing, content modification and data extraction.'''

class PreviewMode:
    '''Provides modes for the page previewing.'''
    
    PNG : PreviewMode
    '''Preview mode as .png'''
    JPEG : PreviewMode
    '''Preview mode as .jpeg'''
    BMP : PreviewMode
    '''Preview mode as .bmp'''

class RangeMode:
    '''Possible modes for the page ranging.'''
    
    ALL_PAGES : RangeMode
    '''Range have all numbers from begin to end.'''
    ODD_PAGES : RangeMode
    '''Range have only odd numbers from begin to end.'''
    EVEN_PAGES : RangeMode
    '''Range have only even numbers from begin to end.'''

class RotateMode:
    '''Possible modes for the page rotation.'''
    
    ROTATE90 : RotateMode
    '''Rotate to the right with 90 degrees.'''
    ROTATE180 : RotateMode
    '''Rotate to the right with 180 degrees.'''
    ROTATE270 : RotateMode
    '''Rotate to the right with 270 degrees.'''

class SplitMode:
    '''Defines page splitting modes.'''
    
    PAGES : SplitMode
    '''Split pages'''
    INTERVAL : SplitMode
    '''Split Intervals'''

class TextSplitMode:
    '''Possible text splitting modes.'''
    
    LINES : TextSplitMode
    '''Split lines'''
    INTERVAL : TextSplitMode
    '''Split Intervals'''

class WordJoinCompliance:
    '''Possible Compliance modes for the Word Ooxml formats such as .docx, .docm, .dotx, .dotm etc.'''
    
    AUTO : WordJoinCompliance
    '''Auto'''
    ECMA_376_2006 : WordJoinCompliance
    '''ECMA-376 1st Edition, 2006.'''
    ISO_29500_2008_TRANSITIONAL : WordJoinCompliance
    '''ISO/IEC 29500:2008 Transitional compliance level.'''
    ISO_29500_2008_STRICT : WordJoinCompliance
    '''ISO/IEC 29500:2008 Strict compliance level.'''

class WordJoinMode:
    '''Possible modes for the Word joining.'''
    
    DEFAULT : WordJoinMode
    '''Specifies Default Word joining.'''
    CONTINUOUS : WordJoinMode
    '''Specifies Word joining without starting from new page.'''
    DISABLE_SECTION_BREAKS : WordJoinMode
    '''Specifies Word joining without section breaks.'''

