import json
import argparse

import boto3

from deidcm.deidentifier import Deidentifier
from deidcm import package_data_path


def main(in_bucket):#, out_bucket):
    with open(package_data_path / 'gore.json', 'r') as f:
        studies = json.load(f)
    print(studies)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_bucket', type=str, required=True, help='input s3 bucket name')
    #parser.add_argument('-o', '--output_bucket', type=str, required=True, help='output s3 bucket name')
    args = parser.parse_args()

    resource = boto3.resource('s3')
    in_bucket = resource.Bucket(args.input_bucket)
    #out_bucket = resource.Bucket(args.output_bucket)
    main(in_bucket)#, out_bucket)
