import os
from pathlib import Path

from constants import Dataset, PrintTemplate

SUPPLIER_TO_SFTP_DIRECTORY = {
    'QM': os.getenv('SFTP_QM_DIRECTORY'),
    'PPO': os.getenv('SFTP_PPO_DIRECTORY')

}

SUPPLIER_TO_KEY_PATH = {
    'QM': os.getenv('QM_PUBLIC_KEY_PATH') or str(
        Path(__file__).parents[0].joinpath('dummy_keys', 'supplier_QM_dummy_public_key.asc')),
    'PPO': os.getenv('PPO_PUBLIC_KEY_PATH') or str(
        Path(__file__).parents[0].joinpath('dummy_keys', 'supplier_PPO_dummy_public_key.asc'))
}

SUPPLIER_TO_PRIVATE_KEY_PATH = {
    'QM': 'dummy_keys/supplier_QM_dummy_private_key.asc',
    'PPO': 'dummy_keys/supplier_PPO_dummy_private_key.asc'
}

SUPPLIER_TO_PRINT_TEMPLATE = {
    'QM': PrintTemplate.QM_PRINT_FILE_TEMPLATE,
    'PPO': PrintTemplate.PPD_PRINT_FILE_TEMPLATE
}

PRODUCTPACK_CODE_TO_DATASET = {
    'D_FD_H1': Dataset.QM3_1,
    'D_FD_H2': Dataset.QM3_1,
    'D_FD_H2W': Dataset.QM3_1,
    'D_FD_H4': Dataset.QM3_1,
    'D_FD_HC1': Dataset.QM3_1,
    'D_FD_HC2': Dataset.QM3_1,
    'D_FD_HC2W': Dataset.QM3_1,
    'D_FD_HC4': Dataset.QM3_1,
    'D_FD_I1': Dataset.QM3_1,
    'D_FD_I2': Dataset.QM3_1,
    'D_FD_I2W': Dataset.QM3_1,
    'D_FD_I4': Dataset.QM3_1,
    'D_CCS_CH1': Dataset.QM3_1,
    'D_CCS_CH2W': Dataset.QM3_1,
    'D_CCS_CHP1': Dataset.QM3_1,
    'D_CCS_CHP2W': Dataset.QM3_1,
    'D_CCS_CCP1': Dataset.QM3_1,
    'D_CCS_CCP2W': Dataset.QM3_1,
    'D_CCS_CCE1': Dataset.QM3_1,
    'D_CCS_CCE2W': Dataset.QM3_1,
    'D_FDCE_H1U': Dataset.QM3_1,
    'D_FDCE_H2U': Dataset.QM3_1,
    'D_FDCE_H2UW': Dataset.QM3_1,
    'D_FDCE_I1U': Dataset.QM3_1,
    'D_FDCE_I2U': Dataset.QM3_1,
    'D_FDCE_I2UW': Dataset.QM3_1,
    'D_CE1U_ICLCR1': Dataset.PPD1_6,
    'D_CE1U_ICLCR2B': Dataset.PPD1_6,
    'D_ICU_ICLR1': Dataset.PPD1_6,
    'D_ICU_ICLR2B': Dataset.PPD1_6,
    'D_ICCE_ICL1': Dataset.PPD1_6,
    'D_ICCE_ICL2B': Dataset.PPD1_6

}

PRODUCTPACK_CODE_TO_DESCRIPTION = {
    'D_FD_H1': 'Household Questionnaire pack for England',
    'D_FD_H2': 'Household Questionnaire pack for Wales (English)',
    'D_FD_H2W': 'Household Questionnaire pack for Wales (Welsh)',
    'D_FD_H4': 'Household Questionnaire pack for Northern Ireland (English)',
    'D_FD_HC1': 'Continuation Questionnaire pack for England',
    'D_FD_HC2': 'Continuation Questionnaire pack for Wales (English)',
    'D_FD_HC2W': 'Continuation Questionnaire pack for Wales (Welsh)',
    'D_FD_HC4': 'Continuation Questionnaire pack for Northern Ireland (English)',
    'D_FD_I1': 'Individual Questionnaire pack for England',
    'D_FD_I2': 'Individual Questionnaire pack for Wales (English)',
    'D_FD_I2W': 'Individual Questionnaire pack for Wales (Welsh)',
    'D_FD_I4': 'Individual Questionnaire pack for Northern Ireland (English)',
    'D_CCS_CH1': 'CCS Interviewer Household Questionnaire for England and Wales',
    'D_CCS_CH2W': 'CCS Interviewer Household Questionnaire for Wales (Welsh)',
    'D_CCS_CHP1': 'CCS Postback Questionnaire for England and Wales (English)',
    'D_CCS_CHP2W': 'CCS Postback Questionnaire for Wales (Welsh)',
    'D_CCS_CCP1': 'CCS Postback Continuation Questionnaire for England & Wales',
    'D_CCS_CCP2W': 'CCS Postback Continuation Questionnaire for Wales (Welsh)',
    'D_CCS_CCE1': 'CCS Interviewer CE Manager for England & Wales (English)',
    'D_CCS_CCE2W': 'CCS Interviewer CE Manager for Wales (Welsh)',
    'D_FDCE_H1U': 'Household Questionnaire for England (UNADDRESSED)',
    'D_FDCE_H2U': 'Household Questionnaire for Wales (UNADDRESSED) (English) (CE)',
    'D_FDCE_H2UW': 'Household Questionnaire for Wales (UNADDRESSED) (Welsh) (CE)',
    'D_FDCE_I1U': 'Individual Questionnaire for England (UNADDRESSED)',
    'D_FDCE_I2U': 'Individual Questionnaire for Wales (UNADDRESSED) (English)',
    'D_FDCE_I2UW': 'Individual Questionnaire for Wales (UNADDRESSED) (Welsh)',
    'D_CE1U_ICLCR1': 'CE1 Packs (Hand Delivery) Unaddressed England',
    'D_CE1U_ICLCR2B': 'CE1 Packs (Hand Delivery) Unaddressed Wales',
    'D_ICU_ICLR1': 'ICL with UAC Individual (Hand Delivery) Unaddressed England',
    'D_ICU_ICLR2B': 'ICL with UAC Individual (Hand Delivery) Unaddressed Wales',
    'D_ICCE_ICL1': 'ICL with UAC HH (Hand delivery) Unaddressed England',
    'D_ICCE_ICL2B': 'ICL with UAC HH (Hand Delivery) Unaddressed Wales'
}
