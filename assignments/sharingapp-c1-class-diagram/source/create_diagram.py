from pathlib import Path
import re, math, fitz
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
ROOT=Path('/workspace/project111/assignments/sharingapp-c1-class-diagram')
SRC=Path('/workspace/sharing_c1/SharingApp/app/src/main/java/com/example/sharingapp')
W,H=1684,1191
c=canvas.Canvas(str(ROOT/'draft.pdf'),pagesize=(W,H))
c.setTitle('SharingApp Items Only — UML Class Diagram');c.setAuthor('')
def txt(x,y,t,size=11,bold=False):
 c.setFont('Helvetica-Bold' if bold else 'Helvetica',size);c.setFillColorRGB(0,0,0);c.drawString(x,y,t)
def lines(t,width,size=11):return simpleSplit(t,'Helvetica',size,width)
def box(name,x,top,w,attrs,methods,external=False):
 head=46 if external else 29
 a=[];m=[]
 for s in attrs:a+=lines(s,w-20)
 for s in methods:m+=lines(s,w-20)
 ah=max(25,len(a)*15+14);mh=max(25,len(m)*15+14);h=head+ah+mh
 c.setLineWidth(1);c.rect(x,top-h,w,h)
 txt(x+10,top-20,name,14,True)
 if external:txt(x+10,top-37,'<<external framework>>',10)
 c.line(x,top-head,x+w,top-head)
 y=top-head-19
 for s in a:txt(x+10,y,s);y-=15
 c.line(x,top-head-ah,x+w,top-head-ah)
 y=top-head-ah-19
 for s in m:txt(x+10,y,s);y-=15
 return (x,top-h,w,h)
def vis(v):return {'private':'-','public':'+','protected':'#'}[v]
def members(name):
 s=(SRC/(name+'.java')).read_text();attrs=[];methods=[]
 for v,static,transient,typ,n,init in re.findall(r'^    (private|protected|public)\s+(static\s+)?(transient\s+)?([\w<>]+)\s+(\w+)\s*(?:=\s*([^;]+))?;',s,re.M):
  st=vis(v)+' '+n+' : '+typ
  if init and not init.strip().startswith('new '):st+=' = '+init.strip()
  if static:st+=' {static}'
  if transient:st+=' {transient}'
  attrs.append(st)
 for v,rest,params in re.findall(r'^    (public|protected|private)\s+([\w<>]+(?:\s+\w+)?)\s*\(([^)]*)\)\s*\{',s,re.M):
  parts=rest.split();n=parts[-1];ret=parts[0] if len(parts)>1 else None
  ps=[]
  for p in params.split(','):
   p=p.strip()
   if p:
    pt,pn=p.rsplit(' ',1);ps.append(pn+' : '+pt)
  st=vis(v)+' '+n+'('+', '.join(ps)+')'
  if ret:st+=' : '+ret
  else:st+=' {constructor}'
  methods.append(st)
 return attrs,methods
coords={'AddItemActivity':(35,1045,490),'EditItemActivity':(1159,1045,490),'ItemList':(617,1010,450),'Item':(617,675,490),'Dimensions':(70,410,470)}
txt(35,H-30,'SharingApp — Items Only | UML Class Diagram',21,True)
# A library superclass is not an application-defined class. Do not invent its implementation members.
framework=box('AppCompatActivity',650,1175,385,[],[],True)
B={}
for n,(x,t,w) in coords.items():B[n]=box(n,x,t,w,*members(n))
def path(points):
 p=c.beginPath();p.moveTo(*points[0])
 for q in points[1:]:p.lineTo(*q)
 c.drawPath(p)
def triangle(x,y):
 p=c.beginPath();p.moveTo(x,y);p.lineTo(x-8,y-14);p.lineTo(x+8,y-14);p.close();c.setFillColorRGB(1,1,1);c.drawPath(p,stroke=1,fill=1)
def diamond(x,y,dx,dy,filled):
 # Whole end is at x,y; diamond extends toward the part.
 px,py=-dy*6,dx*6
 p=c.beginPath();p.moveTo(x,y);p.lineTo(x+dx*10+px,y+dy*10+py);p.lineTo(x+dx*20,y+dy*20);p.lineTo(x+dx*10-px,y+dy*10-py);p.close()
 c.setFillColorRGB(*( (0,0,0) if filled else (1,1,1)));c.drawPath(p,stroke=1,fill=1)
# Generalizations: the hollow triangle points at the superclass.
fy=framework[1]
path([(280,1045),(280,1059),(760,1059),(760,fy-14)]);triangle(760,fy)
path([(1400,1045),(1400,1059),(930,1059),(930,fy-14)]);triangle(930,fy)
# Each activity contains its own ItemList wrapper. Their static item collection is shared.
path([(525,850),(617,850)]);diamond(525,850,1,0,True);txt(540,867,'1',10);txt(590,867,'1',10);txt(535,831,'item_list',10)
path([(1159,900),(1067,900)]);diamond(1159,900,-1,0,True);txt(1138,917,'1',10);txt(1080,917,'1',10);txt(1080,881,'item_list',10)
# Shared aggregation: ItemList references independently created Item objects.
ly=B['ItemList'][1];path([(842,ly),(842,675)]);diamond(842,ly,0,-1,False);txt(852,ly-27,'0..*',10);txt(852,686,'0..* items {static}',10)
# Composite value part; mutator aliasing is explained in the modeling notes.
path([(617,330),(540,330)]);diamond(617,330,-1,0,True);txt(592,346,'1',10);txt(550,346,'1',10);txt(545,311,'dimensions',10)
# Edit activity also keeps a non-owning reference to an existing item.
# This is drawn as shared aggregation, with the whole at the activity end.
ey=B['EditItemActivity'][1]
path([(1400,ey),(1400,460),(1107,460)]);diamond(1400,ey,0,-1,False);txt(1410,ey-26,'0..*',10);txt(1115,472,'0..1 item',10)
# Concise conventions and evidence keep intended model ownership distinct from Java enforcement.
y=117
for t in [
 'Notation: + public; - private; # protected. {static} denotes a class-level field; {transient} denotes a Java transient field.',
 'Hollow triangle = inheritance. Hollow diamond = aggregation. Filled diamond = composition. Diamonds are drawn at the whole/owner end.',
 'Scope: all fields and explicitly declared constructors/methods of the five application classes are shown. AppCompatActivity is the AndroidX external superclass.',
 'Ownership: activities create their ItemList wrappers; ItemList.items is shared static storage. Item objects are created separately and may be referenced by multiple lists/activities.',
 'Dimensions is modeled as the Item value part (one per valid app item). Java setters/getters permit aliasing or null; exclusive ownership is a design assumption, not enforced by this code.',
 'Activity item_list and dimensions relationships duplicate the typed attributes intentionally. Optional create dependencies, Android widget classes and implicit Java constructors are omitted.'
]:
 txt(35,y,t,10);y-=17
c.showPage();c.save()
d=fitz.open(ROOT/'draft.pdf');d.set_metadata({'title':'SharingApp Items Only — UML Class Diagram','author':'','creator':'','producer':'','creationDate':'','modDate':''});d.save(ROOT/'SharingApp_UML_Class_Diagram.pdf');d.close();(ROOT/'draft.pdf').unlink()
d=fitz.open(ROOT/'SharingApp_UML_Class_Diagram.pdf');d[0].get_pixmap(matrix=fitz.Matrix(.85,.85)).save(ROOT/'SharingApp_UML_Class_Diagram.png')
for n in coords:
 a,m=members(n);print(n,len(a),'fields',len(m),'constructors/methods',B[n])
