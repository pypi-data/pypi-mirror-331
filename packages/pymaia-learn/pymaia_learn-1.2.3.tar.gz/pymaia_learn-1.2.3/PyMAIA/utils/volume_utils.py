import math
import shutil
import tempfile
import time
from os import PathLike
from pathlib import Path
from typing import Union, Dict

import SimpleITK as sitk
import dicom2nifti
import nibabel as nib
import numpy as np
import pydicom
import pydicom_seg
from nilearn.image import resample_to_img
from pydicom import dcmread

from PyMAIA.utils.file_utils import subfolders
from PyMAIA.utils.log_utils import get_logger

logger = get_logger(__name__)


def dcm2nii_CT(CT_dcm_path: Union[str, PathLike], nii_out_path: Union[str, PathLike]):
    """
    Conversion of CT DICOM to nifti and save in nii_out_path.

    Parameters
    ----------
    CT_dcm_path :
        CT DICOM folder path.
    nii_out_path :
        Output NIFTI file path.
    """

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(str(tmp))
        dicom2nifti.convert_directory(CT_dcm_path, str(tmp), compression=True, reorient=True)
        nii = next(tmp.glob("*nii.gz"))
        shutil.copy(nii, nii_out_path)


def dcm2nii_seg(mask_dcm_path: Union[str, PathLike], nii_out_path: Union[str, PathLike], ref_nii_path: Union[str]):
    """
    Conversion of SEG DICOM to NIFTI, using a reference NIFTI image.

    Parameters
    ----------
    mask_dcm_path :
        SEG DICOM folder.
    nii_out_path :
        NIFTI file saved as output.
    ref_nii_path :
        Reference NIFTI used to correctly saved the segmentation volume.
    """
    dcm = pydicom.dcmread(mask_dcm_path)

    reader = pydicom_seg.MultiClassReader()
    result = reader.read(dcm)

    image_data = result.data  # directly available
    image = result.image  # lazy construction
    sitk.WriteImage(image, nii_out_path, True)

    input_image = nib.load(nii_out_path)
    reference_image = nib.load(ref_nii_path)
    resampled_image = resample_to_img(input_image, reference_image, fill_value=0)
    nib.save(resampled_image, nii_out_path)

def dcm2nii_mask(mask_dcm_path: Union[str, PathLike], nii_out_path: Union[str, PathLike], ref_nii_path: Union[str, PathLike]):
    """
    Converts a SEG DICOM volume into NIFTI format. Requires an existing NIFTI file to derive the corresponding affine transform.

    Parameters
    ----------
    mask_dcm_path :
        SEG DICOM folder.
    nii_out_path :
        NIFTI file saved as output.
    ref_nii_path :
        Reference NIFTI used to correctly saved the segmentation volume.
    """
    mask_dcm = list(mask_dcm_path.glob("*.dcm"))[0]
    mask = pydicom.read_file(str(mask_dcm))
    mask_array = mask.pixel_array

    mask_array = np.transpose(mask_array, (2, 1, 0))
    mask_orientation = mask[0x5200, 0x9229][0].PlaneOrientationSequence[0].ImageOrientationPatient
    if mask_orientation[4] == -1:
        mask_array = np.flip(mask_array, 1)

    # get affine matrix from the corresponding pet
    pet = nib.load(ref_nii_path)
    pet_affine = pet.affine

    # return mask as nifti object
    mask_out = nib.Nifti1Image(mask_array, pet_affine)
    nib.save(mask_out, nii_out_path)


def convert_DICOM_folder_to_NIFTI_image(patient_dicom_folder: Union[str, PathLike],
                                        patient_nifti_folder: Union[str, PathLike]) -> Dict[str, str]:
    """
    Converts a given Patient DICOM folder into NIFTI format, saving the DICOM Studies in different folders.

    Parameters
    ----------
    patient_dicom_folder :
        DICOM folder containing a single patient Studies.
    patient_nifti_folder :
        Output NIFTI folder used as stem to save the DICOM Studies. The Study index is appended to this path to create
        the corresponding NIFTI study folder path.

    Returns
    -------
    Dictionary mapping each Patient -> Study ID to the corresponding StudyInstanceUID
    """
    studies = subfolders(patient_dicom_folder, join=False)
    single_study = False
    if len(studies) == 1:
        single_study = True

    patient_study_map = {Path(patient_dicom_folder).name: {}}
    for study_id, study in enumerate(studies):
        if not single_study:
            Path(str(patient_nifti_folder) + "_{}".format(study_id)).mkdir(parents=True, exist_ok=True)
        else:
            Path(str(patient_nifti_folder)).mkdir(parents=True, exist_ok=True)
        series = subfolders(Path(patient_dicom_folder).joinpath(study), join=False)
        for serie in series:
            first_file = next(Path(patient_dicom_folder).joinpath(study, serie).glob("*.dcm"))
            ds = pydicom.dcmread(str(first_file))
            patient_study_map[Path(patient_dicom_folder).name][study_id] = str(ds['StudyInstanceUID'].value)

            if Path(patient_dicom_folder).name != ds['PatientName'].value:
                print(
                    f"WARNING! Patient name is different: {ds['PatientName'].value} instead of {Path(patient_dicom_folder).name}")

            if ds.Modality == "CT":
                if not single_study:
                    ct_filename = str(
                        Path(str(patient_nifti_folder) + "_{}".format(study_id)).joinpath(
                            "{}_{}_CT.nii.gz".format(Path(patient_dicom_folder).name, study_id)
                        )
                    )
                else:
                    ct_filename = str(
                        Path(str(patient_nifti_folder)).joinpath("{}_CT.nii.gz".format(Path(patient_dicom_folder).name))
                    )

                dcm2nii_CT(str(Path(patient_dicom_folder).joinpath(study, serie)), ct_filename)
            elif ds.Modality == "PT":
                if not single_study:
                    pet_filename = str(
                        Path(str(patient_nifti_folder) + "_{}".format(study_id)).joinpath(
                            "{}_{}_PET.nii.gz".format(Path(patient_dicom_folder).name, study_id)
                        )
                    )
                else:
                    pet_filename = str(
                        Path(str(patient_nifti_folder)).joinpath("{}_PET.nii.gz".format(Path(patient_dicom_folder).name))
                    )
                normalize_PET_to_SUV_BW(str(Path(patient_dicom_folder).joinpath(study, serie)), pet_filename)

    for study_id, study in enumerate(studies):
        series = subfolders(Path(patient_dicom_folder).joinpath(study), join=False)
        for serie in series:
            first_file = next(Path(patient_dicom_folder).joinpath(study, serie).glob("*.dcm"))
            ds = pydicom.dcmread(str(first_file))

            if ds.Modality == "SEG":
                if not single_study:
                    seg_filename = str(
                        Path(str(patient_nifti_folder) + "_{}".format(study_id)).joinpath(
                            "{}_{}_SEG.nii.gz".format(Path(patient_dicom_folder).name, study_id)
                        )
                    )
                    ref_filename = str(
                        Path(str(patient_nifti_folder) + "_{}".format(study_id)).joinpath(
                            "{}_{}_PET.nii.gz".format(Path(patient_dicom_folder).name, study_id)
                        )
                    )
                else:
                    seg_filename = str(
                        Path(str(patient_nifti_folder)).joinpath(
                            "{}_SEG.nii.gz".format(Path(patient_dicom_folder).name))
                    )
                    ref_filename = str(
                        Path(str(patient_nifti_folder)).joinpath(
                            "{}_PET.nii.gz".format(Path(patient_dicom_folder).name))
                    )
                dcm2nii_mask(Path(patient_dicom_folder).joinpath(study, serie), seg_filename, ref_filename)
    return patient_study_map

def normalize_PET_to_SUV_BW(dicom_pet_series_folder: Union[str, PathLike], suv_pet_filename: Union[str, PathLike]):
    """
    SUV BW Normalization of DICOM PET volume. The resulting normalized PET volume is saved at **suv_pet_filename**.

    Parameters
    ----------
    dicom_pet_series_folder :
        DICOM PET Folder to be normalized.
    suv_pet_filename:
        Normalized SUV PET file location.
    """
    reader = sitk.ImageSeriesReader()
    dicom_names = reader.GetGDCMSeriesFileNames(dicom_pet_series_folder)

    ds = dcmread(dicom_names[0])

    corrected_image = ds[0x0028, 0x0051].value
    decay_correction = ds[0x0054, 0x1102].value
    units = ds[0x0054, 0x1001].value

    series_date = ds.SeriesDate
    acquisition_date = ds.AcquisitionDate
    series_time = ds.SeriesTime
    acquisition_time = ds.AcquisitionTime
    half_life = ds.RadiopharmaceuticalInformationSequence[0].RadionuclideHalfLife
    weight = ds.PatientWeight

    if "ATTN" in corrected_image and "DECY" in corrected_image and decay_correction == "START":
        if units == "BQML":
            if series_time <= acquisition_time and series_date <= acquisition_date:
                scan_date = series_date
                scan_time = series_time
            else:
                scan_date = acquisition_date
                scan_time = acquisition_time
            # if not RadiopharmaceuticalStartTime in ds.RadiopharmaceuticalInformationSequence[0]:
            #    ...
            # else:
            start_time = ds.RadiopharmaceuticalInformationSequence[0].RadiopharmaceuticalStartTime
            start_date = scan_date

            scan_time = str(round(float(scan_time)))
            str_scan_time = time.strptime(scan_date + scan_time, "%Y%m%d%H%M%S")

            start_time = str(round(float(start_time)))

            str_start_time = time.strptime(start_date + start_time, "%Y%m%d%H%M%S")

            decay_time = time.mktime(str_scan_time) - time.mktime(str_start_time)

            injected_dose = ds.RadiopharmaceuticalInformationSequence[0].RadionuclideTotalDose
            decayed_dose = injected_dose * math.pow(2, -decay_time / half_life)

            SUB_BW_scale_factor = (weight * 1000) / decayed_dose

    rescale_slope = 1  # ds[0x0028,0x1053].value

    total_factor = rescale_slope * SUB_BW_scale_factor

    reader.SetFileNames(dicom_names)

    image = reader.Execute()

    image_array = sitk.GetArrayFromImage(image)

    image_array *= total_factor

    itk_image = sitk.GetImageFromArray(image_array)

    itk_image.CopyInformation(image)

    sitk.WriteImage(itk_image, suv_pet_filename)


def resample_image(nii_input_path: Union[str, PathLike], nii_ref_path: Union[str, PathLike],
                   nii_out_path: Union[str, PathLike]):
    """
    Resample Input NIFTI to match Reference NIFTI size and spacing.

    Parameters
    ----------
    nii_input_path  :
        Input NIFTI File Path.
    nii_ref_path    :
        Reference NIFTI File Path.
    nii_out_path
        Resampled Output NIFTI File Path.
    """
    # resample CT to PET and mask resolution
    input_image = nib.load(nii_input_path)
    reference_image = nib.load(nii_ref_path)
    resampled_image = resample_to_img(input_image, reference_image, fill_value=-1024)
    nib.save(resampled_image, nii_out_path)
