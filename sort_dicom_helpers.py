from ManageStudy.DICOM.series.DICOMseries_type import DICOMseries_type as DST
import re

def DICOMseries2study_subid(dicom_series, DICOM_subid_REC_dict={'mri':re.compile('^COGRES_([0-9]{4}).*', re.IGNORECASE),
                                                                'pet':re.compile('^BAY0596[_ -]+[0-9]{3}\^([0-9]{4}).*$', re.IGNORECASE)
                                                                }):
    result = re.search(DICOM_subid_REC_dict['mri'], dicom_series.PatientsName)
    if result != None:
        subid = result.group(1)
        return "P{0:08d}".format(int(subid))
    result = re.search(DICOM_subid_REC_dict['pet'], dicom_series.PatientsName)
    if result != None:
        subid = result.group(1)
        return "P{0:08d}".format(int(subid))
    return None

def DICOMseries2study_visid(dicom_series, DICOM_visid_REC_dict={'mri':re.compile('^COGRES_[0-9]{4}_?([0-9]*)$', re.IGNORECASE),
                                                                  'pet':re.compile('^BAY0596[_ -]+([0-9]{3})\^[0-9]{4}.*$', re.IGNORECASE)}):
    if dicom_series.subid == None:
        return None
    result = re.search(DICOM_visid_REC_dict['mri'], dicom_series.PatientsName)
    if result != None:
        visid = result.group(1)
        if visid == '':
            return "S{0:04d}".format(1)
        else:
            return "S{0:04d}".format(int(visid))
    result = re.search(DICOM_visid_REC_dict['pet'], dicom_series.PatientsName)
    if result != None:
        visid = result.group(1)
        #return "BAY0596_{0:03d}".format(int(visid))
        return "S{0:04d}".format(int(visid))
    return None

def DICOMseries2study_series_types(dicom_series, DICOMseries_type_list=[
                DST(name='pASL', series_desc_RE_list=['^ASL'], expected_image_quantity=2),
                DST(name='ECF_r1', series_desc_RE_list=['^ECFf_Run1'], expected_image_quantity=1),
                DST(name='ECF_r2', series_desc_RE_list=['^ECFf_Run2'], expected_image_quantity=1),
                DST(name='ECF_r3', series_desc_RE_list=['^ECFf_Run3'], expected_image_quantity=1),
                DST(name='ECF_r4', series_desc_RE_list=['^ECFf_Run4'], expected_image_quantity=1),
                DST(name='ECF_r5', series_desc_RE_list=['^ECFf_Run5'], expected_image_quantity=1),
                DST(name='ECF_r6', series_desc_RE_list=['^ECFf_Run6'], expected_image_quantity=1),
                DST(name='LS_r1', series_desc_RE_list=['^LS_RUN1'], expected_image_quantity=1),
                DST(name='LS_r2', series_desc_RE_list=['^LS_RUN2'], expected_image_quantity=1),
                DST(name='LS_r3', series_desc_RE_list=['^LS_RUN3'], expected_image_quantity=1),
                DST(name='Checkerboard_pASL_ACC', series_desc_RE_list=['^Checkerboard_ACC'], expected_image_quantity=1),
                DST(name='Checkerboard_pASL_V1', series_desc_RE_list=['^Checkerboard_V1'], expected_image_quantity=1),
                DST(name='T1', series_desc_RE_list=['^MPRAGE'], expected_image_quantity=1),
                DST(name='FLAIR', series_desc_RE_list=['^T2W_FLAIR'], expected_image_quantity=1),
                DST(name='REST_BOLD', series_desc_RE_list=['^RESTING'], expected_image_quantity=1),
                DST(name='DTI', series_desc_RE_list=['^WIP DTI|^DTI'], expected_image_quantity=1),
                DST(name='Survey', series_desc_RE_list=['Surv'], expected_image_quantity=1),
                DST(name='PET_Static', folder='PET', series_desc_RE_list=['^BAY[0-9]{4}_Static'], expected_image_quantity=1, expected_instances=74),
                DST(name='PET_Dynamic', folder='PET', series_desc_RE_list=['^BAY[0-9]{4}_Dynam'], expected_image_quantity=1, expected_instances=296),
                DST(name='AC_CT', folder='CT', series_desc_RE_list=['AC_CT'], expected_image_quantity=1, expected_instances=75)
              ]):
    if dicom_series.subid == None or dicom_series.visid == None:
        return None
    for series_type in DICOMseries_type_list:
        dicom_series.chk_add_DICOMseries_type(series_type)




def assign_series(DSR):
    for key1 in DSR.merged_series.iterkeys():
        for key2 in DSR.merged_series[key1].iterkeys():
            dti_list = []
            for key3 in DSR.merged_series[key1][key2].iterkeys():
                if key3 in DSR.merged_series[key1][key2]:

                        #remove data without series descriptions
                    if (DSR.merged_series[key1][key2][key3].SeriesDescription == None) or (DSR.merged_series[key1][key2][key3].SeriesDescription == ''):
                        DSR.merged_series[key1][key2][key3].delete_series_unsorted_files()

                        #delete bad data
                    elif (DSR.merged_series[key1][key2][key3].SeriesDescription.lower().find('xxxx') != -1):
                        DSR.merged_series[key1][key2][key3].delete_series_unsorted_files()

                        #delete derived data
                    elif int(DSR.merged_series[key1][key2][key3].SeriesNumber) > 100 and ((int(DSR.merged_series[key1][key2][key3].SeriesNumber) % 10) > 1):
                        DSR.merged_series[key1][key2][key3].delete_series_unsorted_files()

                    #delete PR data
                    elif DSR.merged_series[key1][key2][key3].Modality.upper() == 'PR':
                        DSR.merged_series[key1][key2][key3].delete_series_unsorted_files()

                        #skip if no series matched
                    elif (len(DSR.merged_series[key1][key2][key3].DICOMseries_types) == 0):
                        pass

                        #DTI handled specially
                    elif ('DTI' in DSR.merged_series[key1][key2][key3].DICOMseries_types):
                        dti_list.append(DSR.merged_series[key1][key2][key3])

                        #more than 1 match handled specially
                    elif (len(DSR.merged_series[key1][key2][key3].DICOMseries_types) > 1):
                        pass

                        #Survey data thrown out
                    elif ('Survey' in DSR.merged_series[key1][key2][key3].DICOMseries_types):
                        DSR.merged_series[key1][key2][key3].delete_series_unsorted_files()

                        #skip if number of instances too small
                    elif DSR.merged_series[key1][key2][key3].number_of_instances < DSR.merged_series[key1][key2][key3].DICOMseries_types.itervalues().next().expected_instances:
                        pass

                        #if only one series type matched and it was not one of the special ones above...
                    else:
                        #assign series if not previously assigned
                        if DSR.merged_series[key1][key2][key3].series == None:
                            DSR.merged_series[key1][key2][key3].series = DSR.merged_series[key1][key2][key3].DICOMseries_types.iterkeys().next()
            dti_list.sort(key=lambda x: x.SeriesNumber)
            for i in range(0, len(dti_list)):
                dti_name = "DTI_" + str(i + 1)
                dti_list[i].series = dti_name
                dti_list[i].DICOMseries_types.itervalues().next().folder = dti_name


