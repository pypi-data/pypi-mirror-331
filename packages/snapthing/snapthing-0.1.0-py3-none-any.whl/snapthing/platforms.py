# per-platform functions for code that is platform specific
from abc import ABC, abstractmethod

import subprocess
from io import BytesIO
from typing import override, Literal
from shutil import which


DependencyType = Literal["ocr", "clipboard"]


class Platform(ABC):
    """
    Abstract class for platform-specific functionality
    """

    def check_install(self) -> Exception | None:
        """Validate the installation of external dependencies."""
        return self.check_dependency("clipboard")

    @abstractmethod
    def check_dependency(self, dep: DependencyType) -> Exception | None:
        """Validate the installation of a specfic dependency."""

    @abstractmethod
    def copy_image_to_clipboard(self, image_data: BytesIO) -> None:
        """Copy image to system clipboard"""
        ...

    @abstractmethod
    def copy_text_to_clipboard(self, text: str) -> None:
        """Copy image to system clipboard"""
        ...

    @abstractmethod
    def extract_image_text_ocr(self, image_data: BytesIO) -> str:
        """Extract text from the image"""
        ...

    def assert_dependencies(self):
        error = self.check_install()
        if error is not None:
            raise error


class LinuxXClip(Platform):

    @override
    def check_dependency(self, dep: DependencyType) -> Exception | None:
        """Validate the installation of a specfic dependency."""
        if dep == "clipboard":
            xclip = which('xclip')
            if xclip is None:
                return RuntimeError("xclip is required in order to copy to clipboard")
        elif dep == "ocr":
            tesseract = which('tesseract')
            if tesseract is None:
                return RuntimeError("tesseract is required in order to use the OCR feature")


    @override
    def copy_image_to_clipboard(self, image_data: BytesIO) -> None:
        _ = subprocess.run(
            ['xclip', '-selection', 'clipboard', '-t', 'image/png'], 
            input=image_data.read(), text=False
        )

    @override
    def copy_text_to_clipboard(self, text: str) -> None:
        """Copy image to system clipboard"""
        _ = subprocess.run(
            ['xclip', '-selection', 'clipboard'], 
            input=text, text=True
        )

    @override
    def extract_image_text_ocr(self, image_data: BytesIO) -> str:
        """Extract text from the image"""
        output = subprocess.run(
            ['tesseract', '-', 'stdout'], 
            input=image_data.read(), text=False, stdout=subprocess.PIPE
        )
        return output.stdout.decode()
