Feature: Detail
    One entry from the journal, selected by id

Scenario: The Detail page displays an entry for an anonymous user
    Given an anonymous user
    And a journal entry
    When the user visits the detail page for that entry
    Then they see the one entry
