# SharingApp — Item Lifecycle: UML State Diagram

Project title: **SharingApp — Item Lifecycle: UML State Diagram**

Upload [SharingApp_Item_State_Diagram.pdf](SharingApp_Item_State_Diagram.pdf) to Coursera. Click the PDF and use **Download raw file** to download it. [Preview](SharingApp_Item_State_Diagram.png).

Page 1 shows the four required states: Available without photo, Available with photo, Borrowed without photo and Borrowed with photo. It includes the initial pseudostate, guarded creation choice, eight arrows for independent photo/status changes, and deletion paths from every state to the terminal state. Page 2 supplies exact transition mappings, combined changes and same-state saves.

The model was checked against AddItemActivity.java, EditItemActivity.java and Item.java in the newly supplied SharingApp-c1-items-only-v4 (2).zip. These files match the previously examined archive byte for byte. Initial creation is always Available; a selected image determines which Available state is reached. Borrowed requires a borrower name. Edit save replaces an Item while retaining its identifier, so that implementation step is not terminal deletion. The modeled boundary is the logical item after valid saving, with transient editor behavior and storage limitations explicitly noted.

The PDF was visually checked and contains no personal author name or submission date. The Android app was not run in an emulator in this environment. An editable Python/ReportLab/PyMuPDF generator is in source/create_diagram.py.
