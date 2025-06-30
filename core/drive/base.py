from typing import Annotated
from fastapi import Depends, UploadFile
from core.config import FileStorage, ConfigDepedency
from .abstracts import StorageAdapter, UploadFileOptions
from .storage_adapters import LocalStorageAdapters, S3StorageAdapters


class Drive:
    adapter: StorageAdapter

    def __init__(self, config: ConfigDepedency) -> None:
        if config.file_storage == FileStorage.LOCAL:
            self.adapter = LocalStorageAdapters(config=config)
        elif config.file_storage == FileStorage.S3:
            self.adapter = S3StorageAdapters()
        else:
            raise ValueError(
                "No Storage adapter configured. Did you forget to add config env variable?"
            )

    async def upload_file(self, file: UploadFile, options: UploadFileOptions) -> str:
        url = await self.adapter.upload_file(file, options=options)
        return url

    async def delete_file(self, file_url: str) -> None:
        await self.adapter.delete_file(file_url=file_url)


DriveDependency = Annotated[Drive, Depends()]
