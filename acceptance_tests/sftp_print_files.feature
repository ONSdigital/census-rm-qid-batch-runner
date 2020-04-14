Feature: Upload print files to a remote SFTP
  The batch runner can upload print files to a remote SFTP using SSH and a private key

  Scenario Outline: Upload generated print files to SFTP
    Given the print files have been previously generated from the "<sample_file>"
    And the correct SFTP config has been provided
    When the SFTP utility is used to copy the print files to the "<supplier>" directory
    Then the print files are present on the remote "<supplier>" SFTP

    Examples:
      | sample_file       | expected_uacs | manifest_count | supplier |
      | D_CCS_CH1_test    | 40            | 4              | QM       |
      | D_ICCE_ICL2B_test | 40            | 4              | PPO       |
