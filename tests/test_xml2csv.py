import csv
from collections import defaultdict
from zipfile import ZipFile

from lxml import etree

from random_xml_csv import defaults
from random_xml_csv.csv import xml2csv
from random_xml_csv.xml import RandomXml


def test_xml2csv(tmp_path):
    rx = RandomXml(
        tmp_path,
        defaults.ZIP_NUM,
        defaults.XML_NUM,
        defaults.LEVEL_MIN,
        defaults.LEVEL_MAX,
        defaults.OBJECTS_MIN,
        defaults.OBJECTS_MAX,
        defaults.STR_SIZE,
        defaults.STR_CHARS,
    )
    rx.zips()
    xml2csv(tmp_path, tmp_path)

    assert len(list(tmp_path.glob('*.csv'))) == 2  # noqa: PLR2004

    xml_data = {}
    for path in tmp_path.glob('*.zip'):
        with ZipFile(path, mode='r') as z:
            for name in z.namelist():
                root = etree.fromstring(z.read(name))  # noqa: S320
                id_ = root.find('var[@name="id"]').get('value')
                level = int(root.find('var[@name="level"]').get('value'))
                objects = [obj.get('name') for obj in root.find('objects')]
                xml_data[id_] = {'level': level, 'objects': objects}

    with (tmp_path / 'levels.csv').open(mode='rt', newline='') as f:
        reader = csv.DictReader(f)
        levels_csv = {row['id']: int(row['level']) for row in reader}
        assert len(levels_csv) == defaults.ZIP_NUM * defaults.XML_NUM
        for id_, level in levels_csv.items():
            assert defaults.LEVEL_MIN <= level <= defaults.LEVEL_MAX
            assert level == xml_data[id_]['level']

    with (tmp_path / 'objects.csv').open(mode='rt', newline='') as f:
        reader = csv.DictReader(f)
        objects_csv = defaultdict(list)
        for row in reader:
            objects_csv[row['id']].append(row['object_name'])
        assert len(objects_csv) == defaults.ZIP_NUM * defaults.XML_NUM
        for id_, objects in objects_csv.items():
            assert defaults.OBJECTS_MIN <= len(objects) <= defaults.OBJECTS_MAX
            assert objects == xml_data[id_]['objects']
