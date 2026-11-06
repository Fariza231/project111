from pathlib import Path
import fitz
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
OUT=Path(__file__).resolve().parents[1]
W,H=1600,1160
c=canvas.Canvas(str(OUT/'draft.pdf'),pagesize=(W,H))
def text(x,y,t,s=12,b=False):
 c.setFont('Helvetica-Bold' if b else 'Helvetica',s);c.drawString(x,y,t)
def label(x,y,t,width=1000,s=12):
 for i,line in enumerate(simpleSplit(t,'Helvetica',s,width)):text(x,y-i*15,line,s)
def line(x1,y1,x2,y2,dash=False):
 c.setDash(5,4) if dash else c.setDash();c.line(x1,y1,x2,y2);c.setDash()
def arrow(a,b,y,t='',reply=False,create=False,width=None):
 line(a,y,b,y,reply or create);sgn=1 if b>a else -1
 p=c.beginPath();p.moveTo(b-sgn*8,y+4);p.lineTo(b,y);p.lineTo(b-sgn*8,y-4)
 c.drawPath(p)
 if not reply and not create:
  p.close();c.drawPath(p,fill=1,stroke=1)
 if t:label(min(a,b)+10,y+9,t,width or abs(b-a)-20,11)
def act(x,top,bottom):
 c.setFillColorRGB(1,1,1);c.rect(x-7,bottom,14,top-bottom,fill=1,stroke=1);c.setFillColorRGB(0,0,0)
def head(x,y,t,w=190):
 c.setFillColorRGB(1,1,1);c.rect(x-w/2,y-24,w,48,fill=1,stroke=1);c.setFillColorRGB(0,0,0)
 text(x-w/2+10,y-4,t,13,True)
 line(x,y-24,x,198,True)
def selfcall(x,y,t):
 line(x+7,y,x+65,y);line(x+65,y,x+65,y-24);arrow(x+65,x+14,y-24)
 act(x+7,y-24,y-48);text(x+15,y+10,t,10)
text(35,1123,'SharingApp — Add a New Item | UML Sequence Diagram',22,True)
text(35,1097,'Source scenario: AddItemActivity.onCreate() followed by a valid saveItem(view); the new Item receives id = null.',12)
F,L,A,I,D,T=90,300,560,850,1120,1420
head(F,1040,': Android framework',170);head(L,1040,': Click listener',165);head(A,1040,': AddItemActivity',205);head(I,1040,'item_list : ItemList',210)
# Activity execution begins at the incoming lifecycle call, not at construction.
act(A,975,873);act(I,925,895)
arrow(F,A-7,975,'onCreate(savedInstanceState)',width=430)
text(A+20,949,'Initialize views and obtain application context',10)
arrow(A+7,I-7,925,'loadItems(context)')
arrow(I-7,A+7,895,'return',reply=True)
arrow(A-7,F,873,'return',reply=True)
# A later click is a separate execution of the same Activity instance.
act(L,838,224);act(A,810,242)
arrow(F,L-7,838,'onClick(view)',width=190)
arrow(L+7,A-7,810,'saveItem(view)')
text(A+20,786,'Read form values; check six required fields',10)
# The successful branch is explicit; failure is described below.
c.rect(370,247,1185,510);c.rect(370,734,45,23);text(377,741,'opt',11,True)
text(430,741,'[title, maker, description, length, width and height are nonempty]',11)
# Constructor messages arrive at object heads; lifelines start on creation.
head(D,696,'dimensions : Dimensions',225);act(D,672,638)
arrow(A+7,D-112.5,696,'<<create>> Dimensions(length_str, width_str, height_str)',create=True,width=420)
arrow(D-7,A+7,638,'constructed dimensions',reply=True)
head(T,577,'item : Item',190);act(T,553,386)
arrow(A+7,T-95,577,'<<create>> Item(title_str, maker_str, description_str, dimensions, image, null)',create=True,width=720)
selfcall(T,530,'addImage(image)')
text(1130,495,'Encodes photo only if image != null',10)
selfcall(T,455,'setId() [id == null]')
text(1130,420,'Creates a new UUID identifier',10)
arrow(T-7,A+7,386,'constructed item (Available; borrower = empty string)',reply=True)
act(I,350,330);arrow(A+7,I-7,350,'addItem(item)');arrow(I-7,A+7,330,'return',reply=True)
act(I,302,275);arrow(A+7,I-7,302,'saveItems(context)');arrow(I-7,A+7,275,'return',reply=True)
text(890,304,'Serialize list to items.sav using Gson',10)
text(590,258,'Create Intent and start MainActivity (navigation detail; not a modeled lifeline)',10)
arrow(A-7,L+7,242,'return',reply=True);arrow(L-7,F,224,'return',reply=True)
# Notes are outside the interaction fragment and do not invent validation calls.
notes=[
 'Lifelines proceed downward. Narrow rectangles show execution; solid filled-arrow calls are synchronous; dashed arrows are returns or <<create>> messages.',
 'The ItemList wrapper is initialized by the activity field initializer before onCreate(); it is therefore already present at the start. Its constructor is not called from onCreate().',
 'Validation failure: saveItem() calls setError("Empty field!") on the first empty required EditText and returns. The opt fragment is skipped: no Dimensions/Item is created and no list is saved.',
 'Item construction assigns title/maker/description/dimensions, status = "Available", borrower = "", calls addImage(image), then setId() because the supplied id is null.',
 'UI widgets, Gson, file streams, Intent and UUID are supporting implementation details summarized in notes. loadItems()/saveItems() catch their file I/O exceptions internally.',
 'Framework dispatch and the click listener are external context. Only the four requested application classes are expanded. No author name or submission date is included.'
]
y=166
for n in notes:label(35,y,n,1525,11);y-=25
c.showPage();c.save()
d=fitz.open(OUT/'draft.pdf');d.set_metadata({'title':'SharingApp — Add a New Item: UML Sequence Diagram','author':'','creator':'','producer':'','creationDate':'','modDate':''});d.save(OUT/'SharingApp_Add_Item_Sequence_Diagram.pdf');d.close();(OUT/'draft.pdf').unlink()
d=fitz.open(OUT/'SharingApp_Add_Item_Sequence_Diagram.pdf');d[0].get_pixmap(matrix=fitz.Matrix(.9,.9)).save(OUT/'SharingApp_Add_Item_Sequence_Diagram.png')
