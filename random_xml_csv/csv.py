import csv
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from itertools import chain
from pathlib import Path
from typing import List, Union
from zipfile import ZipFile

from lxml import etree


@dataclass
class Entry:
    id: str
    level: int
    objects: List[List[str]]


Entries = List[Entry]


def write(path: Path, header: List[str], rows: List[List[Union[str, int]]]) -> None:
    with path.open(mode='wt', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def process_xml(data: bytes) -> Entry:
    root = etree.fromstring(data)  # noqa: S320
    id_ = root.find('var[@name="id"]').get('value')
    level = int(root.find('var[@name="level"]').get('value'))
    objects = [[id_, obj.get('name')] for obj in root.find('objects')]
    return Entry(id_, level, objects)


def process_zip(path: Path) -> Entries:
    with ZipFile(path, mode='r') as z:
        return [process_xml(z.read(name)) for name in z.namelist()]


def xml2csv(xml_path: Path, csv_path: Path) -> None:
    zips = xml_path.glob('*.zip')
    levels = []
    objects = []

    with ProcessPoolExecutor() as executor:
        for entry in chain.from_iterable(executor.map(process_zip, zips)):
            levels.append([entry.id, entry.level])
            objects.extend(entry.objects)

    csv_path.mkdir(parents=True, exist_ok=True)
    write(csv_path / 'levels.csv', ['id', 'level'], levels)
    write(csv_path / 'objects.csv', ['id', 'object_name'], objects)
