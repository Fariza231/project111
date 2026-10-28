Feature: Coffee maker user stories
  The machine offers six services, maintains at most three unique recipes,
  displays ingredient quantities and sells a drink for its stated price.
  All interactions use the public command interface.

  Background:
    Given a new coffee maker with an empty recipe book

  @waiting
  Scenario Outline: Select each service from the waiting state
    Then the current mode is WAITING
    When I choose menu service <service>
    Then the current mode is <mode>

    Examples:
      | service | mode              |
      | 1       | ADD_RECIPE        |
      | 2       | DELETE_RECIPE     |
      | 3       | EDIT_RECIPE       |
      | 4       | ADD_INVENTORY     |
      | 5       | CHECK_INVENTORY   |
      | 6       | PURCHASE_BEVERAGE |

  @add
  Scenario: Register a recipe and preserve its information
    When I register "Coffee" priced 50 with 3 coffee 1 milk 2 sugar 0 chocolate
    Then the last status is OK
    And the current mode is WAITING
    And there are 1 registered recipes
    And recipe "Coffee" costs 50 and requires 3 coffee 1 milk 2 sugar 0 chocolate

  @add
  Scenario: Three recipes fit but a fourth does not
    Given three standard recipes have been registered
    When I register "Fourth" priced 40 with 1 coffee 1 milk 1 sugar 1 chocolate
    Then the last status is RECIPE_NOT_ADDED
    And the current mode is WAITING
    And there are 3 registered recipes
    And recipe "Coffee" costs 50 and requires 3 coffee 1 milk 1 sugar 0 chocolate
    And recipe "Latte" costs 70 and requires 2 coffee 3 milk 1 sugar 0 chocolate
    And recipe "Mocha" costs 90 and requires 2 coffee 2 milk 1 sugar 3 chocolate

  @add
  Scenario: Duplicate names are rejected without replacing the first recipe
    When I register "Coffee" priced 50 with 3 coffee 1 milk 1 sugar 0 chocolate
    And I register "Coffee" priced 99 with 9 coffee 9 milk 9 sugar 9 chocolate
    Then the last status is RECIPE_NOT_ADDED
    And the current mode is WAITING
    And there are 1 registered recipes
    And recipe "Coffee" costs 50 and requires 3 coffee 1 milk 1 sugar 0 chocolate

  @delete
  Scenario: Deleting an existing recipe removes only that recipe
    Given three standard recipes have been registered
    When I remove recipe "Latte"
    Then the last status is OK
    And the current mode is WAITING
    And recipe "Latte" is no longer listed
    And there are 2 registered recipes
    And recipe "Coffee" costs 50 and requires 3 coffee 1 milk 1 sugar 0 chocolate
    And recipe "Mocha" costs 90 and requires 2 coffee 2 milk 1 sugar 3 chocolate

  @delete
  Scenario: Deletion makes room for a replacement
    Given three standard recipes have been registered
    When I remove recipe "Latte"
    Then the last status is OK
    When I register "Replacement" priced 40 with 1 coffee 2 milk 3 sugar 4 chocolate
    Then the last status is OK
    And the current mode is WAITING
    And there are 3 registered recipes
    And recipe "Replacement" costs 40 and requires 1 coffee 2 milk 3 sugar 4 chocolate

  @edit
  Scenario: Editing changes the price and ingredients but not the recipe name
    Given three standard recipes have been registered
    When I edit "Latte" submitting name "Different" price 85 and 1 coffee 2 milk 3 sugar 4 chocolate
    Then the last status is OK
    And the current mode is WAITING
    And there are 3 registered recipes
    And recipe "Latte" costs 85 and requires 1 coffee 2 milk 3 sugar 4 chocolate
    And recipe "Different" is no longer listed

  @inventory
  Scenario: Each delivered ingredient increases its own stock
    When I replenish 2 coffee 3 milk 4 sugar 5 chocolate
    Then the last status is OK
    And the current mode is WAITING
    And the displayed stock is 17 coffee 18 milk 19 sugar 20 chocolate

  @inventory
  Scenario: Separate inventory deliveries accumulate
    When I replenish 2 coffee 3 milk 4 sugar 5 chocolate
    Then the last status is OK
    When I replenish 1 coffee 2 milk 3 sugar 4 chocolate
    Then the last status is OK
    And the current mode is WAITING
    And the displayed stock is 18 coffee 20 milk 22 sugar 24 chocolate

  @check
  Scenario: Checking inventory reports stock without consuming it
    Then the displayed stock is 15 coffee 15 milk 15 sugar 15 chocolate
    And the displayed stock is 15 coffee 15 milk 15 sugar 15 chocolate
    And the current mode is WAITING

  @purchase
  Scenario: Buy a drink with exact payment
    When I register "Drink" priced 50 with 2 coffee 3 milk 4 sugar 5 chocolate
    And I pay 50 and buy "Drink"
    Then the last status is OK
    And the current mode is WAITING
    And the change tray contains 0
    And the inserted balance is 0
    And the displayed stock is 13 coffee 12 milk 11 sugar 10 chocolate

  @purchase
  Scenario: Buy a drink and receive the correct change
    When I register "Drink" priced 50 with 2 coffee 3 milk 4 sugar 5 chocolate
    And I pay 75 and buy "Drink"
    Then the last status is OK
    And the current mode is WAITING
    And the change tray contains 25
    And the inserted balance is 0
    And the displayed stock is 13 coffee 12 milk 11 sugar 10 chocolate
    When I empty the change tray
    Then the change tray contains 0

  @purchase
  Scenario: The chosen drink determines the price and ingredients
    Given three standard recipes have been registered
    When I pay 100 and buy "Mocha"
    Then the last status is OK
    And the current mode is WAITING
    And the change tray contains 10
    And the inserted balance is 0
    And the displayed stock is 13 coffee 13 milk 14 sugar 12 chocolate
