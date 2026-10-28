# CoffeeMaker Cucumber coverage — revised submission

**Upload only [CoffeeMaker_Cucumber_Coverage_Submission.zip](CoffeeMaker_Cucumber_Coverage_Submission.zip) to Coursera.** It contains exactly `CoffeeMaker.feature` and `TestSteps.java` at the root, without folders or supplementary files. This replaces the earlier 57-scenario submission for the coverage exercise.

## Why the previous suite could reject a correct implementation

The grading report provided by the learner stated that correct-version verification failed and CoffeeMaker coverage was only 6/10 branches (60%). It did not identify the failed scenarios. Repository inspection found an unsupported UI expectation: the previous suite demanded that failed-payment money always move into the tray. The supplied UI instead retains it for a retry. The revised suite verifies conservation of the full customer amount for a failed purchase while retaining exact inserted/tray assertions after successful purchases. This resolves a demonstrated compatibility issue; without the grader's failing stack traces, it is not proof of the exact cause of every previous failure.

Malformed purchase indices are now exercised at the public CoffeeMaker service boundary. Full refund or the declared RecipeException is accepted; unchecked array-index crashes fail. These scenarios exercise both lower/upper bounds in the correct domain logic. Additional scenarios cover input validation, same-object duplicate rejection, replenishment, unpaid requests and repeated exhaustion of each ingredient. Ordinary integration actions continue through CoffeeMakerUI/UICmd. No mocks, private-field reflection, swallowed assertion failures or source changes are used to manufacture test coverage.

## Executed local results

- 87 Cucumber scenarios, including Scenario Outline examples: all passed on the local reference.
- Gradle `clean check jacocoTestReport`: BUILD SUCCESSFUL.
- Per-class branch thresholds: 75%, verified automatically for all five specified classes present in the supplied source.

| Class | Covered branches / total | Branch coverage |
|---|---:|---:|
| CoffeeMaker | 10/10 | 100.00% |
| CoffeeMakerUI | 42/50 | 84.00% |
| Inventory | 22/26 | 84.62% |
| Recipe | 20/26 | 76.92% |
| RecipeBook | 21/24 | 87.50% |

The exercise text calls the UI class CoffeeMakerMain; the supplied archive and the learner's grading report name it **CoffeeMakerUI**. The report above measures CoffeeMakerUI; it does not pretend that a nonexistent CoffeeMakerMain class was tested.

## Reference limitations

No official golden Cucumber project was supplied. The local validation reference uses the previously supplied Golden Inventory and RecipeBook, and CoffeeMaker's correct selection bounds behavior (invalid index returns full payment). **CoffeeMakerUI is byte-for-byte the original uploaded UI.** The constructor/API remains compatible with the Cucumber archive. All reference changes are recorded in `verification/local-reference.patch` and the isolated `local-reference-src` folder. These are local validation evidence, not edits to the user's original uploaded checkout, and they are not in the submission ZIP.

The same suite also passed a separate local reference that throws the declared RecipeException for invalid selections and places failed payments in the tray. Both supported error/refund conventions therefore passed. Official hidden-correct results remain unknown until Coursera regrades.

## Mutation checks

Ten individually seeded local faults were all detected. See `verification/mutations.txt` and `verification/mutations.json` for counts, changed expressions, and failing scenario names. These are **not the ten hidden Coursera mutants**; no claim of detecting seven hidden mutants or achieving a particular grade is made.

## Reproduce

Copy this folder to a writable directory with a full JDK 17/21 and Gradle 8.14.3. Arrange `TestSteps.java` and `RunCukesTest.java` under `src/test/java/edu/ncsu/csc326/coffeemaker/`, and `CoffeeMaker.feature` under `src/test/resources/edu/ncsu/csc326/coffeemaker/`. Copy the original assignment `src/main/java` into `src/main/java`. Add `settings.gradle` containing `rootProject.name = 'CoffeeMaker-Cucumber-Coverage'`.

Use the included modern build.gradle (JUnit 4.12, Cucumber 1.2.5 and JaCoCo 0.8.12). For local reference validation:

```sh
gradle clean check jacocoTestReport -PdomainSource=local-reference-src
```

Without `-PdomainSource`, original buggy production code is tested and failures are expected. Java 21 module compatibility arguments are local runner settings; submitted source is Java 8 compatible and uses Cucumber 1.2.5 APIs as in the assignment.

Reports: `build/reports/jacoco/test/html/index.html` and `build/reports/jacoco/test/jacocoTestReport.xml`. The recorded raw XML, Cucumber JSON and Gradle log are in `verification/`. The ZIP submitted for grading contains only the two required test files.
