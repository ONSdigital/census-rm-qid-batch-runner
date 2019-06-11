Feature: Generate valid print files
  The batch runner can request an unaddressed QID/UAC batch and subsequently generate valid print files from it

  Scenario: Generate print files from a QID/UAC batch
    Given a QID batch has been generated
    When the print files are generated
    Then the contents of the print files are valid