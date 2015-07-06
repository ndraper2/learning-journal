Feature: Edit
    The ability to edit an entry in the learning journal

Scenario: An authorized user can edit entries
    Given an authenticated user
    And an entry
    When the user visits the edit page
    Then they can edit the title and text of the entry
