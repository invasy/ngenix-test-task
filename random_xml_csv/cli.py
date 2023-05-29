import logging
from argparse import ArgumentParser, Namespace
from pathlib import Path
from random import seed

from . import defaults
from .csv import xml2csv
from .xml import RandomXml

logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')


def parse_args() -> Namespace:
    parser = ArgumentParser(description='NGENIX test task')
    parser.add_argument('--xml-dir', help='directory for zipped XML files')
    parser.add_argument('--csv-dir', help='directory for CSV files')
    parser.add_argument('-z', '--zip-num', type=int, default=defaults.ZIP_NUM,
                        help=f'number of ZIP files to create [{defaults.ZIP_NUM}]')
    parser.add_argument('-x', '--xml-num', type=int, default=defaults.XML_NUM,
                        help=f'number of XML files to create [{defaults.XML_NUM}]')
    parser.add_argument('--level-min', type=int, default=defaults.LEVEL_MIN,
                        help=f'minimal level [{defaults.LEVEL_MIN}]')
    parser.add_argument('--level-max', type=int, default=defaults.LEVEL_MAX,
                        help=f'maximal level [{defaults.LEVEL_MAX}]')
    parser.add_argument('--objects-min', type=int, default=defaults.OBJECTS_MIN,
                        help=f'minimal number of objects [{defaults.OBJECTS_MIN}]')
    parser.add_argument('--objects-max', type=int, default=defaults.OBJECTS_MAX,
                        help=f'maximal number of objects [{defaults.OBJECTS_MAX}]')
    parser.add_argument('--str-size', type=int, default=defaults.STR_SIZE,
                        help=f'size of random strings [{defaults.STR_SIZE}]')
    return parser.parse_args()


def main():
    args = parse_args()
    xml_path = Path(args.xml_dir) if args.xml_dir else Path.cwd()
    csv_path = Path(args.csv_dir) if args.csv_dir else Path.cwd()

    try:
        seed()
        r = RandomXml(
            xml_path,
            args.zip_num,
            args.xml_num,
            args.level_min,
            args.level_max,
            args.objects_min,
            args.objects_max,
            args.str_size,
            defaults.STR_CHARS
        )
        r.zips()
        xml2csv(xml_path, csv_path)
    except PermissionError as e:
        logging.error("cannot create file '%s': permission denied", e.filename)
    except Exception as e:
        logging.exception('something unexpected happened: %s', repr(e), exc_info=e)
