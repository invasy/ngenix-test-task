from zipfile import ZipFile

import pytest

from random_xml_csv import defaults
from random_xml_csv.xml import RandomXml


class TestRandomXml:
    @staticmethod
    def _xml(path):
        return RandomXml(
            path,
            defaults.ZIP_NUM,
            defaults.XML_NUM,
            defaults.LEVEL_MIN,
            defaults.LEVEL_MAX,
            defaults.OBJECTS_MIN,
            defaults.OBJECTS_MAX,
            defaults.STR_SIZE,
            defaults.STR_CHARS,
        )

    def test_zip_name(self):
        assert RandomXml.zip_name(1) == 'random-01.zip'
        assert RandomXml.zip_name(42) == 'random-42.zip'
        assert RandomXml.zip_name(101) == 'random-101.zip'
        with pytest.raises(AssertionError):
            RandomXml.zip_name(-1)

    def test_xml_name(self):
        assert RandomXml.xml_name(1, 1) == 'data-01-01.xml'
        assert RandomXml.xml_name(11, 1) == 'data-11-01.xml'
        assert RandomXml.xml_name(3, 15) == 'data-03-15.xml'
        assert RandomXml.xml_name(42, 69) == 'data-42-69.xml'
        assert RandomXml.xml_name(101, 1337) == 'data-101-1337.xml'
        with pytest.raises(AssertionError):
            RandomXml.xml_name(-1, 1)
        with pytest.raises(AssertionError):
            RandomXml.xml_name(1, -1)

    def test_objects(self, tmp_path):
        rx = self._xml(tmp_path)
        root = rx.xml()
        assert defaults.OBJECTS_MIN <= len(root.find('objects')) <= defaults.OBJECTS_MAX

    def test_xml(self, tmp_path):
        rx = self._xml(tmp_path)
        root = rx.xml()
        var = root.findall('var')
        assert len(var) == 2  # noqa: PLR2004
        assert var[0].get('name') == 'id'
        assert var[1].get('name') == 'level'
        assert defaults.LEVEL_MIN <= int(var[1].get('value')) <= defaults.LEVEL_MAX

    def test_zip(self, tmp_path):
        i = 42
        rx = self._xml(tmp_path)
        path = rx.zip(i)
        assert path.name == RandomXml.zip_name(i)
        with ZipFile(path, 'r') as z:
            names = z.namelist()
            assert len(names) == defaults.XML_NUM

    def test_zips(self, tmp_path):
        rx = self._xml(tmp_path)
        path = rx.zips()
        assert len(list(path.glob('*.zip'))) == defaults.ZIP_NUM
