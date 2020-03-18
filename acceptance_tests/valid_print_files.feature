Feature: Generate valid print files
  The batch runner can request an unaddressed QID/UAC batch and subsequently generate valid print files from it

  Scenario Outline: Generate print files from a QID/UAC batch
    Given a QID batch has been generated from "<sample_file>" and expected uacs to be "<expected_uacs>"
    When the print files are generated
    Then the "<manifest_count>" print files contents are valid

    Examples:
      | sample_file                  | expected_uacs | manifest_count |
      | acceptance_test_batch.csv    | 40            | 4              |
      | acceptance_test_ce_batch.csv | 40            | 4              |
