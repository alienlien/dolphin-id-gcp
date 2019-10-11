from parser import parser
import const
import re
import region
from typing import List, Dict
import csv
from pprint import pprint
import os.path
import json
from PIL import Image

DEFAULT_LABEL_ID = -1

ku_id_key_1 = 'KU_ID'
ku_id_key_2 = 'KU ID'
group_id_key_1 = 'GROUP_ID'
group_id_key_2 = 'GROUP ID'


def prefix_for_filename(fname):
    """It returns the prefix for the group id from file name input.
    Note that we now use the file name directly rather than the folder.
    One day we might need to fetch the 'Date' information (i.e., prefix)
    from folder import directly.

    Args:
        fname: File name of the image.

    Return:
        The prefix used for the group id of that file.

    Example:
        Input : HL20100702_01_Gg_990702 (25).JPG
        Return: 20100702
    """
    group_name = fname.split('_')[0]
    return re.findall('\d+', group_name)[0]


def to_region(obj: Dict, image_folder: str = '') -> region.Region:
    file_path = os.path.join(image_folder, obj['#filename'])
    if os.path.exists(file_path):
        img = Image.open(file_path)
        (x_size, y_size) = img.size
    else:
        x_size = 0
        y_size = 0

    file = region.ImageFile(
        path=file_path,
        x_size=x_size,
        y_size=y_size,
    )
    shape_info = json.loads(obj['region_shape_attributes'])
    label_info = json.loads(obj['region_attributes'])
    label = region.Label(
        ku_id=int(label_info.get('KU_ID', const.DEFAULT_LABEL_ID)),
        group_id=int(label_info.get('GROUP_ID', const.DEFAULT_LABEL_ID)),
    )
    return region.Region(
        file=file,
        shape=shape_info['name'],
        x_min=int(shape_info['x']),
        y_min=int(shape_info['y']),
        x_length=int(shape_info['width']),
        y_length=int(shape_info['height']),
        label=label,
    )


class ViaCSVParser(parser.Parser):
    def __init__(self, image_folder: str, region_file: str) -> None:
        self._image_folder = image_folder
        self._region_file = region_file

    def read(self) -> List[region.Region]:
        """
        format: HL20120708_01_gg_004_IMG_2805.JPG,5455648,"{}",1,0,"{""name"":""rect"",""x"":2985,""y"":1193,""width"":323,""height"":330}","{""GROUP_ID"":""02"",""KU_ID"":""017""}"
        """
        out = []
        with open(self._region_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['region_count'] == str(0):
                    continue

                out.append(to_region(row, self._image_folder))

        return out

    def write(self, regions: List[region.Region]) -> None:
        pass


if __name__ == '__main__':
    region_file_path = './data/src/HL20120708_01_gg_fix/HL20120708_01via_region_data_ID.csv'
    image_folder = './data/src/HL20120708_01_gg_fix/'
    fmter = ViaCSVParser(
        image_folder=image_folder,
        region_file=region_file_path,
    )
    regions = fmter.read()
    pprint(regions)
