from enum import Enum


class Dataset(Enum):
    QM3_1 = 'QM3.1'
    PPD1_1 = 'PPD1.1'


class PrintTemplate:
    QM_PRINT_FILE_TEMPLATE = (
        'UAC', 'QUESTIONNAIRE_ID', 'WALES_UAC', 'WALES_QUESTIONNAIRE_ID', 'TITLE', 'COORDINATOR_ID', 'FORENAME',
        'SURNAME',
        'ADDRESS_LINE1', 'ADDRESS_LINE2', 'ADDRESS_LINE3', 'TOWN_NAME', 'POSTCODE', 'PRODUCTPACK_CODE')

    PPD_PRINT_FILE_TEMPLATE = ('UAC', 'CASE_REF', 'TITLE', 'FORENAME', 'SURNAME',
                               'ADDRESS_LINE1', 'ADDRESS_LINE2', 'ADDRESS_LINE3', 'TOWN_NAME', 'POSTCODE',
                               'PRODUCTPACK_CODE', 'QUESTIONNAIRE_ID',
                               'ORGANISATION_NAME', 'COORDINATOR_ID', 'OFFICER_ID')
