import os
import json
import shutil
import argparse
from pathlib import Path

import boto3
from collections import namedtuple

from deidcm.deidentifier import Deidentifier
from deidcm import package_data_path


args = namedtuple('args', 'InputDirectory skip_private_tags no_bundled_output')
args = args('tmp', False, False)
deidentifier = Deidentifier.create(args)


def main(in_bucket):#, out_bucket):
    with open(package_data_path / 'gore.json', 'r') as f:
        studies = json.load(f)
    study = studies[0]

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

    print('deidentifying DICOM')
    deidentifier.run()

    print('packing deidentified study')
    dirname = [item for item in os.listdir('tmp/deidentified') if '_deidentified' in item][0]
    shutil.make_archive(f'tmp/deidentified/{dirname}', 'zip', f'tmp/deidentified/{dirname}')

    #print('uploading...')

    
    #print('cleaning...')
    #Path('dcm.zip').unlink()
    shutil.rmtree('tmp')

    #print(f'---> done ({idx+1}/{len(studies)}')




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_bucket', type=str, required=True, help='input s3 bucket name')
    #parser.add_argument('-o', '--output_bucket', type=str, required=True, help='output s3 bucket name')
    args = parser.parse_args()

    resource = boto3.resource('s3')
    in_bucket = resource.Bucket(args.input_bucket)
    #out_bucket = resource.Bucket(args.output_bucket)
    main(in_bucket)#, out_bucket)
