Feature: Upload print files to a remote SFTP
  The batch runner can upload print files to a remote SFTP using SSH and a private key

  Scenario: Upload generated print files to SFTP
    Given the print files have been previously generated
    And the correct SFTP config has been provided
    When the SFTP utility is used to copy the print files
    Then the print files are present on the remote SFTP