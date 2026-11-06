# SharingApp — Items Only: UML Class Diagram

Project title: **SharingApp Items Only — UML Class Diagram**

Upload [SharingApp_UML_Class_Diagram.pdf](SharingApp_UML_Class_Diagram.pdf) to the assignment. It is a single vector PDF page that can be enlarged without losing text quality. Click the file and use **Download raw file** to save it.

[PNG preview](SharingApp_UML_Class_Diagram.png)

The model was derived from the supplied SharingApp-c1-items-only-v4 source archive. It contains the six requested classes, visibility, field types, parameter types, return types, explicitly declared constructors, and all explicitly declared application methods. The external AndroidX AppCompatActivity framework class is identified without expanding the Android framework implementation. AppCompatActivity comes from androidx.appcompat:appcompat:1.2.0 in app/build.gradle.

Relationships include inheritance, composition of activity-owned ItemList wrapper instances, shared aggregation of independently created Items, and the intended composition of an Item with its Dimensions value part. EditItemActivity also retains a non-owning reference to the selected Item. Multiplicities describe initialized application use; Java allows null references and Dimensions aliasing. The source does not enforce exclusive Dimensions ownership, which is explicitly noted on the diagram. ItemList.items is a static shared collection, not separate storage per activity.

The source inventory is: AddItemActivity 11 fields/5 methods; EditItemActivity 15 fields/7 methods; ItemList 2 fields/11 operations including its constructor; Item 9 fields/18 operations including its constructor; Dimensions 3 fields/6 operations including its constructor. Implicit Java constructors, local variables, inherited framework members and optional create dependencies are outside the displayed member inventory.

The diagram was checked against the Java declarations and visually inspected for layout. The Android app was not executed in an emulator in this environment. No author name or submission date is printed in the PDF.

The generator is in source/create_diagram.py and requires Python, ReportLab, PyMuPDF and the extracted source archive. Update its ROOT and SRC paths to regenerate elsewhere.
