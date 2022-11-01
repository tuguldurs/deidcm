# Custom DICOM de-identification tool

This package de-identifies DICOM header data through `keep-list` method, e.g., by removing all tags not included in the specified list. The package scans every file in the input directory and creates de-identified copies. The input directory may contain any combination of formats, e.g., plain `.dcm` instances, series, studies either in DICOMDIR format or plain DICOM directory structure, or as a compressed `.zip` file.


## Setup

The package requires python version `>=3.7.10`.

1. Virtual Environment

If the base python3 installation satisfies the minimum requirement, python's built-in `venv` can be used to create a virtual environment:

`python3 -m venv env`

Activate the environment:

`source env/bin/activate`

Alternatively, if Conda is available one can setup a conda-environment with the desired python version, e.g.:

`conda create -n deidcm-dev python=3.8`

and activate it with:

`conda activate deidcm-dev`

2. Installation

Clone the repo:

`git clone https://github.com/tuguldurs/deidcm.git`

Navigate to the repo directory:

`cd deidcm`

and install the package with `pip`:

`pip install -e .`


## Usage

The `Deidentifier` class requires 3 arguments:
- `InputDirectory` - path to directory containing raw DICOM data
- `skip_private_tags` - boolean that specifies whether to remove private tags. When `False` all private tags will be removed, and when `True` they will be left untouched.
- `no_bundled_output` - boolean that specifies whether to bundle de-identified copies into one place. When `False` all de-identified copies will be written in a sub-directory named `deidentified/` that lives inside the `InputDirectory`, and when `False` all de-identified copies will be written in the working directory.

These arguments can be supplied e.g., using argparse or namedtuple to create an instance of `Deidentifier` class. Once the class is instantiated call the `run()` method to start, for example:

```python
from collections import namedtuple

from deidcm import Deidentifier

args = namedtuple('args', 'InputDirectory skip_private_tags no_bundled_output')
args = args('my_directory', False, False)
deidentifier = Deidentifier.create(args)
deidentifier.run()
```

The package will identify all DICOM instances living inside `my_directory/` and will create de-identified copies in their original format in `my_directory/deidentified/`. Non-DICOM files, e.g. DICOMDIR file, will be copied as well.

Suppose we originally had following contents in `my_directory/`:

```text
my_directory/
	├── some_image.png           <- non-DICOM file
	├── some_instance.dcm        <- stand-alone instance
	├── compressed_study.zip     <- compressed DICOM data
	└── sample_series/           <- stand-alone series
		├── instance1.dcm
		├── instance2.dcm
		└── instance3.dcm
	└── some_patient/            <- study in DICOMDIR format
    		├── DICOMDIR
    		└── some_study/
    			└── series1/
    				├── s1_instance1.dcm
    				└── s1_instance2.dcm
    			└── series2
    				├── s2_instance1.dcm
    				└── s2_instance2.dcm
```
After processing it will look like following:

```text
my_directory/
	└── deidentified/
		├── some_instance_deidentified.dcm
		├── compressed_study_deidentified.zip
		├── sample_series_deidentified/
		└── some_patient_deidentified/
	├── some_image.png
	├── some_instance.dcm
	├── compressed_study.zip
	├── sample_series/
	└── some_patient/
```
All original data are retained and all de-identified copies of DICOM data are bunled inside `my_directory/deidentified/`.

## De-identification

Every input file is checked by the package for the existense of 128-byte long preamble followed by `DICM` magic keyword, to determine whether it is a DICOM instance. 
For regular instances the de-identification is performed on a `keep-list` mode, where all base level tags (excluding header meta) are removed entirely except that 
are specified to be kept. The `keep-list` tags are listed in `configs/keep_tags.txt`, and can be modified to include any of the base-level standard tags:

```text
#
# List of standard DICOM tag names to keep
#
ImageType
SOPClassUID
SOPInstanceUID
ConvolutionalKernel
StudyInstanceUID
SeriesInstanceUID
PatientOrientation
ImageOrientationPatient
...
```
The tags are not required to be present in the instances, e.g. if the tag does not exist the processing will just skip and continue to check for the next tag.

For DICOMDIR files, the de-identification is performed on a `redact` mode, where all PHI containing tags are redacted into `0`s. Specifically the first two records, 
`PATIENT` and `STUDY`, are searched for potentially sensitive tags and redacted. The redaction applies the same number of `0` charactecters as the tag's original 
value, so that the native byte offsets among records are kept intact. The `redact-list` tags are listed in `configs/redact_tags.txt`, and can also be modified to include 
any other base level standard tags:

```text
#
# List of standard DICOM tag names to redact with 0s
# (used only for DICOMDIR)
#
PatientName
PatientAge
PatientBirthDate
PatientSex
PatientID
PhysicianName
PhysiciansOfRecord
InstitutionName
InstitutionAddress
AccessionNumber
StudyDate
StudyTime
StudyID
...
```


## Selection Form Redaction

...