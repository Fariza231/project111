# SharingApp — Command Pattern for Contact Management

Project title: **SharingApp — Command Pattern for Contact Management**

Upload [Contact_Command_Pattern_Submission.zip](Contact_Command_Pattern_Submission.zip) to Coursera. Open the ZIP link and click **Download raw file**. The ZIP contains one folder with exactly the five requested Java files:

- AddContactCommand.java
- DeleteContactCommand.java
- EditContactCommand.java
- AddContactActivity.java
- EditContactActivity.java

The supplied Option 1 starter is used. The commands extend its existing abstract Command and delegate to ContactList, following the existing item-command pattern. Constructors capture the receiver, contact arguments and Context without executing the operation. execute() performs the requested mutations, calls saveContacts(context), and marks normal completion. Both activities validate before executing a command and finish only after isExecuted(). Editing reuses the original contact identifier. No direct add/delete/save receiver operations remain in the submitted activities.

The supplied ContactList.saveContacts returns void and internally catches file I/O failures. The command flag therefore records normal completion of receiver calls, rather than a guaranteed disk-write result; the receiver API is retained unchanged for compatibility with the starter and the five-file submission. A receiver runtime exception propagates with isExecuted false. No undo, redo, idempotency or transactional rollback is introduced.

Verification: **25 checks passed**, using the real starter Command, Contact and ContactList with Gson and a small filesystem Context test double. Checks cover constructor side effects, delegation order, persistence/reload after add/edit/delete, retained identity, unaffected contacts and execution flags after injected receiver runtime exceptions. Both Android activities compile in a successful assembleDebug build. An Android UI walkthrough was not executed for this assignment; no video is required by its submission instructions.

Additional files:

- [Full Android Studio project](SharingApp_Command_Pattern_Project.zip)
- [Compiled debug APK](SharingApp_Command_Pattern.apk)
- [Five individual source files](submission)
- [Verification source and results](verification)

The optional full project uses Gradle 8.14.3, Android Gradle plugin 8.7.3, JDK 17 or 21, and compile SDK 35 to support current build tooling. The submitted five source files retain the original AndroidX starter APIs and can be copied into the supplied starter project. Local SDK paths, build outputs and IDE caches are excluded from the project ZIP. No personal author name or submission date is included in the source or instructions.
