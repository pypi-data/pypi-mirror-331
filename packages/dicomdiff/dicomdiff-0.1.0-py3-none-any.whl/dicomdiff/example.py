from dicomdiff.core import compare_dicom_files, print_differences

original_file = "../original.dcm"
deidentified_file = "../deidentified.dcm"

result = compare_dicom_files(original_file, deidentified_file)
print(print_differences(result))