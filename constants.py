from enum import Enum


class Dataset(Enum):
    QM3_1 = 'QM3.1'
    PPD1_1 = 'PPD1.1'
    PPD1_2 = 'PPD1.2'
    PPD1_3 = 'PPD1.3'
    PPD1_6 = 'PPD1.6'
    PPD1_7 = 'PPD1.7'
    PPD1_8 = 'PPD1.8'


class PrintTemplate:
    QM_PRINT_FILE_TEMPLATE = (
        'UAC', 'QUESTIONNAIRE_ID', 'WALES_UAC', 'WALES_QUESTIONNAIRE_ID', 'TITLE', 'COORDINATOR_ID', 'FORENAME',
        'SURNAME',
        'ADDRESS_LINE1', 'ADDRESS_LINE2', 'ADDRESS_LINE3', 'TOWN_NAME', 'POSTCODE', 'PRODUCTPACK_CODE')

    PPD_PRINT_FILE_TEMPLATE = ('UAC', 'CASE_REF', 'TITLE', 'FORENAME', 'SURNAME',
                               'ADDRESS_LINE1', 'ADDRESS_LINE2', 'ADDRESS_LINE3', 'TOWN_NAME', 'POSTCODE',
                               'PRODUCTPACK_CODE', 'QUESTIONNAIRE_ID',
                               'ORGANISATION_NAME', 'COORDINATOR_ID', 'OFFICER_ID')
