# -*- coding: utf-8 -*-

import typing
from io import BytesIO

from PyPDF2 import PdfFileReader
from PyPDF2 import PdfFileWriter

from preview_generator import file_converter
from preview_generator.preview.generic_preview import PreviewBuilder
from preview_generator.utils import ImgDims
from preview_generator.preview.builder.image__wand import convert_pdf_to_jpeg


class PdfPreviewBuilderPyPDF2(PreviewBuilder):
    mimetype = [
        'application/pdf',
        'application/postscript'
    ]

    def build_jpeg_preview(self, file_path: str, preview_name: str,
                           cache_path: str, page_id: int,
                           extension: str = '.jpg',
                           size: ImgDims=None) -> None:
        """
        generate the pdf small preview
        """
        if not size:
            size = ImgDims(256, 256)

        with open(file_path, 'rb') as pdf:
            input_pdf = PdfFileReader(pdf)
            output_pdf = PdfFileWriter()
            output_pdf.addPage(input_pdf.getPage(int(page_id)))
            output_stream = BytesIO()
            output_pdf.write(output_stream)
            output_stream.seek(0, 0)
            result = convert_pdf_to_jpeg(output_stream, size)

            if page_id == -1:
                preview_path = '{path}{file_name}{extension}'.format(
                    file_name=preview_name,
                    path=cache_path,
                    extension=extension
                )
            else:
                preview_path = '{path}{file_name}{extension}'.format(
                    file_name=preview_name,
                    path=cache_path,
                    page_id=page_id,
                    extension=extension
                )
            with open(preview_path, 'wb') as jpeg:
                buffer = result.read(1024)
                while buffer:
                    jpeg.write(buffer)
                    buffer = result.read(1024)

    def build_pdf_preview(self, file_path: str, preview_name: str,
                          cache_path: str, extension: str = '.pdf',
                          page_id: int = -1) -> None:
        """
        generate the pdf large preview
        """

        with open(file_path, 'rb') as pdf:

            input_pdf = PdfFileReader(pdf)
            output_pdf = PdfFileWriter()
            if page_id is None or page_id <= -1:
                for i in range(input_pdf.numPages):
                    output_pdf.addPage(input_pdf.getPage(i))
            else:
                output_pdf.addPage(input_pdf.getPage(int(page_id)))
            output_stream = BytesIO()
            output_pdf.write(output_stream)
            output_stream.seek(0, 0)

            preview_path = '{path}{file_name}{extension}'.format(
                file_name=preview_name,
                path=cache_path,
                extension=extension
            )

            with open(preview_path, 'wb') as jpeg:
                buffer = output_stream.read(1024)
                while buffer:
                    jpeg.write(buffer)
                    buffer = output_stream.read(1024)

    def get_page_number(self, file_path: str, preview_name: str,
                        cache_path: str) -> int:
        with open(cache_path + preview_name + '_page_nb', 'w') as count:
            count.seek(0, 0)

            with open(file_path, 'rb') as doc:
                inputpdf = PdfFileReader(doc)
                count.write(str(inputpdf.numPages))
        with open(cache_path + preview_name + '_page_nb', 'r') as count:
            count.seek(0, 0)
            return count.read()

    def get_original_size(self, file_path: str, page_id: int=-1) -> typing.Tuple[int, int]:  # nopep8
        # FIXME use ImgDims instead of Tuple
        if not page_id or page_id <= -1:
            page_id = 0
        with open(file_path, 'rb') as pdf:
            size = file_converter.get_pdf_size(pdf, page_id)
            return size