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

class FileType:
    '''Represents file type. Provides methods to obtain list of all file types supported by **GroupDocs.Merger**,
    detect file type by extension etc.'''
    
    @staticmethod
    def from_extension(extension : str) -> groupdocs.merger.domain.FileType:
        '''Maps file extension to file type.
        
        :param extension: File extension (including the period ".").
        :returns: When file type is supported returns it, otherwise returns default :py:attr:`groupdocs.merger.domain.FileType.UNKNOWN` file type.'''
        raise NotImplementedError()
    
    @staticmethod
    def get_supported_file_types() -> Iterable[groupdocs.merger.domain.FileType]:
        '''Retrieves supported file types
        
        :returns: Returns sequence of supported file types'''
        raise NotImplementedError()
    
    def equals(self, other : groupdocs.merger.domain.FileType) -> bool:
        '''Determines whether the current :py:class:`groupdocs.merger.domain.FileType` is the same as specified :py:class:`groupdocs.merger.domain.FileType` object.
        
        :param other: The object to compare with the current :py:class:`groupdocs.merger.domain.FileType` object.
        :returns: true
        if both :py:class:`groupdocs.merger.domain.FileType` objects are the same; otherwise,     false'''
        raise NotImplementedError()
    
    @staticmethod
    def is_text(file_type : groupdocs.merger.domain.FileType) -> bool:
        '''Determines whether input :py:class:`groupdocs.merger.domain.FileType` is primitive text format.
        
        :param file_type: The :py:class:`groupdocs.merger.domain.FileType` object.
        :returns: true
        if input :py:class:`groupdocs.merger.domain.FileType` is primitive text format; otherwise,     false'''
        raise NotImplementedError()
    
    @staticmethod
    def is_archive(file_type : groupdocs.merger.domain.FileType) -> bool:
        '''Determines whether input :py:class:`groupdocs.merger.domain.FileType` is archive format.
        
        :param file_type: The :py:class:`groupdocs.merger.domain.FileType` object.
        :returns: true
        if input :py:class:`groupdocs.merger.domain.FileType` is archive format; otherwise,     false'''
        raise NotImplementedError()
    
    @staticmethod
    def is_image(file_type : groupdocs.merger.domain.FileType) -> bool:
        '''Determines whether input :py:class:`groupdocs.merger.domain.FileType` is image format.
        
        :param file_type: The :py:class:`groupdocs.merger.domain.FileType` object.
        :returns: true
        if input :py:class:`groupdocs.merger.domain.FileType` is image format; otherwise,     false'''
        raise NotImplementedError()
    
    @staticmethod
    def is_audio(file_type : groupdocs.merger.domain.FileType) -> bool:
        '''Determines whether input :py:class:`groupdocs.merger.domain.FileType` is audio format.
        
        :param file_type: The :py:class:`groupdocs.merger.domain.FileType` object.
        :returns: true
        if input :py:class:`groupdocs.merger.domain.FileType` is audio format; otherwise,     false'''
        raise NotImplementedError()
    
    @property
    def file_format(self) -> str:
        '''File type name e.g. "Microsoft Word Document".'''
        raise NotImplementedError()
    
    @property
    def extension(self) -> str:
        '''Filename suffix (including the period ".") e.g. ".doc".'''
        raise NotImplementedError()
    
    @property
    def UNKNOWN(self) -> groupdocs.merger.domain.FileType:
        '''Represents unknown file type.'''
        raise NotImplementedError()

    @property
    def ZIP(self) -> groupdocs.merger.domain.FileType:
        '''Zipped File (.zip)'''
        raise NotImplementedError()

    @property
    def GZ(self) -> groupdocs.merger.domain.FileType:
        '''G-Zip Compressed File (.gz)'''
        raise NotImplementedError()

    @property
    def SEVEN_Z(self) -> groupdocs.merger.domain.FileType:
        '''7-Zip Compressed File (.7z)'''
        raise NotImplementedError()

    @property
    def TAR(self) -> groupdocs.merger.domain.FileType:
        '''Consolidated Unix File Archive (.tar)'''
        raise NotImplementedError()

    @property
    def RAR(self) -> groupdocs.merger.domain.FileType:
        '''Roshal ARchive Compressed File (.rar)'''
        raise NotImplementedError()

    @property
    def BZ2(self) -> groupdocs.merger.domain.FileType:
        '''Bzip2 Compressed File (.bz2)'''
        raise NotImplementedError()

    @property
    def VST(self) -> groupdocs.merger.domain.FileType:
        '''Visio Drawing Template (.vst)'''
        raise NotImplementedError()

    @property
    def VSS(self) -> groupdocs.merger.domain.FileType:
        '''Visio Stencil File(.vss)'''
        raise NotImplementedError()

    @property
    def VSD(self) -> groupdocs.merger.domain.FileType:
        '''Visio Drawing File (.vsd)'''
        raise NotImplementedError()

    @property
    def VSSX(self) -> groupdocs.merger.domain.FileType:
        '''Visio Stencil File (.vssx) are drawing stencils created with Microsoft Visio 2013 and above. The VSSX file format can be opened with Visio 2013 and above. Visio files are known for representation of a variety of drawing elements such as collection of shapes, connectors, flowcharts, network layout, UML diagrams,
        Learn more about this file format `here <https://docs.fileformat.com/image/vssx>`.'''
        raise NotImplementedError()

    @property
    def VSDX(self) -> groupdocs.merger.domain.FileType:
        '''Visio Drawing (.vsdx) represents Microsoft Visio file format introduced from Microsoft Office 2013 onwards. It was developed to replace the binary file format, .VSD, which is supported by earlier versions of Microsoft Visio.
        Learn more about this file format `here <https://docs.fileformat.com/image/vsdx>`.'''
        raise NotImplementedError()

    @property
    def VSDM(self) -> groupdocs.merger.domain.FileType:
        '''Visio Macro-Enabled Drawing (.vsdm) are drawing files created with Microsoft Visio application that supports macros. VSDM files are OPC/XML drawings that are similar to VSDX, but also provide the capability to run macros when the file is opened.
        Learn more about this file format `here <https://docs.fileformat.com/image/vsdm>`.'''
        raise NotImplementedError()

    @property
    def VSTX(self) -> groupdocs.merger.domain.FileType:
        '''Visio Drawing Template (.vstx) are drawing template files created with Microsoft Visio 2013 and above. These VSTX files provide starting point for creating Visio drawings, saved as .VSDX files, with default layout and settings.
        Learn more about this file format `here <https://docs.fileformat.com/image/vstx>`.'''
        raise NotImplementedError()

    @property
    def VSTM(self) -> groupdocs.merger.domain.FileType:
        '''Visio Macro-Enabled Drawing Template (.vstm) are template files created with Microsoft Visio that support macros. Unlike VSDX files, files created from VSTM templates can run macros that are developed in Visual Basic for Applications (VBA)  code.
        Learn more about this file format `here <https://docs.fileformat.com/image/vstm>`.'''
        raise NotImplementedError()

    @property
    def VSSM(self) -> groupdocs.merger.domain.FileType:
        '''Visio Macro-Enabled Stencil File (.vssm) are Microsoft Visio Stencil files that support provide support for macros. A VSSM file when opened allows to run the macros to achieve desired formatting and placement of shapes in a diagram.
        Learn more about this file format `here <https://docs.fileformat.com/image/vssm>`.'''
        raise NotImplementedError()

    @property
    def VSX(self) -> groupdocs.merger.domain.FileType:
        '''Visio Stencil XML File (.vsx) refers to stencils that consist of drawings and shapes that are used for creating diagrams in Microsoft Visio. VSX files are saved in XML file format and was supported till Visio 2013.
        Learn more about this file format `here <https://docs.fileformat.com/image/vsx>`.'''
        raise NotImplementedError()

    @property
    def VTX(self) -> groupdocs.merger.domain.FileType:
        '''Visio Template XML File (.vtx) is a Microsoft Visio drawing template that is saved to disc in XML file format. The template is aimed to provide a file with basic settings that can be used to create multiple Visio files of the same settings.
        Learn more about this file format `here <https://docs.fileformat.com/image/vtx>`.'''
        raise NotImplementedError()

    @property
    def VDX(self) -> groupdocs.merger.domain.FileType:
        '''Visio Drawing XML File (.vdx)is a drawing or chart created in Microsoft Visio, but saved in XML format have .VDX extension. A Visio drawing XML file is created in Visio software, which is developed by Microsoft.
        Learn more about this file format `here <https://docs.fileformat.com/image/vdx>`.'''
        raise NotImplementedError()

    @property
    def EPUB(self) -> groupdocs.merger.domain.FileType:
        '''Open eBook File (.epub) are an e-book file format that provide a standard digital publication format for publishers and consumers. The format has been so common by now that it is supported by many e-readers and software applications.
        Learn more about this file format `here <https://docs.fileformat.com/ebook/epub>`.'''
        raise NotImplementedError()

    @property
    def BMP(self) -> groupdocs.merger.domain.FileType:
        '''Bitmap Image File (.bmp) represent files that are used to store bitmap digital images. Learn more about this file format `here <https://docs.fileformat.com/image/bmp>`.'''
        raise NotImplementedError()

    @property
    def JPG(self) -> groupdocs.merger.domain.FileType:
        '''JPEG Image (.jpg)'''
        raise NotImplementedError()

    @property
    def JPEG(self) -> groupdocs.merger.domain.FileType:
        '''JPEG Image (.jpeg) is a type of image format that is saved using the method of lossy compression. The output image, as result of compression, is a trade-off between storage size and image quality.
        Learn more about this file format `here <https://docs.fileformat.com/image/jpeg>`.'''
        raise NotImplementedError()

    @property
    def PNG(self) -> groupdocs.merger.domain.FileType:
        '''Portable Network Graphic (.png) is a type of raster image file format that use loseless compression.
        Learn more about this file format `here <https://docs.fileformat.com/image/png>`.'''
        raise NotImplementedError()

    @property
    def PS(self) -> groupdocs.merger.domain.FileType:
        '''PostScript File (.ps)'''
        raise NotImplementedError()

    @property
    def TIF(self) -> groupdocs.merger.domain.FileType:
        '''Tagged Image File (.tif)'''
        raise NotImplementedError()

    @property
    def TIFF(self) -> groupdocs.merger.domain.FileType:
        '''Tagged Image File Format (.tiff)'''
        raise NotImplementedError()

    @property
    def GIF(self) -> groupdocs.merger.domain.FileType:
        '''Graphical Interchange Format File (.gif)'''
        raise NotImplementedError()

    @property
    def SVG(self) -> groupdocs.merger.domain.FileType:
        '''Scalable Vector Graphics File (.svg)'''
        raise NotImplementedError()

    @property
    def SVGZ(self) -> groupdocs.merger.domain.FileType:
        '''Scalable Vector Graphics Compressed File (.svgz)'''
        raise NotImplementedError()

    @property
    def EMF(self) -> groupdocs.merger.domain.FileType:
        '''Windows Enhanced Metafile (.emf)'''
        raise NotImplementedError()

    @property
    def EMZ(self) -> groupdocs.merger.domain.FileType:
        '''Windows Compressed Enhanced Metafile (.emz)'''
        raise NotImplementedError()

    @property
    def HTML(self) -> groupdocs.merger.domain.FileType:
        '''Hypertext Markup Language File (.html) is the extension for web pages created for display in browsers.
        Learn more about this file format `here <https://docs.fileformat.com/web/html>`.'''
        raise NotImplementedError()

    @property
    def MHT(self) -> groupdocs.merger.domain.FileType:
        '''MHTML Web Archive (.mht) is a web page archive format that can be created by a number of different applications.
        Learn more about this file format `here <https://docs.fileformat.com/web/mhtml>`.'''
        raise NotImplementedError()

    @property
    def MHTML(self) -> groupdocs.merger.domain.FileType:
        '''MIME HTML File (.mhtml) is a web page archive format that can be created by a number of different applications.
        Learn more about this file format `here <https://docs.fileformat.com/web/mhtml>`.'''
        raise NotImplementedError()

    @property
    def ONE(self) -> groupdocs.merger.domain.FileType:
        '''OneNote Document (.one) files are created by Microsoft OneNote application. OneNote lets you gather information using the application as if you are using your draftpad for taking notes.
        Learn more about this file format `here <https://docs.fileformat.com/note-taking/one>`.'''
        raise NotImplementedError()

    @property
    def PDF(self) -> groupdocs.merger.domain.FileType:
        '''Portable Document Format File (.pdf) isa file format that was to introduced as a standard for representation of documents and other reference material in a format that is independent of application software, hardware as well as Operating System.
        Learn more about this file format `here <https://docs.fileformat.com/view/pdf>`.'''
        raise NotImplementedError()

    @property
    def XPS(self) -> groupdocs.merger.domain.FileType:
        '''XML Paper Specification File (.xps) represents page layout files that are based on XML Paper Specifications created by Microsoft.
        Learn more about this file format `here <https://docs.fileformat.com/page-description-language/xps>`.'''
        raise NotImplementedError()

    @property
    def TEX(self) -> groupdocs.merger.domain.FileType:
        '''LaTeX Source Document (.tex) is a language that comprises of programming as well as mark-up features, used to typeset documents.
        Learn more about this file format `here <https://docs.fileformat.com/page-description-language/tex>`.'''
        raise NotImplementedError()

    @property
    def PPT(self) -> groupdocs.merger.domain.FileType:
        '''PowerPoint Presentation (.ppt) represents PowerPoint file that consists of a collection of slides for displaying as SlideShow. It specifies the Binary File Format used by Microsoft PowerPoint 97-2003.
        Learn more about this file format `here <https://docs.fileformat.com/presentation/ppt>`.'''
        raise NotImplementedError()

    @property
    def PPTX(self) -> groupdocs.merger.domain.FileType:
        '''PowerPoint Open XML Presentation (.pptx) is a presentation file created with popular Microsoft PowerPoint application. Unlike the previous version of presentation file format PPT which was binary, the PPTX format is based on the Microsoft PowerPoint open XML presentation file format.
        Learn more about this file format `here <https://docs.fileformat.com/presentation/pptx>`.'''
        raise NotImplementedError()

    @property
    def PPS(self) -> groupdocs.merger.domain.FileType:
        '''PowerPoint Slide Show (.pps) is a file created using Microsoft PowerPoint for Slide Show purpose. PPS file reading and creation is supported by Microsoft PowerPoint 97-2003.
        Learn more about this file format `here <https://docs.fileformat.com/presentation/pps>`.'''
        raise NotImplementedError()

    @property
    def PPSX(self) -> groupdocs.merger.domain.FileType:
        '''PowerPoint Open XML Slide Show (.ppsx) is a file created using Microsoft PowerPoint 2007 and above for Slide Show purpose.
        Learn more about this file format `here <https://docs.fileformat.com/presentation/ppsx>`.'''
        raise NotImplementedError()

    @property
    def ODP(self) -> groupdocs.merger.domain.FileType:
        '''OpenDocument Presentation (.odp) represents presentation file format used by OpenOffice.org in the OASISOpen standard.
        Learn more about this file format `here <https://docs.fileformat.com/presentation/odp>`.'''
        raise NotImplementedError()

    @property
    def OTP(self) -> groupdocs.merger.domain.FileType:
        '''OpenDocument Presentation Template (.otp) represents presentation template files created by applications in OASIS OpenDocument standard format.
        Learn more about this file format `here <https://docs.fileformat.com/presentation/otp>`.'''
        raise NotImplementedError()

    @property
    def PPTM(self) -> groupdocs.merger.domain.FileType:
        '''PowerPoint Open XML Macro-Enabled Presentation'''
        raise NotImplementedError()

    @property
    def PPSM(self) -> groupdocs.merger.domain.FileType:
        '''PowerPoint Open XML Macro-Enabled Slide (.ppsm)'''
        raise NotImplementedError()

    @property
    def XLS(self) -> groupdocs.merger.domain.FileType:
        '''Excel Spreadsheet (.xls) is a file that can be created by Microsoft Excel as well as other similar spreadsheet programs such as OpenOffice Calc or Apple Numbers.
        Learn more about this file format `here <https://docs.fileformat.com/spreadsheet/xls>`.'''
        raise NotImplementedError()

    @property
    def XLSX(self) -> groupdocs.merger.domain.FileType:
        '''Microsoft Excel Open XML Spreadsheet (.xlsx) is a well-known format for Microsoft Excel documents that was introduced by Microsoft with the release of Microsoft Office 2007.
        Learn more about this file format `here <https://docs.fileformat.com/spreadsheet/xlsx>`.'''
        raise NotImplementedError()

    @property
    def XLSM(self) -> groupdocs.merger.domain.FileType:
        '''Excel Open XML Macro-Enabled Spreadsheet (.xlsm) is a type of Spreasheet files that support macros.
        Learn more about this file format `here <https://docs.fileformat.com/spreadsheet/xlsm>`.'''
        raise NotImplementedError()

    @property
    def XLSB(self) -> groupdocs.merger.domain.FileType:
        '''Excel Binary Spreadsheet (.xlsb) file format specifies the Excel Binary File Format, which is a collection of records and structures that specify Excel workbook content.
        Learn more about this file format `here <https://docs.fileformat.com/spreadsheet/xlsb>`.'''
        raise NotImplementedError()

    @property
    def CSV(self) -> groupdocs.merger.domain.FileType:
        '''Comma Separated Values File (.csv) represents plain text files that contain records of data with comma separated values.
        Learn more about this file format `here <https://docs.fileformat.com/spreadsheet/csv>`.'''
        raise NotImplementedError()

    @property
    def TSV(self) -> groupdocs.merger.domain.FileType:
        '''Tab Separated Values File (.tsv) represents data separated with tabs in plain text format.
        Learn more about this file format `here <https://docs.fileformat.com/spreadsheet/tsv>`.'''
        raise NotImplementedError()

    @property
    def ODS(self) -> groupdocs.merger.domain.FileType:
        '''OpenDocument Spreadsheet (.ods)
        Learn more about this file format `here <https://docs.fileformat.com/spreadsheet/ods>`.'''
        raise NotImplementedError()

    @property
    def XLTM(self) -> groupdocs.merger.domain.FileType:
        '''Excel Open XML Macro-Enabled Spreadsheet Template (.xltm) represents files that are generated by Microsoft Excel as Macro-enabled template files. XLTM files are similar to XLTX in structure other than that the later doesn\'t support creating template files with macros.
        Learn more about this file format `here <https://docs.fileformat.com/spreadsheet/xltm>`.'''
        raise NotImplementedError()

    @property
    def XLTX(self) -> groupdocs.merger.domain.FileType:
        '''Excel Open XML Spreadsheet Template (.xltx) files are based on the Office OpenXML file format specifications. It is used to create a standard template file that can be utilized to generate XLSX files that exhibit the same settings as specified in the XLTX file.
        Learn more about this file format `here <https://docs.fileformat.com/spreadsheet/xltx>`.'''
        raise NotImplementedError()

    @property
    def XLT(self) -> groupdocs.merger.domain.FileType:
        '''Excel Template File (.xlt) are template files created with Microsoft Excel which is a spreadsheet application which comes as part of Microsoft Office suite.  Microsoft Office 97-2003 supported creating new XLT files as well as opening these.
        Learn more about this file format `here <https://docs.fileformat.com/spreadsheet/xlt>`.'''
        raise NotImplementedError()

    @property
    def XLAM(self) -> groupdocs.merger.domain.FileType:
        '''Excel Macro-Enabled Add-In (.xlam)'''
        raise NotImplementedError()

    @property
    def DOC(self) -> groupdocs.merger.domain.FileType:
        '''Microsoft Word Document (.doc) represent documents generated by Microsoft Word or other word processing documents in binary file format.
        Learn more about this file format `here <https://docs.fileformat.com/word-processing/doc>`.'''
        raise NotImplementedError()

    @property
    def DOCX(self) -> groupdocs.merger.domain.FileType:
        '''Microsoft Word Open XML Document (.docx) is a well-known format for Microsoft Word documents. Introduced from 2007 with the release of Microsoft Office 2007, the structure of this new Document format was changed from plain binary to a combination of XML and binary files.
        Learn more about this file format `here <https://docs.fileformat.com/word-processing/docx>`.'''
        raise NotImplementedError()

    @property
    def DOCM(self) -> groupdocs.merger.domain.FileType:
        '''Word Open XML Macro-Enabled Document (.docm) files are Microsoft Word 2007 or higher generated documents with the ability to run macros.
        Learn more about this file format `here <https://docs.fileformat.com/word-processing/docm>`.'''
        raise NotImplementedError()

    @property
    def DOT(self) -> groupdocs.merger.domain.FileType:
        '''Word Document Template (.dot) files are template files created by Microsoft Word to have pre-formatted settings for generation of further DOC or DOCX files.
        Learn more about this file format `here <https://docs.fileformat.com/word-processing/dot>`.'''
        raise NotImplementedError()

    @property
    def DOTX(self) -> groupdocs.merger.domain.FileType:
        '''Word Open XML Document Template (.dotx) are template files created by Microsoft Word to have pre-formatted settings for generation of further DOCX files.
        Learn more about this file format `here <https://docs.fileformat.com/word-processing/dotx>`.'''
        raise NotImplementedError()

    @property
    def DOTM(self) -> groupdocs.merger.domain.FileType:
        '''Word Open XML Macro-Enabled Document Template (.dotm) represents template file created with Microsoft Word 2007 or higher.
        Learn more about this file format `here <https://docs.fileformat.com/word-processing/dotm>`.'''
        raise NotImplementedError()

    @property
    def RTF(self) -> groupdocs.merger.domain.FileType:
        '''Rich Text Format File (.rtf) introduced and documented by Microsoft, the Rich Text Format (RTF) represents a method of encoding formatted text and graphics for use within applications.
        Learn more about this file format `here <https://docs.fileformat.com/word-processing/rtf>`.'''
        raise NotImplementedError()

    @property
    def TXT(self) -> groupdocs.merger.domain.FileType:
        '''Plain Text File (.txt) represents a text document that contains plain text in the form of lines.
        Learn more about this file format `here <https://docs.fileformat.com/word-processing/txt>`.'''
        raise NotImplementedError()

    @property
    def ERR(self) -> groupdocs.merger.domain.FileType:
        '''Error Log File (.err) is a text file that contains error messages generated by a program.
        Learn more about this file format `here <https://fileinfo.com/extension/err>`.'''
        raise NotImplementedError()

    @property
    def ODT(self) -> groupdocs.merger.domain.FileType:
        '''OpenDocument Text Document (.odt) files are type of documents created with word processing applications that are based on OpenDocument Text File format.
        Learn more about this file format `here <https://docs.fileformat.com/word-processing/odt>`.'''
        raise NotImplementedError()

    @property
    def OTT(self) -> groupdocs.merger.domain.FileType:
        '''OpenDocument Document Template (.ott) represent template documents generated by applications in compliance with the OASIS\' OpenDocument standard format.
        Learn more about this file format `here <https://docs.fileformat.com/word-processing/ott>`.'''
        raise NotImplementedError()

    @property
    def WAV(self) -> groupdocs.merger.domain.FileType:
        '''WAV, known for WAVE (Waveform Audio File Format), is a subset of Microsoft’s Resource Interchange File Format (RIFF) specification for storing digital audio files. The format doesn’t apply any compression to the bitstream and stores the audio recordings with different sampling rates and bitrates. It has been and is one of the standard format for audio CDs.
        Learn more about this file format `here <https://docs.fileformat.com/audio/wav>`.'''
        raise NotImplementedError()

    @property
    def MP3(self) -> groupdocs.merger.domain.FileType:
        '''Files with .mp3 extension are digitally encoded file formats for audio files that are formally based on the MPEG-1 Audio Layer III or MPEG-2 Audio Layer III. It was developed by the Moving Picture Experts Group (MPEG) that uses Layer 3 audio compression. Compression achieved by MP3 file format is 1/10th the size of .WAV or .AIF files.
        Learn more about this file format `here <https://docs.fileformat.com/audio/mp3>`.'''
        raise NotImplementedError()


