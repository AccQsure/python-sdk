import os
import base64
import mimetypes
import aiofiles
from typing import List, TypedDict

from accqsure.enums import MIME_TYPE

# Keep MIME_TYPES list for backward compatibility and validation
MIME_TYPES: List[str] = [mime_type.value for mime_type in MIME_TYPE]


class DocumentContents(TypedDict):
    """Type definition for document contents prepared for upload.

    This structure is returned by Utilities.prepare_document_contents() and
    should be used for the 'contents' parameter in Document.create() and
    the 'draft' parameter in Inspection.create().
    """

    title: str
    type: MIME_TYPE
    base64_contents: str


class Utilities(object):
    """Utility functions for common SDK operations.

    This class provides static utility methods for operations like preparing
    document contents for upload.
    """

    @staticmethod
    async def prepare_document_contents(file_path: str) -> DocumentContents:
        """Prepare a document file for upload to the API.

        Reads a file from disk, validates its MIME type, and encodes it
        as base64. The file must be one of the supported document types.

        Args:
            file_path: Path to the document file to prepare. Can include
                '~' for home directory expansion.

        Returns:
            DocumentContents dictionary containing:
                - title: Filename without extension
                - type: MIME type of the file
                - base64_contents: Base64-encoded file contents

        Raises:
            ValueError: If the file type is not in the allowed MIME types.
            FileNotFoundError: If the file does not exist.
        """
        mime_type, _ = mimetypes.guess_type(file_path)

        if mime_type not in MIME_TYPES:
            raise ValueError(
                f"Invalid file type. Detected MIME type '{mime_type}' not in allowed types: {', '.join(MIME_TYPES)}"
            )

        async with aiofiles.open(os.path.expanduser(file_path), "rb") as f:
            value = await f.read()
            base64_contents = base64.b64encode(value).decode("utf-8")

        title = os.path.splitext(os.path.basename(file_path))[0]
        return {
            "title": title,
            "type": mime_type,
            "base64_contents": base64_contents,
        }
