import json
import os
import random
import shutil
from distutils.dir_util import copy_tree
from multiprocessing import Pool
from os import PathLike
from pathlib import Path
from typing import Union, List, Tuple, Dict

import SimpleITK
import nibabel as nib
import numpy as np
import pydicom
import pydicom_seg
from tqdm import tqdm

from PyMAIA.utils.log_utils import get_logger, DEBUG, WARN, INFO

logger = get_logger(__name__)


def subfiles(
        folder: Union[str, PathLike], join: bool = True, prefix: str = None, suffix: str = None, sort: bool = True
) -> List[str]:
    """
    Given a folder path, returns a list with all the files in the folder.

    Parameters
    ----------
    folder :
        Folder path.
    join :
        Flag to return the complete file paths or only the relative file names.
    prefix :
        Filter the files with the specified prefix.
    suffix :
        Filter the files with the specified suffix.
    sort :
        Flag to sort the files in the list by alphabetical order.

    Returns
    -------
        Filename list.
    """
    if join:
        l = os.path.join  # noqa: E741
    else:
        l = lambda x, y: y  # noqa: E741, E731
    res = [
        l(folder, i.name)
        for i in Path(folder).iterdir()
        if i.is_file() and (prefix is None or i.name.startswith(prefix)) and (suffix is None or i.name.endswith(suffix))
    ]
    if sort:
        res.sort()
    return res


def subfolders(folder: Union[str, PathLike], join: bool = True, sort: bool = True) -> List[str]:
    """
     Given a folder path, returns a list with all the subfolders in the folder.

    Parameters
    ----------
    folder :
        Folder path.
    join :
        Flag to return the complete folder paths or only the relative folder names.
    sort :
        Flag to sort the sub folders in the list by alphabetical order.

    Returns
    -------
        Sub folder list.
    """
    if join:
        l = os.path.join  # noqa: E741
    else:
        l = lambda x, y: y  # noqa: E741, E731
    res = [l(folder, i.name) for i in Path(folder).iterdir() if i.is_dir()]
    if sort:
        res.sort()
    return res


def create_nnunet_data_folder_tree(data_folder: str, task_name: str, task_id: str):
    """
    Create nnUnet folder tree, ready to be populated with the dataset.

    nnUnet folder tree:

        [raw_data_base]

        [Dataset000_Example]
            - dataset.yaml # dataset.json works too
            
            [imagesTr]
                - case0000_0000.nii.gz # case0000 modality 0
                - case0000_0001.nii.gz # case0000 modality 1
                - case0001_0000.nii.gz # case0001 modality 0
                - case0000_0001.nii.gz # case0001 modality 1
                
            [labelsTr]
                - case0000.nii.gz # instance segmentation case0000
                - case0000.json # properties of case0000
                - case0001.nii.gz # instance segmentation case0001
                - case0001.json # properties of case0001
                
            [imagesTs] # optional, same structure as imagesTr
            
            ...
            
            [labelsTs] # optional, same structure as labelsTr

        [Dataset001_Example1]
            ...


    Parameters
    ----------
    data_folder :
        folder path corresponding to the *raw_data_base* environment variable.
    task_name :
        string used as task_name when creating task folder
    task_id :
        string used as task_id when creating task folder
    """  # noqa E501
    logger.log(DEBUG, ' Creating Dataset tree at "{}"'.format(data_folder))

    Path(data_folder).joinpath("nnUNet_raw", "Dataset" + task_id + "_" + task_name, "imagesTr", ).mkdir(
        parents=True,
        exist_ok=True,
    )

    Path(data_folder).joinpath("nnUNet_raw", "Dataset" + task_id + "_" + task_name, "labelsTr", ).mkdir(
        parents=True,
        exist_ok=True,
    )

    Path(data_folder).joinpath("nnUNet_raw", "Dataset" + task_id + "_" + task_name, "imagesTs", ).mkdir(
        parents=True,
        exist_ok=True,
    )

    Path(data_folder).joinpath("nnUNet_raw", "Dataset" + task_id + "_" + task_name, "labelsTs", ).mkdir(
        parents=True,
        exist_ok=True,
    )


def create_nndet_data_folder_tree(data_folder: Union[str, PathLike], task_name: str, task_id: str):
    """
    Create nnDetection folder tree, ready to be populated with the dataset.

    nnDetection folder tree:

        [raw_data_base]

        [Task000_Example]
            - dataset.yaml # dataset.json works too

            [raw_splitted]
                [imagesTr]
                    - case0000_0000.nii.gz # case0000 modality 0
                    - case0000_0001.nii.gz # case0000 modality 1
                    - case0001_0000.nii.gz # case0001 modality 0
                    - case0000_0001.nii.gz # case0001 modality 1

                [labelsTr]
                    - case0000.nii.gz # instance segmentation case0000
                    - case0000.json # properties of case0000
                    - case0001.nii.gz # instance segmentation case0001
                    - case0001.json # properties of case0001

                [imagesTs] # optional, same structure as imagesTr
                ...

                [labelsTs] # optional, same structure as labelsTr
                ...

            [preprocessed]

            [results]

        [Task001_Example1]
            ...


    Parameters
    ----------
    data_folder :
        folder path corresponding to the *raw_data_base* environment variable.
    task_name :
        string used as task_name when creating task folder
    task_id :
        string used as task_id when creating task folder
    """
    logger.log(DEBUG, ' Creating Dataset tree at "{}"'.format(data_folder))

    Path(data_folder).joinpath("Task" + task_id + "_" + task_name, "raw_splitted", "imagesTr", ).mkdir(
        parents=True,
        exist_ok=True,
    )

    Path(data_folder).joinpath("Task" + task_id + "_" + task_name, "raw_splitted", "labelsTr", ).mkdir(
        parents=True,
        exist_ok=True,
    )

    Path(data_folder).joinpath("Task" + task_id + "_" + task_name, "raw_splitted", "imagesTs", ).mkdir(
        parents=True,
        exist_ok=True,
    )

    Path(data_folder).joinpath("Task" + task_id + "_" + task_name, "raw_splitted", "labelsTs", ).mkdir(
        parents=True,
        exist_ok=True,
    )


def split_dataset(input_data_folder: Union[str, PathLike], test_split_ratio: int, seed: int,
                  patient_class_file: Union[str, PathLike] = None,
                  classes: List[str] = None) -> Tuple[
    List[str], List[str]]:
    """
    Split dataset into a train/test split, given the specified ratio.

    Parameters
    ----------
    classes :
        List of Patient classes to include in the experiment.
    patient_class_file  :
        File path to JSON Patient Class map.
    input_data_folder :
        folder path of the input dataset.
    test_split_ratio :
        integer value in the range 0-100, specifying the split ratio to be used for the test set.
    seed :
        integer value to be used as random seed.

    Returns
    -------
        lists of strings containing subject IDs for train set and test set respectively.
    """
    subjects = subfolders(input_data_folder, join=False)

    if patient_class_file is not None:
        with open(patient_class_file, "r") as file:
            subject_class = json.load(file)

        if classes is not None:
            filtered_subjects = []
            for subject in subjects:
                if subject_class[subject] in classes and subject != "PETCT_0223010e46_0":
                    filtered_subjects.append(subject)
            subjects = filtered_subjects

    random.seed(seed)
    random.shuffle(subjects)

    split_index = len(subjects) - int(len(subjects) * test_split_ratio / 100)

    train_subjects = subjects[0:split_index]
    test_subjects = subjects[split_index:]

    return train_subjects, test_subjects


def copy_image_file(input_filepath: Union[str, PathLike], output_filepath: Union[str, PathLike]):
    """
    Copy image file.

    Parameters
    ----------
    input_filepath :
        file path for the file to copy
    output_filepath :
        file path where to copy the file
    """
    try:
        shutil.copy(
            input_filepath,
            output_filepath,
        )
    except:
        print(f"{output_filepath} not copied")


def copy_label_file(input_image: Union[str, PathLike], input_label: Union[str, PathLike],
                    output_filepath: Union[str, PathLike]):
    """
    Copy label file, verifying the image information (spacing, orientation).

    Parameters
    ----------
    input_image :
        file path for the input image, to be used as reference when copying image information
    input_label :
        file path for the input label to be copied
    output_filepath :
        file location where to save the label image
    """
    try:
    
    
        label_nib = nib.load(input_label)
        image_nib = nib.load(input_image)
    
        label_nib_out = nib.Nifti1Image(label_nib.get_fdata(), image_nib.affine)
        nib.save(label_nib_out, output_filepath)
    except:
        print(f"{output_filepath} not created")


def copy_data_from_dict_to_dataset_folder(
        input_data_file: Union[str, PathLike],
        step: str,
        image_folder: Union[str, PathLike],
        config_dict: Dict[str, object],
        label_folder: Union[str, PathLike] = None,
        num_threads: int = None,
        save_label_instance_config: bool = False,
):
    """

    Parameters
    ----------

    input_data_file :
        JSON dict path of the input dataset
    step :
        string list for the step of the dataset (train/test).
    image_folder :
        folder path where to store images (imagesTr/imagesTs).
    config_dict :
        dictionary with dataset and experiment configuration parameters.
    label_folder :
        folder path where to store labels (labelsTr/labelsTs). Default: ``None``.
        If **label_suffix** is ``None``, the label files are not saved.
    num_threads :
        number of threads to use in multiprocessing ( Default: ``os.environ['N_THREADS']`` )
    save_label_instance_config :
        Flag to save label mask together with an instance dictionary as JSON file. NOTE: All the instances are assigned
         to instance class ``1``.
    """
    label_suffix = str(config_dict["label_suffix"])
    if num_threads is None:
        try:
            num_threads = int(os.environ["N_THREADS"])
        except KeyError:
            logger.warning("N_THREADS is not set as environment variable. Using Default [1]")
            num_threads = 1

    with open(input_data_file, "r") as file:
        input_data_dict = json.load(file)

    pool = Pool(num_threads)
    copied_files = []
    for subject in input_data_dict[step]:

        image_suffix_list = config_dict["Modalities"].keys()

        for modality, image_suffix in enumerate(image_suffix_list):
            modality_code = "_{0:04d}".format(modality)
            image_filename = subject[config_dict["Modalities"][image_suffix]]

            if Path(image_filename).is_file():
                updated_image_filename = Path(image_filename).name.replace(image_suffix,
                                                                           modality_code + str(
                                                                               config_dict["FileExtension"]))

                if Path(updated_image_filename).name ==  modality_code + str(
                                                                               config_dict["FileExtension"]):
                    parent_dir = Path(image_filename).parent.name
                    updated_image_filename = parent_dir  + modality_code + str(
                                                                               config_dict["FileExtension"])
                copied_files.append(
                    pool.starmap_async(
                        copy_image_file,
                        (
                            (
                                str(image_filename),
                                str(Path(image_folder).joinpath(updated_image_filename)),
                            ),
                        ),
                    )
                )
            else:
                logger.warning("{} is not found: skipping {} case".format(image_filename, image_filename))
        if "label" in subject and label_suffix is not None:

            label_filename = subject["label"]

            if Path(label_filename).is_file():

                updated_label_filename = Path(label_filename).name.replace(label_suffix,
                                                                           str(config_dict["FileExtension"]))


                if Path(updated_label_filename).name ==  str(
                                                                               config_dict["FileExtension"]):
                    parent_dir = Path(label_filename).parent.name
                    updated_label_filename =  parent_dir + str(
                                                                               config_dict["FileExtension"])
                copied_files.append(
                    pool.starmap_async(
                        copy_label_file,
                        (
                            (
                                str(image_filename),
                                str(label_filename),
                                str(Path(label_folder).joinpath(updated_label_filename)),
                            ),
                        ),
                    )
                )
                if save_label_instance_config:
                    label_map = SimpleITK.GetArrayFromImage(
                        SimpleITK.ReadImage(str(Path(label_filename)))
                    )
                    instances = np.unique(label_map)
                    instances = instances[instances > 0]

                    json_dict = {
                        "instances": {str(int(i)): 0 for i in instances},
                    }
                    save_config_json(json_dict,
                                     str(Path(label_folder).joinpath(
                                         Path(label_filename).name.replace(label_suffix, ".json"))))
            else:
                logger.warning("{} is not found: skipping {} case".format(label_filename, label_filename))

    _ = [i.get() for i in tqdm(copied_files)]

def copy_data_to_dataset_folder(
        input_data_folder: Union[str, PathLike],
        subjects: List[str],
        image_folder: Union[str, PathLike],
        config_dict: Dict[str, object],
        label_folder: Union[str, PathLike] = None,
        num_threads: int = None,
        save_label_instance_config: bool = False,
):
    """

    Parameters
    ----------

    input_data_folder :
        folder path of the input dataset
    subjects :
        string list containing subject IDs.
    image_folder :
        folder path where to store images (imagesTr/imagesTs).
    config_dict :
        dictionary with dataset and experiment configuration parameters.
    label_folder :
        folder path where to store labels (labelsTr/labelsTs). Default: ``None``.
        If **label_suffix** is ``None``, the label files are not saved.
    num_threads :
        number of threads to use in multiprocessing ( Default: ``os.environ['N_THREADS']`` )
    save_label_instance_config :
        Flag to save label mask together with an instance dictionary as JSON file. NOTE: All the instances are assigned
         to instance class ``1``.
    """
    label_suffix = str(config_dict["label_suffix"])
    if num_threads is None:
        try:
            num_threads = int(os.environ["N_THREADS"])
        except KeyError:
            logger.warning("N_THREADS is not set as environment variable. Using Default [1]")
            num_threads = 1

    pool = Pool(num_threads)
    copied_files = []
    for directory in subjects:

        files = subfiles(
            str(Path(input_data_folder).joinpath(directory)),
            join=False,
            suffix=str(config_dict["FileExtension"]),
        )

        image_suffix_list = config_dict["Modalities"].keys()

        for modality, image_suffix in enumerate(image_suffix_list):
            modality_code = "_{0:04d}".format(modality)
            image_filename = directory + image_suffix

            if image_filename in files:
                updated_image_filename = image_filename.replace(image_suffix,
                                                                modality_code + str(config_dict["FileExtension"]))




                if Path(updated_image_filename).name ==  modality_code + str(
                                                                               config_dict["FileExtension"]):
                    parent_dir = Path(image_filename).parent.name
                    updated_image_filename = parent_dir + modality_code + str(
                                                                               config_dict["FileExtension"])
                copied_files.append(
                    pool.starmap_async(
                        copy_image_file,
                        (
                            (
                                str(Path(input_data_folder).joinpath(directory, image_filename)),
                                str(Path(image_folder).joinpath(updated_image_filename)),
                            ),
                        ),
                    )
                )
            else:
                logger.warning("{} is not found: skipping {} case".format(image_filename, directory))
        if label_suffix is not None and label_folder is not None and type(label_suffix) != list:

            label_filename = directory + label_suffix

            if label_filename in files:

                updated_label_filename = label_filename.replace(label_suffix, str(config_dict["FileExtension"]))

                if Path(updated_label_filename).name == str(
                        config_dict["FileExtension"]):
                    parent_dir = Path(label_filename).parent.name
                    updated_label_filename =  parent_dir + str(
                        config_dict["FileExtension"])

                copied_files.append(
                    pool.starmap_async(
                        copy_label_file,
                        (
                            (
                                str(Path(input_data_folder).joinpath(directory, directory + image_suffix)),
                                str(Path(input_data_folder).joinpath(directory, directory + label_suffix)),
                                str(Path(label_folder).joinpath(updated_label_filename)),
                            ),
                        ),
                    )
                )
                if save_label_instance_config:
                    label_map = SimpleITK.GetArrayFromImage(
                        SimpleITK.ReadImage(str(Path(input_data_folder).joinpath(directory, directory + label_suffix)))
                    )
                    instances = np.unique(label_map)
                    instances = instances[instances > 0]

                    json_dict = {
                        "instances": {str(int(i)): 0 for i in instances},
                    }
                    save_config_json(json_dict,
                                     str(Path(label_folder).joinpath(label_filename.replace(label_suffix, ".json"))))
            else:
                logger.warning("{} is not found: skipping {} case".format(label_filename, directory))

        elif type(label_suffix) == list and label_folder is not None:  # Multi Label
            for task_id, label_s in enumerate(label_suffix):
                task_code = "_{0:04d}".format(task_id)
                label_filename = directory + label_s

                if label_filename in files:

                    updated_label_filename = label_filename.replace(label_s,
                                                                    task_code + str(config_dict["FileExtension"]))

                    copied_files.append(
                        pool.starmap_async(
                            copy_label_file,
                            (
                                (
                                    str(Path(input_data_folder).joinpath(directory, directory + image_suffix)),
                                    str(Path(input_data_folder).joinpath(directory, directory + label_s)),
                                    str(Path(label_folder).joinpath(updated_label_filename)),
                                ),
                            ),
                        )
                    )
                else:
                    logger.warning("{} is not found: skipping {} case".format(label_filename, directory))

    _ = [i.get() for i in tqdm(copied_files)]


def save_config_json(config_dict: Dict[str, object], output_json: Union[str, PathLike]):
    """
    Save dictionary as JSON file.

    Parameters
    ----------
    output_json :
        JSON file path to be saved
    config_dict:
        dictionary to be saved in JSON format in the RESULTS_FOLDER
    """

    with open(output_json, "w") as fp:
        json.dump(config_dict, fp)


def generate_dataset_json(
        output_file: Union[str, PathLike],
        train_subjects: List[str],
        test_subjects: List[str],
        modalities: Tuple,
        labels: Union[Dict, List],
        task_name: str,
        file_extension: str,
        region_class_order=None,
        nnunet_format: bool = False,
):
    """
    Generates and saves a Dataset JSON file.

    Parameters
    ----------
    nnunet_format   :
        Flag to specify which modality key to use.
    file_extension  :
        Dataset file extension
    output_file :
        This needs to be the full path to the dataset.json you intend to write, so
    output_file='DATASET_PATH/dataset.json' where the folder DATASET_PATH points to is the one with the
    imagesTr and labelsTr subfolders.
    train_subjects :
        List of subjects in the train set.
    test_subjects :
        List of subjects in the test set.
    modalities :
        tuple of strings with modality names. must be in the same order as the images (first entry
    corresponds to _0000.nii.gz, etc). Example: ('T1', 'T2', 'FLAIR').
    labels :
        dict with int->str (key->value) mapping the label IDs to label names. Note that 0 is always
    supposed to be background! Example: {0: 'background', 1: 'edema', 2: 'enhancing tumor'}. In case of a multi label task,
        the dictionaries for each label task are nested into a list.
    task_name :
        The name of the dataset.
    region_class_order :
        Optional list of strings with the region class order, used for region-based training. Default: ``None``.
    """
    modality_key = "modalities"
    if nnunet_format:
        modality_key = "channel_names"
    json_dict = {
        "task": task_name,
        "dim": 3,
        "test_labels": True,
        "tensorImageSize": "4D",
        modality_key: {str(i): modalities[i] for i in range(len(modalities))},
        "labels": labels,  # {str(i): labels[i] for i in labels.keys()},
        "numTraining": len(train_subjects),
        "numTest": len(test_subjects),
        "training": [{"image": "./imagesTr/%s.nii.gz" % i, "label": "./labelsTr/%s.nii.gz" % i} for i in
                     train_subjects],
        "test": ["./imagesTs/%s.nii.gz" % i for i in test_subjects],
        "file_ending": file_extension,
    }
    if region_class_order:
        json_dict["regions_class_order"] = region_class_order

    if not str(output_file).endswith("dataset.json"):
        print(
            "WARNING: output file name is not dataset.json! This may be intentional or not. You decide. "  # noqa: E501
            "Proceeding anyways..."
        )
    save_config_json(json_dict, output_file)


def remove_empty_folder_recursive(folder_path: Union[str, PathLike]):
    """
    Recursively removes all the empty subdirectories of the root folder.

    Parameters
    ----------
    folder_path :
        Root folder path.
    """
    for subfolder_path in Path(folder_path).glob("*"):
        if Path(subfolder_path).is_dir():
            try:
                os.rmdir(subfolder_path)
            except FileNotFoundError as e:
                logger.log(WARN, e)
            except OSError as e:
                logger.log(WARN, e)
                remove_empty_folder_recursive(subfolder_path)
                os.rmdir(subfolder_path)


def order_data_in_single_folder(
        root_path: Union[str, PathLike],
        output_path: Union[str, PathLike],
        assign_parent_dir_name: bool = False,
        file_extension: str = "",
):
    """
    Moves all the sub-files, found iteratively from the root directory, to the output folder.
    Recursively removes all the empty subdirectories.
    If the *assign_parent_dir_name* flag is set to True, the parent directory name for each file will be used as suffix
    appended to the filename (used when images and masks are divided in different subfolders).

    Parameters
    ----------
    file_extension  :
        File extension for the files in the selected folder.
    assign_parent_dir_name  :
        Flag to set if to assign the parent directory name as suffix.
    root_path   :
        Root folder.
    output_path :
        Output folder.
    """
    logger.log(DEBUG, "Creating folder at '{}'".format(output_path))
    search_regex = "*/*"
    if assign_parent_dir_name:
        search_regex = "*/*/*"

    search_regex = "*/*"
    for file_path in Path(root_path).glob(search_regex):

        if assign_parent_dir_name:

            logger.log(
                DEBUG,
                "Moving '{}' file to '{}'".format(
                    file_path,
                    Path(output_path).joinpath(
                        str(Path(file_path).name[: -len(file_extension)])
                        + "_"
                        + str(Path(file_path).parent.name)
                        + file_extension
                    ),
                ),
            )
            Path(file_path).rename(
                Path(output_path).joinpath(
                    str(Path(file_path).name[: -len(file_extension)]) + "_" + str(
                        Path(file_path).parent.name) + file_extension
                )
            )
        else:
            logger.log(DEBUG,
                       "Moving '{}' file to '{}'".format(file_path, Path(output_path).joinpath(Path(file_path).name)))
            Path(file_path).rename(Path(output_path).joinpath(Path(file_path).name))
    
    if root_path == output_path:
        logger.log(DEBUG, "Removing empty folders at '{}'".format(root_path))
        remove_empty_folder_recursive(root_path)


def order_data_folder_by_patient(folder_path: Union[str, PathLike], file_pattern: str):
    """
    Order all the files in the root folder into corresponding subdirectories, according to the specified
    file pattern.

    Parameters
    ----------
    folder_path :
        Root folder path.
    file_pattern    :
        File pattern to group the files and create the corresponding subdirectories.
    """
    patient_id_list = []
    for file_path in Path(folder_path).glob("*"):
        if Path(file_path).is_file() and str(file_path).endswith(file_pattern):
            patient_id_list.append(str(file_path.name)[: -len(file_pattern)])

    logger.log(INFO, "Patient folders in database: {}".format(len(patient_id_list)))

    for patient_id in patient_id_list:
        logger.log(DEBUG, "Creating folder at '{}'".format(Path(folder_path).joinpath(patient_id)))
        Path(folder_path).joinpath(patient_id).mkdir(exist_ok=True, parents=True)

    for file_path in Path(folder_path).glob("*"):
        if Path(file_path).is_file():
            matching_patient_ids = []
            for patient_id in patient_id_list:
                
                if file_path.name.startswith(patient_id):
                    matching_patient_ids.append(patient_id)
                
            if len(matching_patient_ids) > 1:
                logger.log(WARN, "Multiple patient IDs found for file: {}".format(file_path))
                logger.log(WARN, "Matching patient IDs: {}".format(matching_patient_ids))
                logger.log(WARN, "Selecting the longest ID: {}".format(max(matching_patient_ids, key=len)))
                matching_patient_id = max(matching_patient_ids, key=len)
                logger.log(
                    DEBUG,
                    "Moving '{}' file to '{}'".format(
                        file_path, Path(folder_path).joinpath(matching_patient_id, Path(file_path).name)
                    ),
                )
                Path(file_path).rename(Path(folder_path).joinpath(matching_patient_id, Path(file_path).name))
            elif len(matching_patient_ids) == 1:
                logger.log(
                    DEBUG,
                    "Moving '{}' file to '{}'".format(
                        file_path, Path(folder_path).joinpath(matching_patient_ids[0], Path(file_path).name)
                    ),
                )
                Path(file_path).rename(Path(folder_path).joinpath(matching_patient_ids[0], Path(file_path).name))


def copy_subject_folder_to_data_folder(
        input_data_folder: Union[str, PathLike], subjects: List[str], data_folder: Union[str, PathLike]
):
    """
    Copy all the specified subject sub-folders to a new data folder.

    Parameters
    ----------
    input_data_folder :
        Input data folder.
    subjects    :
        Subjects to copy.
    data_folder :
        Destination data folder.
    """
    Path(data_folder).mkdir(parents=True, exist_ok=True)
    for subject in subjects:
        if Path(input_data_folder).joinpath(subject).is_dir():
            logger.log(DEBUG, "Copying Subject {}".format(subject))
            copy_tree(str(Path(input_data_folder).joinpath(subject)), str(Path(data_folder).joinpath(subject)))


def convert_nifti_pred_to_dicom_seg(
        nifti_pred_file: Union[str, PathLike],
        patient_dicom_folder: Union[str, PathLike],
        template_file: Union[str, PathLike],
        output_dicom_seg: Union[str, PathLike],
        study_id,
):
    """
    Convert a NIFTI prediction file (segmentation mask), into a single DICOM SEG file. ``patient_dicom_folder`` and
    ``template_file`` are used to extract DICOM metadata and information to use when saving the DICOM SEG file.

    Parameters
    ----------
    study_id    :
        Study ID used to match the appropriate DICOM folder.
    nifti_pred_file :
        NIFTI prediction file (segmentation mask) to convert.
    patient_dicom_folder :
        Original patient DICOM folder, used to retrieve DICOM Metadata.
    template_file :
        Template JSON file for the prediction model/algorithm used. Generated from : http://qiicr.org/dcmqi/#/home
    output_dicom_seg :
        Output DICOM SEG file to save.
    """
    segmentation = SimpleITK.ReadImage(nifti_pred_file)
    reader = SimpleITK.ImageSeriesReader()

    studies = subfolders(Path(patient_dicom_folder), join=False)

    dcm_files = None
    for study in studies:
        series = subfolders(Path(patient_dicom_folder).joinpath(studies[0]), join=False)
        for serie in series:
            first_file = next(Path(patient_dicom_folder).joinpath(studies[0], serie).glob("*.dcm"))
            ds = pydicom.dcmread(str(first_file))
            if ds.Modality != "SEG" and ds.StudyInstanceUID == study_id and dcm_files is None:
                dcm_files = reader.GetGDCMSeriesFileNames(str(Path(patient_dicom_folder).joinpath(study, serie)))

    template = pydicom_seg.template.from_dcmqi_metainfo(template_file)
    writer = pydicom_seg.MultiClassWriter(
        template=template,
        inplane_cropping=False,
        skip_empty_slices=False,
        skip_missing_segment=False,
    )

    source_images = [pydicom.dcmread(x, stop_before_pixels=True) for x in dcm_files]
    dcm = writer.write(segmentation, source_images)

    dcm.save_as(output_dicom_seg)
