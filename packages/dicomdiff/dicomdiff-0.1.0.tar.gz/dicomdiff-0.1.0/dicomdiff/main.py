import pydicom


def compare_dicom_datasets(original, deidentified):
    """
    Compares DICOM tags between an original DICOM file and a deidentified one.

    Args
    -----
        original_file (str): Path to the original DICOM file.
        deidentified_file (str): Path to the deidentified DICOM file.

    Returns
    -------
        list: A list of differences found between
        the original and deidentified DICOM files.
    """
    differences = []

    for elem in deidentified.iterall():
        tag = elem.tag
        name = elem.name

        # Check if the tag is also in the original file
        original_value = original.get(tag, None)
        deidentified_value = deidentified.get(tag, None)

        # If present in both, compare values
        if original_value is not None and deidentified_value is not None:
            if original_value != deidentified_value:
                differences.append(
                    {
                        "tag": tag,
                        "name": name,
                        "original_value": original_value,
                        "deidentified_value": deidentified_value,
                        "change_type": "Changed",
                    }
                )

        elif original_value is None:
            differences.append(
                {
                    "tag": tag,
                    "name": name,
                    "original_value": "Not Present in Original",
                    "deidentified_value": deidentified_value,
                    "change_type": "Created",
                }
            )

    for elem in original.iterall():
        tag = elem.tag
        original_value = original.get(tag, None)

        if original_value is not None:
            deidentified_value = deidentified.get(tag, None)
            if deidentified_value is None:
                differences.append(
                    {
                        "tag": tag,
                        "name": elem.name,
                        "original_value": original_value,
                        "deidentified_value": "Not Present in Deidentified",
                        "change_type": "Removed",
                    }
                )

    return differences


def compare_dicom_files(original_file, deidentified_file):
    original = pydicom.dcmread(original_file)
    deidentified = pydicom.dcmread(deidentified_file)
    return compare_dicom_datasets(original, deidentified)


def print_differences(differences):
    """
    Prints out the differences in a user-friendly format.

    Args
    ----
        differences (list): A list of differences.
    """
    if not differences:
        print("No differences found.")
        return

    for diff in differences:
        print("-" * 50)
        print(f"Tag: {diff['tag']}, Name: {diff['name']}")
        print(f"  Original Value: {diff['original_value']}")
        print(f"  Deidentified Value: {diff['deidentified_value']}")
        print(f"  Change Type: {diff['change_type']}")
