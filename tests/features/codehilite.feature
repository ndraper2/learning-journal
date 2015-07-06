Feature: Markdown
    The journal adds code highlighting to code blocks.

Scenario: Code blocks are properly highlighted
    Given an anonymous user
    And an entry with a code block
    When they view the post
    Then the code block has syntax highlighting
