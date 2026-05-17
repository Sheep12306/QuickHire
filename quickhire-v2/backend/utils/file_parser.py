import io
from typing import Optional
from pathlib import Path

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


class FileParseError(Exception):
    pass


def read_txt_file(file_content: bytes) -> str:
    try:
        return file_content.decode('utf-8')
    except UnicodeDecodeError:
        try:
            return file_content.decode('gbk')
        except UnicodeDecodeError:
            return file_content.decode('utf-8', errors='ignore')


def read_md_file(file_content: bytes) -> str:
    """Parse Markdown file — treat as plain text, strip excessive markdown syntax."""
    text = read_txt_file(file_content)
    return text


def read_docx_file(file_content: bytes) -> str:
    if not DOCX_AVAILABLE:
        raise FileParseError("python-docx库未安装，无法解析DOCX文件")

    try:
        doc = docx.Document(io.BytesIO(file_content))
        paragraphs = []
        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append(para.text)
        return "\n".join(paragraphs)
    except Exception as e:
        raise FileParseError(f"DOCX文件解析失败: {str(e)}")


def read_pdf_file(file_content: bytes) -> str:
    if not PDF_AVAILABLE:
        raise FileParseError("PyPDF2库未安装，无法解析PDF文件")

    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text_parts = []

        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            if text.strip():
                text_parts.append(text)

        return "\n".join(text_parts)
    except Exception as e:
        raise FileParseError(f"PDF文件解析失败: {str(e)}")


def parse_uploaded_file(filename: str, file_content: bytes) -> str:
    file_extension = Path(filename).suffix.lower()

    if file_extension == '.txt':
        return read_txt_file(file_content)
    elif file_extension == '.md':
        return read_md_file(file_content)
    elif file_extension == '.docx':
        return read_docx_file(file_content)
    elif file_extension == '.pdf':
        return read_pdf_file(file_content)
    elif file_extension in ['.doc', '.rtf']:
        raise FileParseError(f"暂不支持{file_extension}格式，请转换为TXT、MD、DOCX或PDF格式")
    else:
        raise FileParseError(f"不支持的文件格式: {file_extension}")


def get_supported_formats() -> list:
    formats = ['txt', 'md']
    if DOCX_AVAILABLE:
        formats.append('docx')
    if PDF_AVAILABLE:
        formats.append('pdf')
    return formats