# CURRENT submission: CoffeeMaker — Unifying Use Cases and Tests using Cucumber

Download **[CoffeeMaker_Cucumber_FINAL.zip](CoffeeMaker_Cucumber_FINAL.zip)**. Upload this ZIP for the **Unifying Use Cases and Tests using Cucumber** assignment (the 5/10 screenshot), replacing earlier ZIPs. It contains exactly CoffeeMaker.feature and TestSteps.java at the top level.

## What changed

The grading output says correct-version verification failed; no failed-test trace was supplied. Earlier submissions included assumptions about invalid recipe indices, error statuses, refund location, reset behavior and form-level internals. This version removes those scenarios. It uses the public UI commands and queries only, finds recipes by name instead of assuming insertion indices, and checks inventory values without depending on trailing whitespace or newline formatting. Successful purchases still assert exact change and exact ingredient consumption.

The supplied UI retains an unsuccessful payment for retry, contradicting the earlier assertion that it must always move to the tray. That is a demonstrated incompatibility in the earlier suite. The exact hidden-grader cause cannot be confirmed without its failing test trace.

## Coverage of user stories

18 expanded scenarios cover all seven stories:
1. Waiting/menu: all six services.
2. Add recipe: stored fields, maximum three, duplicate-name rejection.
3. Delete recipe: removal and replacement capacity, other recipes preserved.
4. Edit recipe: name preserved, price and all ingredients updated.
5. Add inventory: independent additions and cumulative totals.
6. Check inventory: reported amounts and no depletion by reading.
7. Purchase beverage: exact payment, overpayment, recipe selection, change collection and stock use.

This is the use-case assignment, not the separate JaCoCo coverage exercise; intentionally broad invalid-input/form scenarios are not included merely to increase a coverage number.

## Validation

- 18/18 scenarios pass with correct domain classes and the original uploaded UI unchanged.
- 18/18 pass with the alternate local reference UI that moves failed-payment money into the tray.
- Both Gradle/Cucumber runs completed successfully, using Cucumber 1.2.5 and JUnit 4.12; source is Java 8 compatible.
- Each of five separately seeded documented defects was detected: maximum four instead of three recipes; deletion leaving an occupied slot; edit losing the original name; wrong sugar-addition condition; coffee increasing during purchase.
- There are no mocks, hardcoded passing results, swallowed assertion errors, production-code edits in the submission, or dependence on a functional stub.

The reference uses previously supplied Golden RecipeBook/Inventory plus correct public CoffeeMaker selection behavior; no official golden Cucumber archive was provided. Test success on local references and local mutants does not establish a 10/10 Coursera result. The hidden grader must re-run this ZIP. Raw local Cucumber results and mutation counts are in verification/.
