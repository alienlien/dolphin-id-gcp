from parser import via_csv, gcp
from pprint import pprint
import os.path
import os
import region as r
from typing import List, Dict
from collections import defaultdict
import attr

MIN_NUM_REGIONS_PER_LABEL = 15

if __name__ == '__main__':

    base_data_folder = 'data/src'

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
        if len(regions) >= MIN_NUM_REGIONS_PER_LABEL:
            print(
                '>>> Label to train: {} with number of iamges: {}'.format(
                    label, len(regions)
                )
            )
            out_regions += regions

    print('>>> Number of regions in parser:', len(raw_regions))
    print('>>> Number of regions filtered :', len(regions_filtered))
    print('>>> Number of regions in dedup :', len(regions_dedup.values()))
    print('>>> Number of regions for label:', total_num)
    print('>>> Number of regions output   :', len(out_regions))

    bucket = 'dolphin-id-gcp'
    out_file = './gcp_test_3.csv'
    gcp_parser = gcp.GCPParser(
        bucket=bucket,
        out_file=out_file,
    )

    # pprint(out_regions)
    gcp_parser.write(out_regions)
