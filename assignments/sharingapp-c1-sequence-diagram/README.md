# SharingApp — Add a New Item: UML Sequence Diagram

Project title: **SharingApp — Adding a New Item: UML Sequence Diagram**

Upload [SharingApp_Add_Item_Sequence_Diagram.pdf](SharingApp_Add_Item_Sequence_Diagram.pdf) to Coursera. Open the file and click **Download raw file**. [PNG preview](SharingApp_Add_Item_Sequence_Diagram.png).

This single-page vector diagram contains AddItemActivity, ItemList, Dimensions and Item. Android framework dispatch and the click listener provide external context. AddItemActivity execution begins with onCreate(savedInstanceState), which calls loadItems(context); a later click invokes saveItem(view). On the valid-input path the activity creates Dimensions and Item, calls addItem(item), then saveItems(context). The Item constructor calls addImage(image) and setId() because the supplied identifier is null. Creation messages terminate at newly created object heads, and activation bars and returns are shown. Invalid input is described beneath the guarded successful branch.

Evidence: the four source files were inspected and matched byte-for-byte against the newly supplied SharingApp-c1-items-only-v4 (1).zip archive. The activity initializes its ItemList field before onCreate, rather than constructing the wrapper in onCreate. Persistence is summarized inside ItemList; saveItems catches I/O failures internally, so its return is not represented as guaranteed durable success. The app was not run in an Android emulator in this environment.

No author name or submission date is printed in the PDF. The editable diagram generator is source/create_diagram.py (Python, ReportLab and PyMuPDF).
