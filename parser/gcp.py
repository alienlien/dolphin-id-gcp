from parser import parser
import region
from typing import List
from parser import gcp_type
import os.path
import csv


def to_gcp_rows(obj: region.Region, bucket: str,
                tp: gcp_type.GCPImageType) -> List[List[str]]:
    # UNASSIGNED,gs://folder/im2.png,car,0.1,0.1,0.2,0.1,0.2,0.3,0.1,0.3
    # Ref: https://cloud.google.com/vision/automl/object-detection/docs/csv-format
    file_path = 'gs://{}'.format(os.path.join(bucket, obj.file.path))
    location = [
        str(obj.x_min_rel),
        str(obj.y_min_rel),
        '',
        '',
        str(obj.x_max_rel),
        str(obj.y_max_rel),
        '',
        '',
    ]
    out = []
    for label in obj.labels:
        row = [tp.name, file_path, str(label)] + location
        out.append(row)

    return out


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
        rows: List[List[str]] = []
        for reg in regions:
            reg_rows = to_gcp_rows(
                obj=reg,
                bucket=self._bucket,
                tp=gcp_type.GCPImageType.UNASSIGNED,
            )
            rows += reg_rows

        with open(self._out_file, 'w') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(rows)
