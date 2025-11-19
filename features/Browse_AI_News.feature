Feature: Browse AI news

  As a user
  I want to browse and search a feed of AI-related news
  So that I can keep up to date with the latest developments.

  Scenario: View recent AI news
    Given I am on the AI News page
    When the page loads
    Then I see a list of recent AI news items with titles and summaries

  Scenario: Open news details
    Given a news item is visible
    When I select the news item
    Then I see the full article and related links