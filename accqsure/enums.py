"""Enumerations for AccQsure SDK types.

This module defines enums for various types used throughout the SDK,
ensuring type safety and consistency.
"""

from enum import Enum


class MIME_TYPE(str, Enum):
    """Supported MIME types for document uploads.

    These are the allowed MIME types that can be used when uploading
    documents or content to the AccQsure API.
    """

    WORD_DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    EXCEL_XLSX = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    EXCEL_XLSM = "application/vnd.ms-excel.sheet.macroenabled.12"
    WORD_DOCM = "application/vnd.ms-word.document.macroenabled.12"
    TEXT_PLAIN = "text/plain"
    JSON = "application/json"
    CSV = "text/csv"
    MARKDOWN = "text/markdown"
    PDF = "application/pdf"


class INSPECTION_TYPE(str, Enum):
    """Inspection type enumeration.

    Defines the types of inspections that can be created.
    """

    PRELIMINARY = "preliminary"
    EFFECTIVE = "effective"


class CHART_SECTION_STYLE(str, Enum):
    """Chart section style enumeration.

    Defines the heading styles available for chart sections.
    """

    TITLE = "title"
    H1 = "h1"
    H2 = "h2"
    H3 = "h3"
    H4 = "h4"
    H5 = "h5"
    H6 = "h6"


class CHART_ELEMENT_TYPE(str, Enum):
    """Chart element type enumeration.

    Defines the types of elements that can be created in chart sections.
    """

    TITLE = "title"
    NARRATIVE = "narrative"
    TABLE = "table"
    STATIC = "static"
