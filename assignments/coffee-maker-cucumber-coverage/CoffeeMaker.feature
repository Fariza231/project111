Feature: Coffee maker user stories through the command interface
  Users manage at most three unique recipes, replenish and check stock,
  and purchase drinks with correct ingredient consumption and returned money.
  Recipe indices in the UI command API are zero based.

  Background:
    Given a fresh coffee maker

  @waiting
  Scenario Outline: Each main-menu selection enters its service mode
    When I select service <button>
    Then the machine mode is <mode>
    And the operation status is OK

    Examples:
      | button | mode              |
      | 1      | ADD_RECIPE        |
      | 2      | DELETE_RECIPE     |
      | 3      | EDIT_RECIPE       |
      | 4      | ADD_INVENTORY     |
      | 5      | CHECK_INVENTORY   |
      | 6      | PURCHASE_BEVERAGE |
      | 0      | WAITING           |
      | -1     | WAITING           |
      | 7      | WAITING           |

  @waiting
  Scenario: A new machine waits with no recipes or money
    Then the machine mode is WAITING
    And the operation status is OK
    And the recipe book contains 0 recipes
    And the inserted money is 0
    And the return tray contains 0 money units

  @add
  Scenario: Add a recipe and preserve every field
    When I add recipe "Coffee" priced 50 using 3 coffee 1 milk 2 sugar 0 chocolate
    Then the operation status is OK
    And the machine mode is WAITING
    And the recipe book contains 1 recipes
    And recipe at index 0 is "Coffee" priced 50 using 3 coffee 1 milk 2 sugar 0 chocolate
    And the inventory report shows 15 coffee 15 milk 15 sugar 15 chocolate

  @add
  Scenario: The fourth distinct recipe is rejected
    Given the standard three recipes are available
    When I add recipe "Fourth" priced 40 using 1 coffee 1 milk 1 sugar 1 chocolate
    Then the operation status is RECIPE_NOT_ADDED
    And the machine mode is WAITING
    And the recipe book contains 3 recipes
    And recipe at index 0 is "Coffee" priced 50 using 3 coffee 1 milk 1 sugar 0 chocolate

  @add
  Scenario: A duplicate recipe name does not replace the original
    When I add recipe "Coffee" priced 50 using 3 coffee 1 milk 1 sugar 0 chocolate
    And I add recipe "Coffee" priced 99 using 9 coffee 9 milk 9 sugar 9 chocolate
    Then the operation status is RECIPE_NOT_ADDED
    And the machine mode is WAITING
    And the recipe book contains 1 recipes
    And recipe at index 0 is "Coffee" priced 50 using 3 coffee 1 milk 1 sugar 0 chocolate

  @delete
  Scenario: Delete an existing recipe and preserve other recipes
    Given the standard three recipes are available
    When I delete recipe at index 1
    Then the operation status is OK
    And the machine mode is WAITING
    And recipe at index 1 is empty
    And the recipe book contains 2 recipes
    And recipe at index 0 is "Coffee" priced 50 using 3 coffee 1 milk 1 sugar 0 chocolate
    And recipe at index 2 is "Mocha" priced 90 using 2 coffee 2 milk 1 sugar 3 chocolate

  @delete
  Scenario: Deleting a recipe frees capacity for a new recipe
    Given the standard three recipes are available
    When I delete recipe at index 1
    Then the operation status is OK
    When I add recipe "Replacement" priced 40 using 1 coffee 2 milk 3 sugar 4 chocolate
    Then the operation status is OK
    And the machine mode is WAITING
    And the recipe book contains 3 recipes

  @delete
  Scenario: Deleting an empty slot reports an error
    When I delete recipe at index 0
    Then the operation status is OUT_OF_RANGE
    And the machine mode is WAITING
    And the recipe book contains 0 recipes

  @delete
  Scenario Outline: Invalid delete selection leaves recipes intact
    Given the standard three recipes are available
    When I delete recipe at index <index>
    Then the operation status is OUT_OF_RANGE
    And the machine mode is WAITING
    And the recipe book contains 3 recipes

    Examples:
      | index |
      | -1    |
      | 3     |
      | 99    |

  @edit
  Scenario: Edit updates values but keeps the original name
    Given the standard three recipes are available
    When I select recipe at index 1 for editing
    Then the machine mode is EDIT_RECIPE
    And the operation status is OK
    When I submit edited recipe named "ChangedName" priced 85 using 1 coffee 2 milk 3 sugar 4 chocolate
    Then the operation status is OK
    And the machine mode is WAITING
    And the recipe book contains 3 recipes
    And recipe at index 1 is "Latte" priced 85 using 1 coffee 2 milk 3 sugar 4 chocolate
    And the inventory report shows 15 coffee 15 milk 15 sugar 15 chocolate

  @edit
  Scenario: Edited price and ingredients govern subsequent purchase
    Given the standard three recipes are available
    When I select recipe at index 1 for editing
    And I submit edited recipe named "Ignored" priced 85 using 1 coffee 2 milk 3 sugar 4 chocolate
    And I insert 100 money units
    And I purchase recipe at index 1
    Then the operation status is OK
    And the machine mode is WAITING
    And the inserted money is 0
    And the return tray contains 15 money units
    And the inventory report shows 14 coffee 13 milk 12 sugar 11 chocolate

  @edit
  Scenario: An empty recipe cannot be selected for editing
    When I select recipe at index 0 for editing
    Then the operation status is OUT_OF_RANGE
    And the machine mode is WAITING
    And the recipe book contains 0 recipes

  @edit
  Scenario Outline: Invalid edit selection is rejected
    Given the standard three recipes are available
    When I select recipe at index <index> for editing
    Then the operation status is OUT_OF_RANGE
    And the machine mode is WAITING
    And the recipe book contains 3 recipes

    Examples:
      | index |
      | -1    |
      | 3     |
      | 99    |

  @inventory
  Scenario: Add different amounts to each ingredient
    When I add inventory 2 coffee 3 milk 4 sugar 5 chocolate
    Then the operation status is OK
    And the machine mode is WAITING
    And the inventory report shows 17 coffee 18 milk 19 sugar 20 chocolate

  @inventory
  Scenario: Inventory additions accumulate
    When I add inventory 2 coffee 3 milk 4 sugar 5 chocolate
    Then the operation status is OK
    When I add inventory 1 coffee 2 milk 3 sugar 4 chocolate
    Then the operation status is OK
    And the machine mode is WAITING
    And the inventory report shows 18 coffee 20 milk 22 sugar 24 chocolate

  @inventory
  Scenario: Adding zero changes no stock
    When I add inventory 0 coffee 0 milk 0 sugar 0 chocolate
    Then the operation status is OK
    And the machine mode is WAITING
    And the inventory report shows 15 coffee 15 milk 15 sugar 15 chocolate

  @inventory
  Scenario Outline: Each negative inventory amount is rejected
    When I add inventory <coffee> coffee <milk> milk <sugar> sugar <chocolate> chocolate
    Then the operation status is OUT_OF_RANGE
    And the machine mode is WAITING
    And the inventory report shows 15 coffee 15 milk 15 sugar 15 chocolate

    Examples:
      | coffee | milk | sugar | chocolate |
      | -1     | 0    | 0     | 0         |
      | 0      | -1   | 0     | 0         |
      | 0      | 0    | -1    | 0         |
      | 0      | 0    | 0     | -1        |

  @check
  Scenario: Check inventory twice without changing it
    Then the inventory report shows 15 coffee 15 milk 15 sugar 15 chocolate
    And the inventory report shows 15 coffee 15 milk 15 sugar 15 chocolate
    And the machine mode is WAITING

  @purchase
  Scenario: Exact payment
    Given the standard three recipes are available
    When I insert 50 money units
    And I purchase recipe at index 0
    Then the operation status is OK
    And the machine mode is WAITING
    And the inserted money is 0
    And the return tray contains 0 money units
    And the inventory report shows 12 coffee 14 milk 14 sugar 15 chocolate

  @purchase
  Scenario: Overpayment
    Given the standard three recipes are available
    When I insert 75 money units
    And I purchase recipe at index 0
    Then the operation status is OK
    And the machine mode is WAITING
    And the inserted money is 0
    And the return tray contains 25 money units
    And the inventory report shows 12 coffee 14 milk 14 sugar 15 chocolate

  @purchase
  Scenario: Middle recipe purchase
    Given the standard three recipes are available
    When I insert 100 money units
    And I purchase recipe at index 1
    Then the operation status is OK
    And the machine mode is WAITING
    And the inserted money is 0
    And the return tray contains 30 money units
    And the inventory report shows 13 coffee 12 milk 14 sugar 15 chocolate

  @purchase
  Scenario: Last recipe purchase
    Given the standard three recipes are available
    When I insert 100 money units
    And I purchase recipe at index 2
    Then the operation status is OK
    And the machine mode is WAITING
    And the inserted money is 0
    And the return tray contains 10 money units
    And the inventory report shows 13 coffee 13 milk 14 sugar 12 chocolate

  @purchase
  Scenario: Several inserted payments accumulate
    Given the standard three recipes are available
    When I insert 20 money units
    And I insert 55 money units
    Then the inserted money is 75
    When I purchase recipe at index 0
    Then the operation status is OK
    And the inserted money is 0
    And the return tray contains 25 money units
    And the machine mode is WAITING

  @purchase
  Scenario: Underpayment is returned without consuming stock
    Given the standard three recipes are available
    When I insert 49 money units
    And I purchase recipe at index 0
    Then the machine mode is WAITING
    And all 49 money units remain available to the customer
    And the inventory report shows 15 coffee 15 milk 15 sugar 15 chocolate

  @purchase
  Scenario: Insufficient coffee returns the full payment
    When I add recipe "Large" priced 50 using 16 coffee 1 milk 1 sugar 1 chocolate
    Then the operation status is OK
    When I insert 75 money units
    And I purchase recipe at index 0
    Then the machine mode is WAITING
    And all 75 money units remain available to the customer
    And the inventory report shows 15 coffee 15 milk 15 sugar 15 chocolate

  @purchase
  Scenario: Insufficient milk returns the full payment
    When I add recipe "Large" priced 50 using 1 coffee 16 milk 1 sugar 1 chocolate
    Then the operation status is OK
    When I insert 75 money units
    And I purchase recipe at index 0
    Then the machine mode is WAITING
    And all 75 money units remain available to the customer
    And the inventory report shows 15 coffee 15 milk 15 sugar 15 chocolate

  @purchase
  Scenario: Insufficient sugar returns the full payment
    When I add recipe "Large" priced 50 using 1 coffee 1 milk 16 sugar 1 chocolate
    Then the operation status is OK
    When I insert 75 money units
    And I purchase recipe at index 0
    Then the machine mode is WAITING
    And all 75 money units remain available to the customer
    And the inventory report shows 15 coffee 15 milk 15 sugar 15 chocolate

  @purchase
  Scenario: Insufficient chocolate returns the full payment
    When I add recipe "Large" priced 50 using 1 coffee 1 milk 1 sugar 16 chocolate
    Then the operation status is OK
    When I insert 75 money units
    And I purchase recipe at index 0
    Then the machine mode is WAITING
    And all 75 money units remain available to the customer
    And the inventory report shows 15 coffee 15 milk 15 sugar 15 chocolate

  @purchase
  Scenario: Exactly available ingredients can be consumed
    When I add recipe "All" priced 50 using 15 coffee 15 milk 15 sugar 15 chocolate
    And I insert 50 money units
    And I purchase recipe at index 0
    Then the operation status is OK
    And the machine mode is WAITING
    And the inserted money is 0
    And the return tray contains 0 money units
    And the inventory report shows 0 coffee 0 milk 0 sugar 0 chocolate

  @purchase
  Scenario: A recipe using only chocolate leaves other ingredients unchanged
    When I add recipe "Chocolate" priced 65 using 0 coffee 0 milk 0 sugar 4 chocolate
    And I insert 100 money units
    And I purchase recipe at index 0
    Then the operation status is OK
    And the return tray contains 35 money units
    And the inserted money is 0
    And the machine mode is WAITING
    And the inventory report shows 15 coffee 15 milk 15 sugar 11 chocolate

  @purchase
  Scenario: Money returned from several purchases accumulates until collected
    Given the standard three recipes are available
    When I insert 75 money units
    And I purchase recipe at index 0
    And I insert 80 money units
    And I purchase recipe at index 1
    Then the operation status is OK
    And the inserted money is 0
    And the return tray contains 35 money units
    When I collect the returned money
    Then the operation status is OK
    And the return tray contains 0 money units
    And the machine mode is WAITING
    And the inventory report shows 10 coffee 11 milk 13 sugar 15 chocolate

  @purchase
  Scenario: Selecting an empty recipe returns the payment
    When I insert 75 money units
    And I purchase recipe at index 0
    Then the machine mode is WAITING
    And all 75 money units remain available to the customer
    And the inventory report shows 15 coffee 15 milk 15 sugar 15 chocolate

  @purchase
  Scenario Outline: An invalid purchase selection returns the payment
    Given the standard three recipes are available
    When a purchase request selects invalid index <index> with payment 75
    Then the invalid selection is rejected without charging the 75 money units
    And the inventory report shows 15 coffee 15 milk 15 sugar 15 chocolate

    Examples:
      | index |
      | -1    |
      | 3     |
      | 99    |

  @waiting
  Scenario Outline: Nonpositive money insertion is rejected
    When I insert <amount> money units
    Then the operation status is OUT_OF_RANGE
    And the machine mode is WAITING
    And the inserted money is 0
    And the return tray contains 0 money units

    Examples:
      | amount |
      | 0      |
      | -1     |

  @waiting
  Scenario Outline: Reset aborts supported service modes
    When I select service <button>
    And I reset the current operation
    Then the machine mode is WAITING
    And the recipe book contains 0 recipes

    Examples:
      | button |
      | 1      |
      | 3      |
      | 4      |
      | 5      |
      | 6      |

  @purchase @service_boundary
  Scenario: A purchase request with no available recipe slots is rejected safely
    When a purchase request selects invalid index 3 with payment 75
    Then the invalid selection is rejected without charging the 75 money units
    And the inventory report shows 15 coffee 15 milk 15 sugar 15 chocolate

  @add
  Scenario: Resubmitting an existing recipe object does not duplicate it
    Given the standard three recipes are available
    When I resubmit the existing recipe at index 0
    Then the operation status is RECIPE_NOT_ADDED
    And the machine mode is WAITING
    And the recipe book contains 3 recipes
    And recipe at index 0 is "Coffee" priced 50 using 3 coffee 1 milk 1 sugar 0 chocolate

  @recipe_validation
  Scenario Outline: Recipe form rejects negative and noninteger values without corrupting valid fields
    Given a recipe form containing valid values
    When I enter value "<value>" for recipe field <field>
    Then the invalid recipe value is rejected and the valid form is unchanged
    And the machine mode is WAITING
    And the recipe book contains 0 recipes

    Examples:
      | field     | value      |
      | price     | -1         |
      | coffee    | -1         |
      | milk      | -1         |
      | sugar     | -1         |
      | chocolate | -1         |
      | price     | abc        |
      | coffee    | abc        |
      | milk      | abc        |
      | sugar     | abc        |
      | chocolate | abc        |
      | price     | 1.5        |
      | coffee    | 1.5        |
      | milk      | 1.5        |
      | sugar     | 1.5        |
      | chocolate | 1.5        |
      | price     | 2147483648 |
      | coffee    | 2147483648 |
      | milk      | 2147483648 |
      | sugar     | 2147483648 |
      | chocolate | 2147483648 |

  @recipe_validation
  Scenario: A missing recipe name does not erase the current form name
    Given a recipe form containing valid values
    When the recipe form receives a missing name
    Then the existing recipe form name is preserved
    When I submit the valid recipe form
    Then the operation status is OK
    And the machine mode is WAITING
    And recipe at index 0 is "Form" priced 50 using 1 coffee 2 milk 3 sugar 4 chocolate

  @purchase
  Scenario: An unsuccessful purchase preserves all paid money and inventory
    When I add recipe "TooLarge" priced 50 using 16 coffee 1 milk 1 sugar 1 chocolate
    And I insert 75 money units
    And I purchase recipe at index 0
    Then all 75 money units remain available to the customer
    And the inventory report shows 15 coffee 15 milk 15 sugar 15 chocolate

  @inventory
  Scenario: Replenishment makes a formerly impossible drink available
    When I add recipe "LargeCoffee" priced 50 using 16 coffee 1 milk 1 sugar 1 chocolate
    And I add inventory 1 coffee 0 milk 0 sugar 0 chocolate
    Then the operation status is OK
    When I insert 75 money units
    And I purchase recipe at index 0
    Then the operation status is OK
    And the inserted money is 0
    And the return tray contains 25 money units
    And the machine mode is WAITING
    And the inventory report shows 0 coffee 14 milk 14 sugar 14 chocolate

  @purchase
  Scenario: An unpaid purchase does not consume stock
    Given the standard three recipes are available
    When I purchase recipe at index 0
    Then the machine mode is WAITING
    And the inserted money is 0
    And the return tray contains 0 money units
    And the inventory report shows 15 coffee 15 milk 15 sugar 15 chocolate

  @purchase
  Scenario: Three purchases exhaust only milk and a fourth is not dispensed
    When I add recipe "Single" priced 10 using 0 coffee 5 milk 0 sugar 0 chocolate
    And I insert 10 money units
    And I purchase recipe at index 0
    Then the operation status is OK
    And the machine mode is WAITING
    And the inserted money is 0
    And I insert 10 money units
    And I purchase recipe at index 0
    Then the operation status is OK
    And the machine mode is WAITING
    And the inserted money is 0
    And I insert 10 money units
    And I purchase recipe at index 0
    Then the operation status is OK
    And the machine mode is WAITING
    And the inserted money is 0
    And the inventory report shows 15 coffee 0 milk 15 sugar 15 chocolate
    When I insert 10 money units
    And I purchase recipe at index 0
    Then the machine mode is WAITING
    And all 10 money units remain available to the customer
    And the inventory report shows 15 coffee 0 milk 15 sugar 15 chocolate

  @purchase
  Scenario: Three purchases exhaust only sugar and a fourth is not dispensed
    When I add recipe "Single" priced 10 using 0 coffee 0 milk 5 sugar 0 chocolate
    And I insert 10 money units
    And I purchase recipe at index 0
    Then the operation status is OK
    And the machine mode is WAITING
    And the inserted money is 0
    And I insert 10 money units
    And I purchase recipe at index 0
    Then the operation status is OK
    And the machine mode is WAITING
    And the inserted money is 0
    And I insert 10 money units
    And I purchase recipe at index 0
    Then the operation status is OK
    And the machine mode is WAITING
    And the inserted money is 0
    And the inventory report shows 15 coffee 15 milk 0 sugar 15 chocolate
    When I insert 10 money units
    And I purchase recipe at index 0
    Then the machine mode is WAITING
    And all 10 money units remain available to the customer
    And the inventory report shows 15 coffee 15 milk 0 sugar 15 chocolate

  @purchase
  Scenario: Three purchases exhaust only chocolate and a fourth is not dispensed
    When I add recipe "Single" priced 10 using 0 coffee 0 milk 0 sugar 5 chocolate
    And I insert 10 money units
    And I purchase recipe at index 0
    Then the operation status is OK
    And the machine mode is WAITING
    And the inserted money is 0
    And I insert 10 money units
    And I purchase recipe at index 0
    Then the operation status is OK
    And the machine mode is WAITING
    And the inserted money is 0
    And I insert 10 money units
    And I purchase recipe at index 0
    Then the operation status is OK
    And the machine mode is WAITING
    And the inserted money is 0
    And the inventory report shows 15 coffee 15 milk 15 sugar 0 chocolate
    When I insert 10 money units
    And I purchase recipe at index 0
    Then the machine mode is WAITING
    And all 10 money units remain available to the customer
    And the inventory report shows 15 coffee 15 milk 15 sugar 0 chocolate

  @purchase
  Scenario: Three purchases exhaust only coffee and a fourth is not dispensed
    When I add recipe "Single" priced 10 using 5 coffee 0 milk 0 sugar 0 chocolate
    And I insert 10 money units
    And I purchase recipe at index 0
    Then the operation status is OK
    And the machine mode is WAITING
    And the inserted money is 0
    And I insert 10 money units
    And I purchase recipe at index 0
    Then the operation status is OK
    And the machine mode is WAITING
    And the inserted money is 0
    And I insert 10 money units
    And I purchase recipe at index 0
    Then the operation status is OK
    And the machine mode is WAITING
    And the inserted money is 0
    And the inventory report shows 0 coffee 15 milk 15 sugar 15 chocolate
    When I insert 10 money units
    And I purchase recipe at index 0
    Then the machine mode is WAITING
    And all 10 money units remain available to the customer
    And the inventory report shows 0 coffee 15 milk 15 sugar 15 chocolate
