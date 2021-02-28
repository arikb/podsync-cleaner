import os
from typing import List, Optional, MutableSet
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, ParseResult

import click

from log import l


@click.group()
def cli() -> None:
    """PodSync media folder cleaner"""
    pass


def get_feed_files(folder: str) -> List[str]:
    """return all XML files in the folder"""
    return [
        os.path.join(folder, file_name)
        for file_name in os.listdir(folder)
        if os.path.splitext(file_name)[1].lower() == ".xml"
    ]


def feed_clean(file_name: str) -> None:
    """cleans a podcast feed's folder"""
    feed_file_folder: str = os.path.split(file_name)[0]
    xml_element_tree: ET.ElementTree = ET.parse(file_name)
    xml_root: ET.Element = xml_element_tree.getroot()

    # loop modified objects:
    enclosure_file_names: MutableSet[str] = set()
    enclosure_relative_folder: Optional[str] = None

    for item in xml_root.findall("./channel/item/enclosure"):
        enclosure_url: str = item.attrib["url"]
        url_parse_result: ParseResult = urlparse(enclosure_url)
        if enclosure_relative_folder is None:
            enclosure_relative_folder = os.path.dirname(url_parse_result.path)
        enclosure_file_names.add(os.path.basename(url_parse_result.path))

    if enclosure_relative_folder is None:
        l.warn(f"No enclosures in feed file {file_name}")
        return

    enclosure_abs_folder = os.path.join(feed_file_folder, enclosure_relative_folder[1:])
    existing_file_names: List[str] = os.listdir(enclosure_abs_folder)
    files_to_delete: List[str] = [
        os.path.join(enclosure_abs_folder, f)
        for f in existing_file_names
        if f not in enclosure_file_names
    ]

    l.info(
        f"Feed file {file_name} - deleting {len(files_to_delete)} out of {len(existing_file_names)} files"
    )

    for file_name in files_to_delete:
        print(file_name)
        ## os.unlink(file_name)


@cli.command("clean")
@click.argument(
    "folder",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
)
def podsync_clean(folder: str) -> None:
    """scan a folder and clean any redundant media files"""
    feed_files: List[str] = get_feed_files(folder)
    for file_name in feed_files:
        feed_clean(file_name)


if __name__ == "__main__":
    cli()