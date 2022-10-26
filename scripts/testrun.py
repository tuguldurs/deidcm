import os
import json
import shutil
import logging
import argparse
from pathlib import Path

import boto3
from collections import namedtuple

from deidcm.deidentifier import Deidentifier
from sfredact import SfRedactor
from deidcm import package_data_path


args = namedtuple('args', 'InputDirectory skip_private_tags no_bundled_output')
args = args('tmp', False, False)
deidentifier = Deidentifier.create(args)


def main(in_bucket, out_bucket):
    with open(package_data_path / 'gore.json', 'r') as f:
        studies = json.load(f)

    print(f'this script will process {len(studies)} studies')

    for idx, study in enumerate(studies):
        print(f'processing study - ')
        print(f'DICOM: {study["DICOM"]}')
        print(f'   SF: {study["SF"]}')

        print(f'downloading study...')
        in_bucket.download_file(study['DICOM'], 'dcm.zip')
        in_bucket.download_file(study['SF'], 'sf.pdf')

        print('unpacking...')
        if Path('tmp').is_dir():
            shutil.rmtree('tmp')
        os.mkdir('tmp')
        shutil.unpack_archive('dcm.zip', extract_dir='tmp')
        Path('dcm.zip').unlink()

        print('deidentifying DICOM and SF')
        deidentifier.run()
        redacted_name = f'{study["SF"].split("/")[-1].split(".pdf")[0]}_redacted.pdf'
        SfRedactor('sf.pdf').redact(redacted_name)

        print('packing deidentified study')
        dirname = [item for item in os.listdir('tmp/deidentified') if '_deidentified' in item][0]
        shutil.make_archive(f'tmp/deidentified/{dirname}', 'zip', f'tmp/deidentified/{dirname}')

        print('uploading...')
        out_bucket.upload_file(f'tmp/deidentified/{dirname}.zip', f'{dirname}.zip')
        out_bucket.upload_file(redacted_name, redacted_name)

        print('cleaning...')
        shutil.rmtree('tmp')
        for fname in os.listdir():
            if fname.endswith('.pdf') or fname.endswith('.zip'):
                Path(fname).unlink()

        print(f'---> done ({idx+1}/{len(studies)})')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_bucket', type=str, required=True, help='input s3 bucket name')
    parser.add_argument('-o', '--output_bucket', type=str, required=True, help='output s3 bucket name')
    args = parser.parse_args()

    resource = boto3.resource('s3')
    in_bucket = resource.Bucket(args.input_bucket)
    out_bucket = resource.Bucket(args.output_bucket)
    main(in_bucket, out_bucket)
