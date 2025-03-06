#!/usr/bin/env python

import datetime
import json
import os
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path
from textwrap import dedent

from PyMAIA.utils.file_utils import subfolders, subfiles
from PyMAIA.utils.log_utils import add_verbosity_options_to_argparser, str2bool
from PyMAIA.utils.seg_mask_utils import semantic_segmentation_to_instance

TIMESTAMP = "{:%Y-%m-%d_%H-%M-%S}".format(datetime.datetime.now())

DESC = dedent(
    """
    Script to convert a semantic segmentation dataset (with the `Patient ID` as the folder name) into an instance segmentation dataset.
    Instance segmentation masks are saved within the same patient folder with the standard format "INST_SEG.nii.gz". Regions in instance 
    segmentation containing less than 10 voxels are ignored and the number of labels in each instance segmentation mask is saved in a 
    separate json file ('inst_seg_labels.json') alongside its 'Patient ID'. 
    """  # noqa: E501
)
EPILOG = dedent(
    """
    Example call:
    ::
        {filename}  --data-folder /PATH/TO/SEMANTIC_SEG_DATA --sem-seg-suffix _SEG.nii.gz --inst-seg-suffix _INST_SEG.nii.gz --output-json-path /PATH/TO/JSON/inst_seg_labels.json
    """.format(  # noqa: E501
        filename=Path(__file__).stem
    )
)


def get_arg_parser():
    pars = ArgumentParser(description=DESC, epilog=EPILOG, formatter_class=RawTextHelpFormatter)

    pars.add_argument(
        "--data-folder",
        type=str,
        required=True,
        help="AutoPET patient dataset folder.",
    )

    pars.add_argument(
        "--sem-seg-suffix",
        type=str,
        required=True,
        help="Semantic Segmentation suffix.",
    )

    pars.add_argument(
        "--inst-seg-suffix",
        type=str,
        required=True,
        help="Instance Segmentation suffix.",
    )

    pars.add_argument(
        "--inst-seg-folder",
        type=str,
        required=False,
        help="Instance Segmentation Folder.Required only for the Decathlon-format Dataset.",
    )
    pars.add_argument(
        "--output-json-path",
        type=str,
        required=True,
        help="Output path of json file.",
    )

    pars.add_argument(
        "--decathlon-format",
        type=str2bool,
        required=False,
        default="no",
        help="Flag to specify if the Dataset is in the Decathlon format.",
    )

    add_verbosity_options_to_argparser(pars)

    return pars


def main():
    parser = get_arg_parser()
    arguments = vars(parser.parse_args())


    sem_seg = arguments["sem_seg_suffix"]
    inst_seg = arguments["inst_seg_suffix"]
    out_json = arguments["output_json_path"]

    # e.g. subject + sem_seg = "PETCT_0011f3deaf_0_SEG.nii.gz"
    labels_dict = {}

    if arguments["decathlon_format"]:
        subjects = subfiles(arguments["data_folder"], join=False)
        for subject in subjects:
            subject_id = subject[:-len(sem_seg)]
            subject_sem_seg_filename = os.path.join(arguments["data_folder"], subject)
            subject_inst_seg_filename = os.path.join(arguments["inst_seg_folder"], str(subject_id+sem_seg))
            if Path(subject_inst_seg_filename).is_file():
                    print(f"Skipping {subject_id}: Already exist!")
            else:
                num_features = semantic_segmentation_to_instance(subject_sem_seg_filename, subject_inst_seg_filename)
                labels_dict.update({str(subject_id): num_features})
                print("Subject: ", subject_id, " converted mask done.")
    else:
        subjects = subfolders(arguments["data_folder"], join=False)
        for subject in subjects:
            subject_sem_seg_filename = os.path.join(arguments["data_folder"], subject, str(subject + sem_seg))
            subject_inst_seg_filename = os.path.join(arguments["data_folder"], subject, str(subject + inst_seg))
            if Path(subject_inst_seg_filename).is_file():
                    print(f"Skipping {subject}: Already exist!")
            else:
                num_features = semantic_segmentation_to_instance(subject_sem_seg_filename, subject_inst_seg_filename)
                labels_dict.update({str(subject): num_features})
                print("Subject: ", subject, " converted mask done.")

    # Create Json file with number of labels of instance segmentation for each patient.
    with open(out_json, 'w') as json_file:
        json.dump(labels_dict, json_file)


if __name__ == "__main__":
    main()
