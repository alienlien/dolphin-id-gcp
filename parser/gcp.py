from parser import parser
import region
from typing import List
from parser import gcp_type
import os.path
import csv


def to_gcp_region(
    obj: region.Region, bucket: str, tp: gcp_type.GCPImageType
) -> List:
    # UNASSIGNED,gs://folder/im2.png,car,0.1,0.1,0.2,0.1,0.2,0.3,0.1,0.3
    # Ref: https://cloud.google.com/vision/automl/object-detection/docs/csv-format
    file_path = 'gs://{}'.format(os.path.join(bucket, obj.file.path))
    location = [
        obj.x_min_rel,
        obj.y_min_rel,
        '',
        '',
        obj.x_max_rel,
        obj.y_max_rel,
        '',
        '',
    ]
    return [
        tp.name,
        file_path,
        obj.label.to_label_str(),
    ] + location


class GCPParser(parser.Parser):
    """Parser to parse the image annotation for GCP auto ML.
    UNASSIGNED,gs://folder/im2.png,car,0.1,0.1,0.2,0.1,0.2,0.3,0.1,0.3

    Attributes:
        _bucket: GCS bucket.
        _out_file: Output file path.
    """
    def __init__(self, bucket: str, out_file: str) -> None:
        self._bucket = bucket
        self._out_file = out_file

    def read(self) -> List[region.Region]:
        pass

    def write(self, regions: List[region.Region]) -> None:
        rows = [
            to_gcp_region(reg, self._bucket, gcp_type.GCPImageType.UNASSIGNED)
            for reg in regions
        ]
        with open(self._out_file, 'w') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(rows)
