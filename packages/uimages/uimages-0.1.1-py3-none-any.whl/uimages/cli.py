import argparse
import logging
from os import getenv
from pathlib import Path

from uimages.main import ImageHelper


class UimagesArgs(argparse.Namespace):
    content_dir: Path
    image_dir: Path
    tinify_token: str
    minify: bool
    verbose: bool


def cli():
    parser = argparse.ArgumentParser(
        prog="Uimages", description="An Images helper for markdown."
    )

    parser.add_argument(
        "-c",
        "--content-dir",
        type=Path,
        required=True,
        help="the dir that contains the markdown files.",
    )
    parser.add_argument(
        "-i",
        "--image-dir",
        type=Path,
        required=True,
        help="the dir that contains the image files.",
    )
    parser.add_argument(
        "-m",
        "--minify",
        action="store_true",
        help="minify non-webp images to webp.",
    )
    parser.add_argument(
        "-t",
        "--tinify-token",
        type=str,
        default=getenv("TINIFY_TOKEN"),
        help="the token of your tinify.com API.",
    )
    parser.add_argument(
        "-V",
        "--verbose",
        action="store_true",
        help="enable verbose log.",
    )
    args: UimagesArgs = parser.parse_args(namespace=UimagesArgs())

    print()
    print("====== Uimages CLI ======")
    print(args)
    print()

    logging.basicConfig(
        format="%(levelname)s(%(funcName)s): %(message)s",
        level=logging.DEBUG if args.verbose else logging.INFO,
    )

    content_dir = args.content_dir
    image_dir = args.image_dir
    tinify_token = args.tinify_token

    if not (content_dir.exists() and image_dir.exists()):
        raise Exception("Content dir or image dir does not exist")

    helper = ImageHelper(content_dir, image_dir)
    helper.run()

    if not args.minify:
        return

    if not args.tinify_token:
        raise Exception("tinify token is required for minify images.")

    helper.minify(tinify_token)

    print()
    print("====== Uimages END ======")
    print()


if __name__ == "__main__":
    cli()
