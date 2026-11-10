# SharingApp — Code Smells and Long Method Refactoring

Project title: **SharingApp — Code Smells and Long Method Refactoring**

## Upload to Coursera

1. **Part 1:** [Part1_Code_Smell_Analysis.pdf](Part1_Code_Smell_Analysis.pdf). One page, two paragraphs, 311 words. It identifies Duplicated Code and Data Clumps with original class/method locations, reasons and proposed solutions. Long Method is excluded from this analysis. The proposed fixes are not applied.
2. **Part 2:** [Part2_ValidateInput_Submission.zip](Part2_ValidateInput_Submission.zip). One folder containing exactly AddItemActivity.java, EditItemActivity.java, AddContactActivity.java and EditContactActivity.java.

Open each file and click **Download raw file** to save it. Upload the PDF and the four-file ZIP into their separate fields. No video is requested.

## Refactoring

Each of the four save methods begins with `if (!validateInput()) { return; }`. Its original form reads and validation branches have been moved to `private boolean validateInput()`. Invalid input sets the original widget error and returns false; successful validation returns true. Values needed later by saving have private Activity scope. EditItemActivity also resets its borrower field during each validation, retaining the original local-variable behavior between saves.

Original check order, whitespace handling, error messages, uniqueness checks and all existing input policies are preserved. No extra field checks, trimming, shared validators, controller/model redesigns or other feature fixes are introduced. Only the four requested application Java files changed relative to the supplied solution archive.

| Activity | Original save body lines | Refactored save body lines |
| --- | ---: | ---: |
| AddItemActivity | 50 | 17 |
| EditItemActivity | 65 | 26 |
| AddContactActivity | 28 | 14 |
| EditContactActivity | 34 | 16 |

Line counts include the physical body lines, including internal blank lines, with leading/trailing blank lines excluded.

## Verification

**167 checks passed:** 158 original-versus-refactored single-save trace comparisons, five repeated-save scenarios and four validateInput signature checks. The original and submitted Activity methods execute with identical deterministic Android/widget/controller doubles. The comparison checks field reads, error targets/messages/order, controller arguments, IDs, photo/status/borrower handling, save-result branches, observer removal, navigation/finish and existing exception behavior. It also checks reused forms and the Borrowed-to-Available transition for stale borrower values.

These are JVM behavior-preservation checks, not an Android UI walkthrough or a claim that every possible Android runtime state was exercised. The complete Android application also builds successfully with assembleDebug.

- [Check results](verification/behavior-check-results.txt)
- [Runnable regression-check sources](verification/Behavior_Regression_Checks.zip) — extract and run `bash run.sh` with a JDK.
- [Android build log](verification/android-build.log)
- [Change-scope description](verification/SCOPE.txt)

## Optional files

- [Four individual Java files](submission)
- [Full refactored Android Studio project](SharingApp_Refactored_Project.zip)
- [Compiled debug APK](SharingApp_Refactored.apk)
- [Part 1 text](Part1_Text.txt)
- [Part 1 preview](Part1_Preview.png)

The optional full project uses JDK 17 or 21, Gradle 8.14.3, Android Gradle plugin 8.7.3 and compile SDK 35; target SDK remains 29. Local SDK paths, build outputs and IDE caches are excluded. The submitted four Java files retain the supplied starter's APIs. No personal author name or submission date is inserted in the documents or source.
