# SharingApp — Model-View-Controller and Observer Patterns

Project title: **SharingApp — MVC and Observer Pattern Refactoring**

Upload [SharingApp_MVC_Submission.zip](SharingApp_MVC_Submission.zip) to Coursera. Click the file and use **Download raw file**. The ZIP contains one folder with exactly the six requested Java files:

- Contact.java
- ContactList.java
- ContactController.java
- ContactListController.java
- AddContactActivity.java
- EditContactActivity.java

## Architecture

| Role | Implementation |
| --- | --- |
| Model | Contact and ContactList store domain state, publish observer notifications and persist the directory. |
| Controller | ContactController validates and updates a form's working model. ContactListController validates list operations, enforces unique usernames and active-borrower rules, invokes the supplied commands and handles save failure. |
| View | AddContactActivity and EditContactActivity read widgets, forward actions, render model notifications, and display controller validation errors. |
| Observer | Typed observer interfaces are nested in each model; subscriptions are deduplicated and detached with the Activity lifecycle. Observer lists are transient and excluded from JSON. |
| Command | The starter's existing Add/Edit/DeleteContactCommand classes remain unchanged and are invoked by ContactListController. |

The six files are self-contained with the supplied Option 2 starter APIs: they do not require an additional Model.java or View.java. Typed nested observer interfaces avoid a conflict with android.view.View. Editing uses a working copy with the original ID, so cancelling the form does not alter the committed record. The controller checks active-borrower eligibility before edit/delete. Save failure restores the prior in-memory list, and temporary-file persistence avoids truncating the committed JSON file.

## Verification

**53 executable MVC contract checks passed.** They cover model notifications, duplicate subscriptions, safe removal during callbacks, child-to-list propagation, observer removal, JSON reload and transient observer exclusion, required-field/username validation, unchanged IDs, working-copy isolation, add/edit/delete persistence, active-borrower protection, save-failure rollback and item model/controller behavior.

Two Android builds passed:

1. The complete project with both contact and item features refactored to MVC.
2. A separate copy of the supplied starter with only the six submitted Java files replaced/added; the remaining Java sources are unchanged. This verifies the six-file submission does not depend on the optional item refactoring.

The contract checks use production models/controllers/commands with Gson, Android API type signatures and a small filesystem Context test double. An Android UI walkthrough was not executed for this assignment; there is no video deliverable. The linked Google Docs tutorial could not be retrieved through this environment's network policy; this implementation follows the supplied starter and stated MVC/Observer requirements rather than claiming to reproduce the tutorial's exact class hierarchy.

## Optional complete project

- [SharingApp_MVC_Project.zip](SharingApp_MVC_Project.zip): full Android Studio project, including the corresponding item MVC controllers, observable item models, list views and contact list view.
- [SharingApp_MVC.apk](SharingApp_MVC.apk): compiled debug application.
- [Individual submission source](submission).
- [Verification source and results](verification).

The optional full project uses Gradle 8.14.3, Android Gradle plugin 8.7.3, compile SDK 35 and JDK 17 or 21. Local SDK paths, caches, build outputs and IDE configuration are excluded. The six-file compatibility build uses the same build tooling and keeps the remaining original application Java files unchanged. No personal author name or submission date is inserted in the source or instructions.
