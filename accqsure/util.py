import os
import base64
import mimetypes
import aiofiles

MIME_TYPES = [
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel.sheet.macroenabled.12",
    "application/vnd.ms-word.document.macroenabled.12",
    "text/plain",
    "application/json",
    "text/csv",
    "text/markdown",
    "application/pdf",
]


class Utilities(object):
    @staticmethod
    async def prepare_document_contents(file_path: str):
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
