from pathlib import Path
import fitz,zipfile
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
OUT=Path(__file__).resolve().parents[1];W,H=1520,1200
c=canvas.Canvas(str(OUT/'draft.pdf'),pagesize=(W,H))
def text(x,y,s,size=12,b=False):
 c.setFont('Helvetica-Bold' if b else 'Helvetica',size);c.setFillColorRGB(0,0,0);c.drawString(x,y,s)
def wrap(x,y,s,w,size=12):
 for i,t in enumerate(simpleSplit(s,'Helvetica',size,w)):text(x,y-16*i,t,size)
def arrow(points):
 p=c.beginPath();p.moveTo(*points[0])
 for q in points[1:]:p.lineTo(*q)
 c.drawPath(p)
 (x0,y0),(x,y)=points[-2:];import math
 a=math.atan2(y-y0,x-x0);r=9
 p=c.beginPath();p.moveTo(x,y);p.lineTo(x-r*math.cos(a-.4),y-r*math.sin(a-.4));p.lineTo(x-r*math.cos(a+.4),y-r*math.sin(a+.4));p.close();c.drawPath(p,stroke=1,fill=1)
def state(x,y,name,condition):
 c.roundRect(x-210,y-48,420,96,12,stroke=1,fill=0);text(x-190,y+15,name,19,True);text(x-190,y-15,condition,12)
text(35,1160,'SharingApp — Item Lifecycle | UML State Diagram',23,True)
text(35,1130,'Four states combine availability and the presence of an attached photo. The state machine tracks the logical item, identified by its id.',12)
# initial and a guarded creation choice
c.circle(180,1050,9,fill=1,stroke=1);arrow([(189,1050),(747,1050)])
text(250,1065,'AddItemActivity.saveItem(view) [all required fields valid]',12)
p=c.beginPath();p.moveTo(760,1063);p.lineTo(773,1050);p.lineTo(760,1037);p.lineTo(747,1050);p.close();c.drawPath(p)
arrow([(760,1037),(760,990),(410,990),(410,908)])
arrow([(773,1050),(1110,1050),(1110,908)])
text(450,1005,'[image == null]',12);text(880,1065,'[image != null]',12)
text(495,964,'/ new Item(..., image, null); status = "Available"',11)
state(410,860,'Available without photo','status = "Available"; no attached image')
state(1110,860,'Available with photo','status = "Available"; attached image present')
state(410,490,'Borrowed without photo','status = "Borrowed"; no attached image')
state(1110,490,'Borrowed with photo','status = "Borrowed"; attached image present')
# Photo changes preserve status.
for y,a,b in [(860,'T1','T2'),(490,'T3','T4')]:
 arrow([(620,y+20),(900,y+20)]);text(635,y+35,a+': attach photo + save',11)
 arrow([(900,y-20),(620,y-20)]);text(635,y-41,b+': deletePhoto(view) + save',11)
# status changes preserve photo and require a nonempty borrower for Borrowed.
for x,a,b in [(410,'T5','T6'),(1110,'T7','T8')]:
 arrow([(x-75,812),(x-75,538)])
 wrap(x-290,718,a+': saveItem(view)\n[status switch unchecked && borrower nonempty]\n/ setStatus("Borrowed"); setBorrower(borrower)',195,11)
 arrow([(x+75,538),(x+75,812)])
 wrap(x+90,718,b+': saveItem(view) [status switch checked] / status = "Available"; borrower = ""',200,11)
# Explicit deletion ends the logical item lifecycle. Branches merge at the terminal.
arrow([(200,860),(65,860),(65,270),(746,270)])
arrow([(1320,860),(1455,860),(1455,270),(774,270)])
text(75,797,'deleteItem(view)',11);text(1325,797,'deleteItem(view)',11)
arrow([(410,442),(410,335),(760,335),(760,284)])
arrow([(1110,442),(1110,335),(760,335),(760,284)])
text(430,351,'deleteItem(view)',11);text(930,351,'deleteItem(view)',11)
c.circle(760,270,14,stroke=1,fill=0);c.circle(760,270,8,stroke=1,fill=1);text(790,258,'Deleted — terminal state',13,True)
# Notes explain exact UI events and avoid mistaking implementation replacement for deletion.
y=219
for s in [
 'T1: Available without -> Available with; T2: reverse. T3: Borrowed without -> Borrowed with; T4: reverse.',
 'T5: Available without -> Borrowed without; T6: reverse. T7: Available with -> Borrowed with; T8: reverse.',
 'Attach photo means addPhoto(view), then successful onActivityResult(... RESULT_OK ...) with a non-null Bitmap, followed by saveItem(view).',
 'All saving transitions require nonempty title, maker, description, length, width and height. Borrowed also requires a nonempty borrower. Failed validation does not commit a replacement item.',
 'Edit save rebuilds the Item with the same id, replaces it in ItemList and calls saveItems(context). This replacement is not terminal deletion. Explicit delete removes the logical item.',
 'If both the status and photo change in one edit, the target is determined by both final values; all four combined transitions are listed on page 2. Saving unchanged values is a self-transition.',
 'The diagram models logical saved edits. toggleSwitch() can modify the current in-memory item before save; file-write exceptions are caught internally, so durable persistence is not guaranteed.'
]:wrap(35,y,s,1450,11);y-=27
c.showPage()
# Complete mapping for combined changes and same-state saves, without crossing diagonal arrows.
text(35,1155,'SharingApp — Transition Details and Source Mapping',23,True)
text(35,1118,'The state diagram and this transition dictionary form one model. "save" means a valid EditItemActivity.saveItem(view).',12)
rows=[
('T1','Available without photo','Available with photo','Photo attached; status remains Available'),
('T2','Available with photo','Available without photo','Photo deleted; status remains Available'),
('T3','Borrowed without photo','Borrowed with photo','Photo attached; status remains Borrowed'),
('T4','Borrowed with photo','Borrowed without photo','Photo deleted; status remains Borrowed'),
('T5','Available without photo','Borrowed without photo','Unchecked switch; nonempty borrower; no photo'),
('T6','Borrowed without photo','Available without photo','Checked switch; photo remains absent'),
('T7','Available with photo','Borrowed with photo','Unchecked switch; nonempty borrower; photo retained'),
('T8','Borrowed with photo','Available with photo','Checked switch; photo retained'),
('T9','Available without photo','Borrowed with photo','Save with unchecked switch, borrower and attached photo'),
('T10','Borrowed with photo','Available without photo','Save with checked switch and deleted photo'),
('T11','Available with photo','Borrowed without photo','Save with unchecked switch, borrower and deleted photo'),
('T12','Borrowed without photo','Available with photo','Save with checked switch and attached photo')]
for x,s in [(35,'ID'),(95,'FROM'),(420,'TO'),(760,'EVENT / GUARD')]:text(x,1070,s,13,True)
y=1038
for ident,fr,to,guard in rows:
 for x,s in [(35,ident),(95,fr),(420,to),(760,guard)]:text(x,y,s,12)
 c.line(35,y-12,1485,y-12);y-=38
wrap(35,530,'Self-transitions: each of the four states returns to itself when saveItem(view) succeeds without changing status or photo presence. Editing title, maker, description or dimensions, or replacing an existing photo, does not create an additional state.',1450,13)
wrap(35,463,'Final-state mapping: from every state, EditItemActivity.deleteItem(view) invokes item_list.deleteItem(item), then item_list.saveItems(context), and navigates to MainActivity. No outgoing transition from the final state is modeled.',1450,13)
wrap(35,395,'Creation mapping: AddItemActivity.saveItem(view) constructs Dimensions, then Item(..., image, null), adds it to ItemList and saves. Item initializes status to Available and borrower to the empty string. The creation choice therefore reaches one of the two Available states, depending on whether an image is attached.',1450,13)
wrap(35,311,'Editing mapping: onCreate loads the selected item and its image. deletePhoto sets the editor image to null. A successful camera result supplies the editor image. saveItem constructs a replacement with the original id; an unchecked switch sets Borrowed and the supplied borrower, while a checked switch keeps the constructor defaults Available and empty borrower.',1450,13)
wrap(35,211,'Scope: four stable logical states, initial pseudostate, guarded creation choice, all single-axis changes, combined saved edits, self-transitions and explicit final deletion. The transient editor UI and storage-error handling are summarized rather than represented as extra Item states.',1450,13)
text(35,83,'Source: supplied SharingApp-c1-items-only-v4 archive; AddItemActivity.java, EditItemActivity.java and Item.java.',11)
c.showPage();c.save()
d=fitz.open(OUT/'draft.pdf');d.set_metadata({'title':'SharingApp — Item Lifecycle: UML State Diagram','author':'','creator':'','producer':'','creationDate':'','modDate':''});d.save(OUT/'SharingApp_Item_State_Diagram.pdf');d.close();(OUT/'draft.pdf').unlink()
d=fitz.open(OUT/'SharingApp_Item_State_Diagram.pdf');d[0].get_pixmap(matrix=fitz.Matrix(.85,.85)).save(OUT/'SharingApp_Item_State_Diagram.png')
