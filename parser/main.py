import argparse
import os
import os.path
from collections import defaultdict
from parser import gcp, via_csv
from typing import Dict, List

import attr
import region as r

MIN_NUM_REGIONS_PER_LABEL = 15

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f',
        '--base_data_folder',
        help='Base data folder for the label files (in csv format)',
        type=str,
        default='data/src',
    )
    parser.add_argument(
        '-b',
        '--bucket',
        help='Bucket for the Google Storage',
        type=str,
        default='photo-id-2021',
    )
    parser.add_argument(
        '-o',
        '--out_file',
        help='The file name for the output gcp label file',
        type=str,
        default='./gcp_auto_ml_labels.csv',
    )
    parser.add_argument(
        '-n',
        '--min_num_regions',
        help='Min. number of regions per label',
        type=int,
        default=MIN_NUM_REGIONS_PER_LABEL,
    )
    args = parser.parse_args()

    base_data_folder = args.base_data_folder
    bucket = args.bucket
    out_file = args.out_file
    min_num_regions_per_label = args.min_num_regions

    image_sub_folders = [
        'HL20100702_01',
        'HL20100730_02',
        'HL20100803_01_gg_fix',
        'HL20100804_01_gg_fix',
        'HL20100818_02_gg_fix',
        'HL20100821_01_gg_fix',
        'HL20100823_04_gg_fix',
        'HL20110813_01_gg_fix',
        'HL20110819_03_gg_fix',
        'HL20110820_02_gg_fix',
        'HL20120708_01_gg_fix',
    ]
    image_folders = [
        os.path.join(base_data_folder, folder) for folder in image_sub_folders
    ]

    raw_regions: List[r.Region] = []
    for folder in image_folders:
        all_files = os.listdir(folder)
        region_files = [
            os.path.join(folder, f) for f in all_files if f.endswith('.csv')
        ]

        for region_file in region_files:
            print(
                '>>> Begin to process folder: {} with region file: {}'.format(
                    folder, region_file
                )
            )
            via_parser = via_csv.ViaCSVParser(
                image_folder=folder,
                region_file=region_file,
            )
            raw_regions += via_parser.read()

    # Filter out invalid regions.
    regions_filtered: List = []
    for region in raw_regions:
        if not region.is_valid():
            print('Invalid region:', region)
            continue

        regions_filtered.append(region)

    # Dedup
    regions_dedup: Dict[str, r.Region] = {}
    for region in regions_filtered:
        for label in region.labels:
            key = '{}_{}'.format(region.file.path, str(label))
            if key in regions_dedup:
                continue

            region_single_label = attr.evolve(region, labels=[label])
            regions_dedup[key] = region_single_label

    regions_dict: Dict = defaultdict(list)
    for region in regions_dedup.values():
        for label in region.labels:
            regions_dict[str(label)].append(region)

    total_num = sum([len(regions) for regions in regions_dict.values()])

    out_regions: List = []
    for label, regions in regions_dict.items():
        if len(regions) >= min_num_regions_per_label:
            print(
                '>>> Label to train: {:12s} with number of images: {}'.format(
                    label, len(regions)
                )
            )
            out_regions += regions

    print('>>> Number of regions in parser:', len(raw_regions))
    print('>>> Number of regions filtered :', len(regions_filtered))
    print('>>> Number of regions in dedup :', len(regions_dedup.values()))
    print('>>> Number of regions for label:', total_num)
    print('>>> Number of regions output   :', len(out_regions))

    gcp_parser = gcp.GCPParser(
        bucket=bucket,
        out_file=out_file,
    )

    gcp_parser.write(out_regions)

    print('>>> Output label file          :', out_file)