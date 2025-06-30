from abc import ABC, abstractmethod
from dataclasses import dataclass
from fastapi import UploadFile


@dataclass()
class UploadFileOptions:
    allowed_types: list[str]
    max_size_bytes: int
    dir: str = ""


class StorageAdapter(ABC):
    @abstractmethod
    async def upload_file(self, file: UploadFile, options: UploadFileOptions) -> str:
        """uploads the file to storage and return the relative url"""
        pass

    @abstractmethod
    async def delete_file(self, file_url: str) -> None:
        """Takes the uploaded file url and deletes the file"""
        pass
