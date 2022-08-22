# deidcm
DICOM de-identifier

# Custom tags

The list of tags to be de-identified can be configured by changing the contents of the configuration file `config\tags.ini`. However note, that beside the de-identification mode, the tags perceived type also needs to be provided. This is because tag type is not defined in the DICOM dictionary, where the tag definitions are generated from, but in the IODs in part 3 of the standard. The same tag can have different types in different IODs, and even than the type may depend on other present tags. 