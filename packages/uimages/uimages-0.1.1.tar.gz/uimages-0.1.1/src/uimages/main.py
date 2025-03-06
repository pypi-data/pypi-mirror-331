import logging
from pathlib import Path

from uimages.processor import FileProcessorFactory, PostProcessor, ImageProcessor


class ImageHelper:
    def __init__(self, content_dir: Path, image_dir: Path):
        self.content_dir = content_dir
        self.image_dir = image_dir
        self.check_results = {
            "invalid_references": {},  # {post_path: [image_path, ...]}
            "missing_titles": {},  # {post_path: [image_path, ...]}
            "unused_images": [],  # [image_path, ...]
            "image_usage_count": {},  # {image_path: count}
        }

        # Create processors using the factory
        self.post_processor: PostProcessor = FileProcessorFactory.create_processor(
            "post", self.content_dir
        )  # type: ignore
        self.image_processor: ImageProcessor = FileProcessorFactory.create_processor(
            "image", self.image_dir
        )  # type: ignore

    def run(self) -> None:
        """Run the entire process including extraction, checks, and updates."""
        self.post_processor.extract_image_references()
        self.image_processor.process_images()
        self.check_invalid_references()
        self.find_unreferenced_images()
        self.update_image_filenames_to_hash()

        # Output results
        self.output_results()

    def check_invalid_references(self) -> None:
        """Check for invalid image references and missing titles in posts."""
        for post_path_str, images in self.post_processor.posts_images.items():
            for img_alt, img_path in images:
                img_path_str = Path(img_path.lstrip("/")).as_posix()
                # Check if image exists
                if img_path_str not in self.image_processor.all_images:
                    if post_path_str not in self.check_results["invalid_references"]:
                        self.check_results["invalid_references"][post_path_str] = []
                    self.check_results["invalid_references"][post_path_str].append(
                        img_path
                    )

                # Check for missing title
                if not img_alt:
                    if post_path_str not in self.check_results["missing_titles"]:
                        self.check_results["missing_titles"][post_path_str] = []
                    self.check_results["missing_titles"][post_path_str].append(
                        (img_path, img_alt)
                    )

                # Count image usage
                if img_path_str in self.check_results["image_usage_count"]:
                    self.check_results["image_usage_count"][img_path_str] += 1
                else:
                    self.check_results["image_usage_count"][img_path_str] = 1

    def find_unreferenced_images(self) -> None:
        """Find images that are not referenced in any post."""
        used_images = {
            img_path_str
            for imgs in self.post_processor.posts_images.values()
            for _, img_path_str in imgs
        }
        for img_path_str in self.image_processor.all_images.keys():
            # path without slash
            if img_path_str not in used_images:
                self.check_results["unused_images"].append(img_path_str)

    def update_image_filenames_to_hash(self) -> None:
        """Rename image files to their hash values and update references in posts."""
        for img_path_str, img_hash in self.image_processor.all_images.items():
            img_path = Path(img_path_str)
            new_img_stem = f"{img_hash}"
            new_img_path = img_path.with_stem(new_img_stem)

            if img_path.stem == new_img_stem:
                continue

            # Rename the file
            img_path.rename(new_img_path)

            # Update references in posts
            self.update_image_references_in_posts(
                img_path.as_posix(), new_img_path.as_posix()
            )

    def update_image_references_in_posts(
        self, old_path: str | bytes, new_path: str | bytes
    ) -> None:
        """Update image references in posts when filenames are changed."""

        def get_lines(path):
            with open(path, "rb") as f:
                for line in f:
                    yield line

        def get_new_lines(path, old, new):
            for line in get_lines(path):
                if old in line:
                    new_line = line.replace(old, new)
                    print(new_line)
                    yield new_line
                else:
                    yield line

        old_path = old_path.encode() if type(old_path) is str else old_path
        new_path = new_path.encode() if type(new_path) is str else new_path
        for post in self.content_dir.glob("**/*.md"):
            with open(post, "r+b") as f:
                f.writelines(get_new_lines(post, old_path, new_path))

    def output_results(self) -> None:
        """Output the results of all checks and processes."""
        logging.info(
            f"Extract {sum((len(imgs) for imgs in self.post_processor.posts_images.values()))} images from {self.post_processor.post_count} posts in path {self.content_dir}"
        )
        logging.info(
            f"Get {self.image_processor.image_count} images in path {self.image_dir}"
        )

        def _output_invalid():
            data = self.check_results["invalid_references"]
            print(
                f"Invalid image references: {len(data)}",
            )
            if data:
                for post, img_paths in data.items():
                    print(f"    {post} : {img_paths}")

        def _output_untitle():
            data = self.check_results["missing_titles"]
            print(
                f"Images without titles: {len(data)}",
            )
            if data:
                for post, img_paths in data.items():
                    print(f"    {post} : {img_paths}")

        def _output_unused():
            data = self.check_results["unused_images"]
            print(
                f"Unreferenced images: {len(data)}",
            )
            if data:
                for img_path in data:
                    print(f"    {img_path}")

        def _output_usage(ref_count=1):
            print(
                f"Image usage count lt '{ref_count}': {sum([1 for count in self.check_results['image_usage_count'].values() if count > 1])}"
            )
            for img_path, count in self.check_results["image_usage_count"].items():
                if count > ref_count:
                    print(f"    {img_path} : {count} times")

        # _output_invalid()
        # _output_untitle()
        # _output_unused()
        # _output_usage()
        for f in locals().copy():
            if f.startswith("_output"):
                print(f'\n{"-" * 48}')
                locals().get(f)()
        print()

    def minify(self, tinify_key: str) -> None:
        import tinify

        to_minify = {
            img_path
            for img_path in self.image_processor.all_images.keys()
            if Path(img_path).suffix != ".webp"
        }
        logging.info(f"Images pending to be minified via tinypng: {len(to_minify)}")
        print("    " + "\n    ".join(to_minify))
        tinify.key = tinify_key

        for path in to_minify:
            new_path = Path(path).with_suffix(".webp").as_posix()
            if new_path not in self.image_processor.all_images.keys():
                source = tinify.from_file(path)
                converted = source.convert(type=["image/webp"])
                extension = converted.result().extension
                new_path = Path(path).with_suffix("." + extension).as_posix()
                converted.to_file(new_path)
                logging.info(f"minify {path} to {new_path}")
                self.update_image_references_in_posts(path, new_path)
            else:
                logging.info([f"{path} have been minified", "deleting it"])
                Path(path).unlink()  # TODO


if __name__ == "__main__":
    logging.basicConfig(
        format="%(levelname)s(%(funcName)s): %(message)s", level=logging.INFO
    )

    content_dir = Path("content/posts")
    image_dir = Path("images")
    tinify_token = ""

    helper = ImageHelper(content_dir, image_dir)
    helper.run()
    helper.minify(tinify_token)
