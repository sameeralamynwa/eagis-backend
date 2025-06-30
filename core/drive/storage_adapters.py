from pathlib import Path
from fastapi import HTTPException, UploadFile
from core import get_config
from .abstracts import StorageAdapter, UploadFileOptions
import uuid


class LocalStorageAdapters(StorageAdapter):
    def __init__(self, config) -> None:
        self.config = config


    async def upload_file(self, file: UploadFile, options: UploadFileOptions) -> str:
        # Validate content type
        if file.content_type not in options.allowed_types:
            raise HTTPException(status_code=400, detail="Invalid file type")

        # Sanitize and generate a unique file name
        original_ext = Path(file.filename or "").suffix or ".bin"
        file_name = f"{uuid.uuid4().hex}{original_ext}"

        # Construct full storage path
        target_dir = Path(
            self.config.root_path,
            self.config.local_storage_path,
            options.dir or "",
        )

        target_dir.mkdir(parents=True, exist_ok=True)  # Ensure dir exists
        file_path = target_dir / file_name

        # Stream file to disk and validate size
        total_size = 0
        try:
            with open(file_path, "wb") as f:
                while chunk := await file.read(1024 * 1024):
                    total_size += len(chunk)
                    if total_size > options.max_size_bytes:
                        raise HTTPException(status_code=400, detail="File too large")
                    f.write(chunk)
        except (Exception, HTTPException) as e:
            # Remove partially written file
            if file_path.exists():
                file_path.unlink()

            if isinstance(e, HTTPException):
                raise e

            raise HTTPException(status_code=500, detail="File upload failed")

        # 5. Return public URL path
        url_path = "/".join(filter(None, [options.dir, file_name])).replace("\\", "/")
        return f"/{url_path}"

    async def delete_file(self, file_url: str) -> None:
        target_dir = Path(
            self.config.root_path,
            self.config.local_storage_path,
        )

        file_path = target_dir / file_url.lstrip("/")
        if file_path.exists():
            file_path.unlink()


class S3StorageAdapters(StorageAdapter):
    config = get_config()

    async def upload_file(self, file: UploadFile, options: UploadFileOptions) -> str:
        raise NotImplementedError("Adapter not implemented")

    async def delete_file(self, file_url: str) -> None:
        raise NotImplementedError("Adapter not implemented")
