# SharingApp — Contacts and Borrower Selection

**Project title:** SharingApp — Contacts and Borrower Selection

## Submission

- **Part 1:** download [Contact_Submission.zip](Contact_Submission.zip), containing a folder with exactly Contact.java and ContactList.java, and upload that ZIP to Coursera.
- **Part 2:** download [SharingApp_Contacts_Demo.mp4](SharingApp_Contacts_Demo.mp4) (2 minutes 28 seconds, normal playback speed, real Android 10 emulator capture), upload it to **YouTube (Unlisted)** or **Internet Archive**, and paste the resulting video URL into Coursera. A GitHub download URL is not one of the requested video-hosting options. Video publication requires the learner's hosting account.
- **Video title:** SharingApp Contacts Feature Demo
- **Caption:** Demonstration of contact creation, email editing, contact deletion, and borrower selection in the Android app.

Click a file and use **Download raw file** to download it. No personal author name or submission date is included in these deliverables.

## Additional files

- [SharingApp_Contacts.apk](SharingApp_Contacts.apk): compiled debug Android application.
- [SharingApp_Contacts_Project.zip](SharingApp_Contacts_Project.zip): complete Android Studio project; extract and open the SharingApp folder. Requires JDK 17 or 21 and Android SDK Platform 35; tested device environment is Android 10/API 29. Gradle 8.14.3 / Android Gradle plugin 8.7.3 retain the original Android support-library application.
- [Submission source files](submission): the two implemented model classes.
- [Verification](verification): filesystem persistence checks and on-device walkthrough source/evidence.
- [Russian upload instructions](DEMO_UPLOAD_RU.txt).

## Implementation

Contact implements the username, email and stable UUID identifier with all getters/setters and the constructor's existing-id reuse behavior. ContactList implements the list methods, username availability and lookup, username ordering for the borrower spinner, identity-based matching, and JSON persistence to app-private contacts.sav. Its collection is instance-scoped so a temporary active-borrowers list does not overwrite the contact directory.

The full project also fixes validation before contact mutation (a rejected duplicate username no longer removes the existing record), rejects blank renamed usernames, blocks editing/deleting active borrowers at the edit screen, checks empty borrower selection, postpones item status changes until Save, and increases both contact email input limits from 24 to 254 characters to avoid truncating ordinary email addresses. Contact creation, editing, deletion and borrower selection use the supplied starter screens. Source provenance is the supplied SharingApp_c1_starter_codebase.zip, with the two missing models implemented and the above integration corrections.

## Verification

The Android APK builds successfully with assembleDebug. The 20 model checks cover identity generation/reuse, list operations, duplicate-username queries, separately deserialized borrower matching, JSON save/reload, persistent email edits/deletion, UTF-8 names, missing files and invalid JSON. Their minimal filesystem Context double does not emulate the Android UI. The separate instrumentation walkthrough passed on the real Android 10 emulator: **OK (1 test), 139.316 seconds**. It verifies contact addition, email editing, deletion, item creation, the default borrower, selecting another borrower, saving, and reopening the item to verify the persisted borrower. Screenshots and the passing runner output are included. The video is a continuous normal-speed capture, trimmed only after the walkthrough to remove the return to the emulator launcher.

To rerun model checks, extract the full project, point GSON_JAR at app/src/include/gson-2.8.2-SNAPSHOT.jar and run verification/run_model_checks.sh with a JDK. The Android walkthrough expects fresh test application data and adds sample contacts and an item; its source is included in the full project under app/src/androidTest.
