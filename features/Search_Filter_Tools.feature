Feature: Search and filter AI tools

  As a user browsing AI tools
  I want to search by name or keyword and apply filters
  So that I can quickly find tools that match my needs and view more details before visiting the tool's site.

  Background:
    Given I am on the AI Tools page

  Scenario: Basic search and filter flow
    When I search for "chat"
    And I apply filters:
      | filter   | value               |
      | category | AI Text Generators  |
      | pricing  | Freemium            |
    Then I see a list of tools matching "chat"
    And each listed tool shows the name, a short description, tags, and an external link

    When I expand the first tool in the results
    Then I see extended information including a full description, features, rating, and tags

    When I click the external link for the first tool
    Then the external link should open in a new tab or window (target="_blank")

    When I clear the search and reset filters
    Then I see the default (unfiltered) tools list

  Scenario: No results found suggests alternatives
    When I search for "nonexistent-tool-xyz"
    Then I see a "No results found" message
    And I see suggestions for popular categories or an option to clear filters

  Scenario: Invalid filter combination is prevented
    Given the UI provides filters for category and subcategory
    When I apply an invalid filter combination:
      | filter      | value                |
      | category    | AI Art Generators    |
      | subcategory | AI Text Generators   |
    Then I see a warning indicating the selected filters are incompatible
    And the system does not apply the invalid combination

  Scenario: External link unavailable shows an error and logs the failure
    Given there is a tool with an unreachable external URL
    When I click the external link for that tool
    Then I see an error notice explaining the link could not be opened
    And the failure is recorded for diagnostics
