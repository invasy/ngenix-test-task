from pathlib import Path
from random import choices, randint
from zipfile import ZipFile

from lxml import etree


def randstr(k: int, chars: str) -> str:
    return ''.join(choices(chars, k=k))


class RandomXml:
    def __init__(  # noqa: PLR0913
        self,
        xml_dir: Path,
        zip_num: int,
        xml_num: int,
        level_min: int,
        level_max: int,
        objects_min: int,
        objects_max: int,
        str_size: int,
        str_chars: str,
    ) -> None:
        self.xml_dir = xml_dir
        self.zip_num = zip_num
        self.xml_num = xml_num
        self.level_min = level_min
        self.level_max = level_max
        self.objects_min = objects_min
        self.objects_max = objects_max
        self.str_size = str_size
        self.str_chars = str_chars

    @staticmethod
    def zip_name(i: int) -> str:
        assert i >= 0, 'ZIP file number must be greater or equal to 0'
        return f'random-{i:02}.zip'

    @staticmethod
    def xml_name(i: int, j: int) -> str:
        assert i >= 0, 'ZIP file number must be greater or equal to 0'
        assert j >= 0, 'XML file number must be greater or equal to 0'
        return f'data-{i:02}-{j:02}.xml'

    def zips(self) -> Path:
        self.xml_dir.mkdir(parents=True, exist_ok=True)
        for i in range(self.zip_num):
            self.zip(i)
        return self.xml_dir

    def zip(self, i: int) -> Path:
        assert i >= 0, 'ZIP file number must be greater or equal to 0'
        path = self.xml_dir / self.zip_name(i)
        with ZipFile(path, 'w') as z:
            for j in range(self.xml_num):
                filename = self.xml_name(i, j)
                data = etree.tostring(self.xml())
                z.writestr(filename, data)
        return path

    def xml(self):
        id_ = randstr(self.str_size, self.str_chars)
        level = randint(self.level_min, self.level_max)

        root = etree.Element('root')
        root.append(etree.Element('var', name='id', value=id_))
        root.append(etree.Element('var', name='level', value=str(level)))
        self.objects(root, randint(1, 10))

        return root

    def objects(self, root, n: int):
        obj = etree.SubElement(root, 'objects')
        for _ in range(n):
            obj.append(etree.Element('object', name=randstr(self.str_size, self.str_chars)))
        return root
