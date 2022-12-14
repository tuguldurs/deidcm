import os
import json
import shutil
import logging.config
import argparse
from pathlib import Path

import boto3
from collections import namedtuple

from deidcm.deidentifier import Deidentifier
from sfredact import SfRedactor
from deidcm import package_data_path
from deidcm.utils import parse_log_config


logging.config.dictConfig(parse_log_config())
log = logging.getLogger(__name__)


args = namedtuple('args', 'InputDirectory skip_private_tags no_bundled_output')
args = args('tmp', False, False)
deidentifier = Deidentifier.create(args)

parent = 'tmp/deidentified'


def main(in_bucket, out_bucket):
    with open(package_data_path / 'gore.json', 'r') as f:
        studies = json.load(f)

    # local
    #studies = [studies[4], studies[8], studies[150]]
    studies = studies[5:10]


    log.info(f'this script will process {len(studies)} studies')

    for idx, study in enumerate(studies):
        log.info(f'processing study - ')
        log.info(f'DICOM: {study["DICOM"]}')
        log.info(f'   SF: {study["SF"]}')
        study_id = study["SF"].split("/")[-1].replace('.pdf', '')
        log.info(f'study ID = {study_id}')
        study_id = f'study{idx:03}'

        log.info(f'downloading study...')
        in_bucket.download_file(study['DICOM'], 'dcm.zip')
        in_bucket.download_file(study['SF'], 'sf.pdf')

        log.info('unpacking...')
        if Path('tmp').is_dir():
            shutil.rmtree('tmp')
        os.mkdir('tmp')
        shutil.unpack_archive('dcm.zip', extract_dir='tmp')
        Path('dcm.zip').unlink()

        log.info('deidentifying DICOM and SF')
        deidentifier.run()
        redacted_name = f'{study_id}.pdf'
        SfRedactor('sf.pdf').redact(redacted_name)

        log.info('packing deidentified study')
        dirname = [item for item in os.listdir(parent) if '_deidentified' in item][0]
        shutil.move(f'{parent}/{dirname}', f'{parent}/{study_id}')
        shutil.make_archive(f'{parent}/{study_id}', 'zip', f'{parent}/{study_id}')

        log.info('uploading...')
        out_bucket.upload_file(f'{parent}/{study_id}.zip', f'{study_id}.zip')
        out_bucket.upload_file(redacted_name, redacted_name)

        log.info('cleaning...')
        shutil.rmtree('tmp')
        for fname in os.listdir():
            if fname.endswith('.pdf') or fname.endswith('.zip'):
                Path(fname).unlink()

        log.info(f'---> done ({idx+1}/{len(studies)})')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_bucket', type=str, required=True, help='input s3 bucket name')
    parser.add_argument('-o', '--output_bucket', type=str, required=True, help='output s3 bucket name')
    args = parser.parse_args()

    session = boto3.session.Session(profile_name='default')
    resource = session.resource('s3')
    in_bucket = resource.Bucket(args.input_bucket)
    out_bucket = resource.Bucket(args.output_bucket)
    main(in_bucket, out_bucket)
