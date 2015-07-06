Feature: Markdown
    The journal accepts Markdown syntax in entries and renders them properly.

Scenario: An authorized user can use Markdown in an entry
    Given an authenticated user
    When the user creates an entry
    Then they can use Markdown to format the entry
