Feature: Generate valid print files
  The batch runner can request an unaddressed QID/UAC batch and subsequently generate valid print files from it

  Scenario Outline: Generate print files from a QID/UAC batch
    Given a QID batch has been generated from "<sample_file>" and expected uacs to be "<expected_uacs>"
    When the print files are generated for "<supplier>"
    Then the "<file_count>" print files contents are valid for the "<supplier>"

    Examples:
      | sample_file                         | expected_uacs | file_count | supplier |
      | acceptance_test_batch.csv           | 40            | 4          | QM       |
      | acceptance_test_ce_batch.csv        | 60            | 6          | QM       |
      | acceptance_test_batch_hh_global.csv | 20            | 2          | PPO      |
