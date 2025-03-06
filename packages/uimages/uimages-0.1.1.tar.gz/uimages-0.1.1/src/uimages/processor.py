import hashlib
import logging
import re
from pathlib import Path
from typing import Generator, TypedDict, Dict, List


class FileProcessorFactory:
    @staticmethod
    def create_processor(file_type: str, base_path: Path):
        if file_type == "post":
            return PostProcessor(base_path)
        elif file_type == "image":
            return ImageProcessor(base_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")


class BaseProcessor:
    def __init__(self, base_path: Path):
        self.base_path = base_path

    def get_files(self) -> Generator[Path, None, None]:
        """Generator to yield all files in the base path."""
        for file in self.base_path.glob("**/*"):
            if file.is_file():
                yield file


class ImgInMd(TypedDict):
    img_alt: str
    img_path: str


class PostProcessor(BaseProcessor):
    markdownImage_pattern = re.compile(r"!\[(.*?)\]\((.*?)\)")

    def __init__(self, base_path: Path):
        super().__init__(base_path)
        self.post_count = 0
        self.posts_images: Dict[str, List[tuple[str | None, str | None]]] = (
            {}
        )  # {post_path: [(image_alt, image_path)]}

    def extract_image_references(self) -> None:
        """Extract image references from all posts and build a mapping."""
        md_image_pattern = self.markdownImage_pattern
        for post in self.get_files():
            self.post_count += 1
            images_in_post = []
            with post.open("r", encoding="utf-8") as f:
                logging.debug(f"reading {post.as_posix()}")
                while line := f.readline():
                    for match in md_image_pattern.finditer(line):
                        img_alt, img_path = match.groups()
                        images_in_post.append(
                            tuple(
                                (
                                    img_alt.strip(),
                                    Path(img_path.strip().lstrip("/")).as_posix(),
                                )
                            )
                        )
            self.posts_images[post.as_posix()] = images_in_post


class ImageProcessor(BaseProcessor):
    def __init__(self, base_path: Path):
        super().__init__(base_path)
        self.image_count = 0
        self.all_images: Dict[str, str] = {}  # {image_path: hash}

    @staticmethod
    def get_hash_hex(path: Path) -> str:
        """Calculate image hash using SHA256."""
        hasher = hashlib.sha256()
        with path.open("rb") as fp:
            while block := fp.read(4096):
                hasher.update(block)
        return hasher.hexdigest()

    def process_images(self) -> None:
        """Traverse images, hash their content, and map to the hash."""

        for image_path in self.get_files():
            self.image_count += 1
            image_hash = (
                self.get_hash_hex(image_path)
                if len(image_path.stem) <= 64
                else image_path.stem
            )
            self.all_images[image_path.as_posix()] = image_hash
