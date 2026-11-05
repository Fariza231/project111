from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3,landscape
from reportlab.lib import colors
from reportlab.lib.utils import simpleSplit
import subprocess,fitz,textwrap
out=Path('/workspace/UWON_Library_Diagrams');source=out/'source';W,H=landscape(A3)
INK=colors.HexColor('#19354C');GRAY=colors.HexColor('#536779')
def text(c,x,y,s,size=10,bold=False):
 c.setFillColor(INK);c.setFont('Helvetica-Bold' if bold else 'Helvetica',size);c.drawString(x,y,s)
def wrap(c,x,y,s,width,size=10,leading=14):
 for ln in simpleSplit(s,'Helvetica',size,width):text(c,x,y,ln,size);y-=leading
 return y
def header(c,title,subtitle):
 text(c,32,H-36,title,20,True);text(c,32,H-58,subtitle,10);c.setStrokeColor(colors.HexColor('#BAC9D5'));c.line(32,H-70,W-32,H-70)
def clean(src,dest):
 d=fitz.open(src);d.set_metadata({'title':dest.stem.replace('_',' '),'author':'','creator':'','producer':'','creationDate':'','modDate':''});d.save(dest);d.close()
def assemble(inputs,dest):
 d=fitz.open()
 for f in inputs:
  with fitz.open(f) as p:d.insert_pdf(p)
 d.set_metadata({'title':dest.stem.replace('_',' '),'author':'','creator':'','producer':'','creationDate':'','modDate':''});d.save(dest)
scenarios=[
('S1','Search the unified catalogue and reserve a resource',
 'An active, authorized patron searches across UWON department holdings using the shared subject vocabulary, reviews recorded availability, and reserves a resource. If an eligible copy is available, the same transaction allocates it and marks the reservation Ready; otherwise the reservation is Waiting without an allocated copy. The patron receives a reference and an email notification attempt, while duplicate active reservations return the existing reference.',
 ['Patron','UWON Library\nSystem','Patron Registry\n(D1)','Catalogue + Inventory\n(D2,D3)','Reservation Store\n(D4)','Email Gateway'],
 [(0,1,'Search(session, keywords / subjects)'),(1,2,'Read active account and category'),(2,1,'Patron identity and facility permission'),(1,3,'Find resources, subjects and department copies'),(3,1,'Matching titles and recorded copy availability'),(1,0,'Display unified results / no matches'),(0,1,'Reserve(resource_id)'),(1,4,'Check existing active reservation'),(4,1,'Existing reference or none'),(1,3,'Recheck and select eligible available copy'),(3,1,'copy_id or no allocatable copy'),(1,4,'Create reservation: Ready + copy_id, or Waiting + null'),(1,3,'If allocated: set copy availability = Reserved'),(4,1,'Committed reservation reference and status'),(1,0,'Reservation reference + Ready / Waiting'),(1,5,'Email reservation reference and status'),(5,1,'Accepted for delivery or delivery error'),(1,0,'Display notification result; reservation remains valid')],
 'Precondition: registered active patron and facility permission. Reservation creation and any copy allocation are one atomic transaction; copies marked Binding, Missing, Damaged or OnLoan cannot be allocated. Alternatives: invalid permission -> deny without writes; no search match -> empty results; no available copy -> Waiting; duplicate hold -> existing reference; email failure does not cancel a committed reservation.'),
('S2','Borrow a reserved copy, return it and preserve borrower history',
 'A patron presents a Ready reservation, and authorized library staff scan its allocated copy. The system checks account status, the applicable loan policy and reservation ownership before recording the loan and due time. On return, staff record the copy condition, the loan is closed without deleting borrower history, and the copy becomes Available or is withheld as Damaged.',
 ['Patron','Library Staff','UWON Library\nSystem','Patron + Policy\n(D1)','Inventory + Holds\n(D3,D4)','Loan Store\n(D5)'],
 [(0,1,'Present patron identity and reservation reference'),(1,2,'Issue request(staff session, patron, copy barcode)'),(2,3,'Check staff permission, patron status and loan policy'),(3,2,'Authorized staff, eligible patron and limits'),(2,4,'Read Ready hold and allocated Reserved copy'),(4,2,'Matching patron/resource/copy or refusal reason'),(2,5,'Read active-loan count and active-copy loan'),(5,2,'Current loan count and copy-loan result'),(2,5,'Create Loan(patron, copy, reservation, due_at, condition_out)'),(2,4,'Mark hold Fulfilled; mark copy OnLoan'),(5,2,'Committed loan reference and due time'),(2,0,'Loan receipt and due time'),(0,1,'Return physical copy'),(1,2,'Return report(loan/copy, inspected condition)'),(2,5,'Set returned_at and condition_in; retain borrower link'),(2,4,'Set copy Available or Damaged / unavailable'),(2,0,'Return receipt and recorded condition'),(1,2,'Request authorized copy-loan history'),(2,5,'Read loans for copy, including closed loans'),(5,2,'Borrower references, dates and recorded conditions'),(2,1,'Authorized traceability report')],
 'Preconditions: active patron, authorized staff, Ready reservation with allocated copy, and a known loan policy. Loan creation, hold fulfillment and copy status change are atomic; return updates are atomic and closed loans are retained. Alternatives: over limit, wrong patron, missing physical copy or unavailable copy -> refuse before issue; duplicate return -> existing return receipt; damage history supports investigation but does not by itself prove who caused damage.'),
('S3','Access a licensed e-journal or partner digital resource',
 'An authenticated patron selects a digital resource and requests access. The system checks the patron category and either an active subscription or an applicable partner-university agreement, then asks the provider for an access grant. A valid provider response produces a short-lived access link and an audit record; denied or unavailable access is recorded without exposing protected content.',
 ['Patron','UWON Library\nSystem','Patron Registry\n(D1)','Routes + Rights\n(D2,D6)','Digital Provider /\nPartner University','Access Audit\n(D7)'],
 [(0,1,'Request digital access(session, resource_id)'),(1,2,'Read active patron and category'),(2,1,'Identity and facility permission'),(1,3,'Read resource route, provider and entitlement records'),(3,1,'Route + subscription / agreement validity and rules'),(1,1,'Evaluate resource scope, category and validity interval'),(1,4,'Request access grant for authorized resource and category'),(4,1,'Grant URL + expiry, denial, or provider unavailable'),(1,5,'Record attempt(patron, route, entitlement reference, outcome)'),(5,1,'Audit reference'),(1,0,'Granted: short-lived link; otherwise reason / retry guidance')],
 'Precondition: a selected digital catalogue record and active registered patron. Grant requires an active, in-scope Subscription OR Agreement plus provider acceptance; no entitlement means deny before the provider grant request. Each entitlement/provider attempt is retained with Granted, Denied or ProviderUnavailable; identity/facility denials stop before an attempt is created; a granted attempt references exactly one entitlement source, and the audit does not store a reusable access token.')]
# Sequence charts, one clearly explained page per scenario.
seqs=[]
for sid,title,description,participants,messages,notes in scenarios:
 f=out/(sid+'_Event_Trace_raw.pdf');c=canvas.Canvas(str(f),pagesize=(W,H));header(c,sid+' — Event Trace Diagram',title)
 wrap(c,32,H-93,description,W-64,10,14)
 top=H-170;left=90;step=(W-180)/(len(participants)-1);xs=[left+i*step for i in range(len(participants))]
 for x,name in zip(xs,participants):
  c.setFillColor(colors.HexColor('#EDF3F8'));c.setStrokeColor(INK);c.rect(x-82,top,164,43,fill=1,stroke=1)
  for j,ln in enumerate(name.split('\n')):text(c,x-74,top+27-j*13,ln,10,True)
  c.setDash(3,3);c.line(x,top,x,165);c.setDash()
 start=top-22;dy=min(23,(start-180)/len(messages))
 for i,(a,b,label) in enumerate(messages):
  y=start-i*dy;x1=xs[a];x2=xs[b]
  c.setStrokeColor(INK);c.setLineWidth(.9)
  if a==b:
   c.line(x1,y,x1+55,y);c.line(x1+55,y,x1+55,y-9);c.line(x1+55,y-9,x1,y-9)
   c.line(x1,y-9,x1+6,y-5);c.line(x1,y-9,x1+6,y-13);text(c,x1+63,y-5,str(i+1)+'. '+label,8.4)
  else:
   c.line(x1,y,x2,y);sgn=1 if x2>x1 else -1;c.line(x2,y,x2-sgn*6,y+3);c.line(x2,y,x2-sgn*6,y-3)
   tw=c.stringWidth(str(i+1)+'. '+label,'Helvetica',8.4);text(c,(x1+x2-tw)/2,y+5,str(i+1)+'. '+label,8.4)
 text(c,32,142,'Scenario conditions and alternatives',11,True);wrap(c,32,123,notes,W-64,10,14)
 text(c,32,37,'Time proceeds downward. Logical repositories refer to the same persistent data groups used in the ER and DFD views.',9)
 c.showPage();c.save();dest=out/(sid+'_Event_Trace.pdf');clean(f,dest);seqs.append(dest)
assemble(seqs,out/'Q1_Event_Trace_Diagrams.pdf')
# ER views: explicit min..max multiplicities and PK/FK labels.
entities={
'PATRON':['PK patron_id','UK university_ref','email','category','active'],
'RESOURCE':['PK resource_id','kind: Book / Proceedings / Journal','title','standard_identifier','searchable_text'],
'SUBJECT':['PK subject_id','UK normalized_term'],
'RESOURCE_SUBJECT':['PK, FK resource_id','PK, FK subject_id'],
'COPY':['PK copy_id','FK resource_id','FK department_id','unit_label: edition / issue / volume','shelf_location','availability','condition'],
'DEPARTMENT':['PK department_id','name','library_location'],
'RESERVATION':['PK reservation_id','FK patron_id','FK resource_id','FK allocated_copy_id [nullable]','requested_at','status: Waiting / Ready / Fulfilled / Cancelled'],
'LOAN':['PK loan_id','FK patron_id','FK copy_id','FK reservation_id [nullable, unique]','issued_at / due_at','returned_at [nullable]','condition_out','condition_in [nullable until returned]'],
'LOAN_POLICY':['PK policy_id','UK patron_category','max_active_loans','loan_period_days'],
'PROVIDER':['PK provider_id','name','type: Publisher / PartnerUniversity'],
'ACCESS_ROUTE':['PK route_id','FK resource_id','FK provider_id','provider_resource_ref','endpoint'],
'SUBSCRIPTION':['PK subscription_id','FK route_id','valid_from / valid_until','status','category_rule'],
'AGREEMENT':['PK agreement_id','FK provider_id','valid_from / valid_until','resource_scope_rule','category_rule'],
'ACCESS_ATTEMPT':['PK access_id','FK patron_id','FK route_id','FK subscription_id [nullable]','FK agreement_id [nullable]','attempted_at','outcome: Granted / Denied / ProviderUnavailable']}
from html import escape as he
def ernode(name,attrs):return name+' [label=<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="5"><TR><TD BGCOLOR="#E8F0F6"><B>'+name+'</B></TD></TR>'+''.join('<TR><TD ALIGN="LEFT">'+he(a)+'</TD></TR>' for a in attrs)+'</TABLE>>];\n'
def eredge(a,b,relation,ca='1',cb='0..*'):return f'{a} -> {b} [dir=none,label="{relation}",taillabel="{ca}",headlabel="{cb}",labeldistance=2.0,labelangle=28];\n'
erdefs=[
('S1',['PATRON','RESOURCE','SUBJECT','RESOURCE_SUBJECT','COPY','DEPARTMENT','RESERVATION'],[
 ('PATRON','RESERVATION','places'),('RESOURCE','RESERVATION','requested title'),('RESOURCE','COPY','has holdings'),('DEPARTMENT','COPY','owns'),('RESOURCE','RESOURCE_SUBJECT','classified by'),('SUBJECT','RESOURCE_SUBJECT','indexes'),('COPY','RESERVATION','allocation history','0..1','0..*')],
 'Each Reservation belongs to exactly one Patron and Resource; allocated_copy_id is null while Waiting and required while Ready. Any allocated copy must belong to the same Resource. One copy has at most one active Ready allocation; only an eligible Available copy can become Reserved. RESOURCE_SUBJECT has a composite primary key; subjects are shared across departments.'),
('S2',['PATRON','LOAN_POLICY','RESOURCE','DEPARTMENT','COPY','RESERVATION','LOAN'],[
 ('PATRON','LOAN','borrows'),('COPY','LOAN','loan history'),('RESOURCE','COPY','has'),('DEPARTMENT','COPY','owns'),('PATRON','RESERVATION','places'),('RESOURCE','RESERVATION','requested title'),('COPY','RESERVATION','allocated copy','0..1','0..*'),('RESERVATION','LOAN','fulfilled by','0..1','0..1'),('LOAN_POLICY','PATRON','governs category')],
 'In this view PATRON also has FK policy_id -> LOAN_POLICY. A Loan always links one Patron to one Copy; an optional reservation_id is unique and, when supplied, must match the same patron and allocated copy. At most one Loan per Copy can have returned_at null. Keep closed loans and condition records; return does not delete history. Copy becomes Available only if inspection permits circulation.'),
('S3',['PATRON','RESOURCE','PROVIDER','ACCESS_ROUTE','SUBSCRIPTION','AGREEMENT','ACCESS_ATTEMPT'],[
 ('RESOURCE','ACCESS_ROUTE','available through'),('PROVIDER','ACCESS_ROUTE','serves'),('ACCESS_ROUTE','SUBSCRIPTION','licensed by'),('PROVIDER','AGREEMENT','covered by'),('PATRON','ACCESS_ATTEMPT','requests'),('ACCESS_ROUTE','ACCESS_ATTEMPT','requested route'),('SUBSCRIPTION','ACCESS_ATTEMPT','entitlement used','0..1','0..*'),('AGREEMENT','ACCESS_ATTEMPT','entitlement used','0..1','0..*')],
 'For Granted attempts, exactly one of subscription_id or agreement_id is present (XOR); its route/provider, scope, category rule and validity interval must match the requested access. A Denied attempt may have neither reference. Partner access is represented by PROVIDER.type = PartnerUniversity plus an applicable Agreement. A grant depends on provider acceptance; audit stores outcome and references, not reusable grant tokens.')]
def graph_pdf(dotpath,title,subtitle,notes,dest,legend):
 raw=dotpath.with_suffix('.graph.pdf');subprocess.run(['dot','-Tpdf',str(dotpath),'-o',str(raw)],check=True)
 pg=fitz.open();page=pg.new_page(width=W,height=H);g=fitz.open(raw);page.show_pdf_page(fitz.Rect(26,105,W-26,H-90),g,0,keep_proportion=True)
 # ReportLab overlay preserves readable selectable labels and explanations.
 overlay=out/'_overlay.pdf';c=canvas.Canvas(str(overlay),pagesize=(W,H));header(c,title,subtitle)
 text(c,32,91,legend,9);wrap(c,32,72,notes,W-64,9,12);c.showPage();c.save()
 ov=fitz.open(overlay);page.show_pdf_page(page.rect,ov,0);pg.set_metadata({'title':title,'author':'','creationDate':'','modDate':''});pg.save(dest)
ers=[]
for sid,nodes,edges,notes in erdefs:
 dot='digraph ER { graph [rankdir=LR, nodesep=0.5, ranksep=1.1, splines=spline, bgcolor="white", pad=0.3]; node [shape=plain,fontname="Helvetica",fontsize=10]; edge [fontname="Helvetica",fontsize=9,arrowsize=0.7];\n'
 for n in nodes:
  attrs=entities[n][:]
  if sid=='S2' and n=='PATRON':attrs.append('FK policy_id')
  dot+=ernode(n,attrs)
 for e in edges:dot+=eredge(*e)
 dot+='}\n';dp=source/(sid+'_ER.dot');dp.write_text(dot);dest=out/(sid+'_ER.pdf');graph_pdf(dp,sid+' — Entity Relationship Diagram',next(x[1] for x in scenarios if x[0]==sid),notes,dest,'PK = primary key; FK = foreign key; UK = unique key. Numbers at an entity end show its allowed multiplicity for one entity at the opposite end.');ers.append(dest)
assemble(ers,out/'Q2_Entity_Relationship_Diagrams.pdf')
# DFDs: logical boundary, external entities, numbered processes, open-ended stores.
def store(id,name):return id+' [shape=plain,label=<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="7"><TR><TD BORDER="1">'+id+'</TD><TD BORDER="1" SIDES="TB">'+name+'</TD></TR></TABLE>>];\n'
def flow(a,b,label):
 label='\\n'.join(textwrap.wrap(label,27,break_long_words=False))
 return f'{a} -> {b} [label="{label}"];\n'
dfddefs=[
('S1',{'Patron':'Library Patron','Email':'Email Gateway'}, {'p11':'1.1 Authorize patron','p12':'1.2 Search catalogue','p13':'1.3 Reserve resource','p14':'1.4 Notify patron'}, {'D1':'Patrons','D2':'Resources + Subjects','D3':'Copies + Departments','D4':'Reservations'},[
('Patron','p11','session + search criteria'),('D1','p11','active identity + category'),('p11','Patron','authorization denial'),('p11','p12','authorized search criteria'),('D2','p12','resource + subject records'),('D3','p12','holding locations + availability'),('p12','Patron','unified search results'),('Patron','p13','selected resource + session'),('D1','p13','identity + category'),('D3','p13','eligible copy state'),('D4','p13','existing active reservations'),('p13','D4','new reservation record'),('p13','D3','allocated-copy Reserved state'),('p13','Patron','Ready / Waiting reference or refusal'),('p13','p14','committed hold + recipient data'),('p14','Email','reservation email'),('Email','p14','delivery acceptance / error'),('p14','Patron','notification status')],
 'D2 maps RESOURCE, SUBJECT and RESOURCE_SUBJECT; D3 maps COPY and DEPARTMENT; D4 maps RESERVATION. Process 1.3 performs copy recheck plus reservation/copy update atomically. D1 is read for every restricted operation. Email failure affects notification status, not the committed hold.'),
('S2',{'Patron':'Library Patron','Staff':'Authorized Library Staff'}, {'p21':'2.1 Validate checkout','p22':'2.2 Issue loan','p23':'2.3 Record return','p24':'2.4 Trace loan history'}, {'D1':'Patrons + Loan policies','D3':'Copies + Departments','D4':'Reservations','D5':'Loans'},[
('Patron','p21','patron identity + hold reference'),('Staff','p21','staff session + copy barcode'),('D1','p21','account + category + loan rules'),('D3','p21','copy availability + condition'),('D4','p21','Ready reservation + allocation'),('D5','p21','active loan count + copy loans'),('p21','Patron','eligibility / limit refusal'),('p21','p22','validated patron + copy + hold'),('p22','D5','new Loan + due time + condition_out'),('p22','D3','copy OnLoan state'),('p22','D4','Fulfilled reservation state'),('p22','Patron','loan receipt + due time'),('Patron','p23','returned copy / loan reference'),('Staff','p23','staff session + inspected condition'),('D1','p23','staff authorization'),('D5','p23','active / already closed loan'),('p23','D5','returned_at + condition_in'),('p23','D3','Available / Damaged copy state'),('p23','Patron','return receipt'),('Staff','p24','authorized copy-history criteria'),('D1','p24','staff authorization'),('D5','p24','retained loan history'),('p24','Staff','borrower / condition history report')],
 'D1 maps PATRON and LOAN_POLICY; D3 maps COPY/DEPARTMENT; D4 maps RESERVATION; D5 maps LOAN. Issue and return updates each form an atomic unit. Patron and Staff are external roles, not data stores; recorded patron identity remains in D1 and loan links in D5. Read-only history access is restricted to authorized staff.'),
('S3',{'Patron':'Library Patron','Provider':'Digital Provider / Partner University'}, {'p31':'3.1 Authorize patron','p32':'3.2 Evaluate entitlement','p33':'3.3 Obtain provider grant','p34':'3.4 Record access outcome'}, {'D1':'Patrons','D2':'Resources','D6':'Providers + Routes + Rights','D7':'Access attempts'},[
('Patron','p31','session + resource request'),('D1','p31','active identity + category'),('p31','Patron','identity / facility denial'),('p31','p32','authorized patron + resource'),('D2','p32','digital resource metadata'),('D6','p32','route + provider + subscription / agreement'),('p32','p33','eligible access context'),('p32','p34','denied entitlement outcome'),('p33','Provider','resource + authorized access context'),('Provider','p33','grant URL + expiry / denial / unavailable'),('p33','p34','provider outcome + entitlement reference'),('p34','D7','access-attempt audit record'),('p34','Patron','temporary link or reason / retry guidance')],
 'D6 maps PROVIDER, ACCESS_ROUTE, SUBSCRIPTION and AGREEMENT; D7 maps ACCESS_ATTEMPT. Only eligible requests reach the provider; granted access also requires provider acceptance. Attempt records preserve outcome and selected entitlement source, while reusable access tokens are not persisted. No entitlement or provider denial produces no content link.')]
dfds=[]
for sid,externals,procs,stores,edges,notes in dfddefs:
 dot='digraph DFD { graph [rankdir=TB, nodesep=0.65, ranksep=1.0, splines=spline, pad=0.4, bgcolor="white"]; node [fontname="Helvetica",fontsize=11]; edge [fontname="Helvetica",fontsize=11,arrowsize=0.65];\n'
 for id,label in externals.items():dot+=id+' [shape=box,label="'+label+'",style=solid];\n'
 dot+='subgraph cluster_UWON { label="UWON Library System — logical data-flow boundary"; color="#A8BCCC"; fontname="Helvetica"; fontsize=12;\n'
 for id,label in procs.items():dot+=id+' [shape=box,style="rounded,filled",fillcolor="#EDF3F8",label="'+label+'"];\n'
 for id,label in stores.items():dot+=store(id,label)
 dot+='}\n'
 for i,(a,b,l) in enumerate(edges,1):dot+=flow(a,b,f'F{i:02d}')
 dot+='}\n';dp=source/(sid+'_DFD.dot');dp.write_text(dot);dest=out/(sid+'_DFD.pdf');graph_pdf(dp,sid+' — Dataflow Diagram',next(x[1] for x in scenarios if x[0]==sid),notes,dest,'Rectangles = external entities; rounded numbered boxes = processes; open-ended D# boxes = stores; F# arrows identify named data in the following flow dictionary, not time sequence.');dfds.append(dest)
 # Flow dictionary keeps the diagram uncluttered and gives every arrow a precise name.
 dictpath=out/(sid+'_DFD_Dictionary.pdf');c=canvas.Canvas(str(dictpath),pagesize=(W,H))
 header(c,sid+' — Dataflow Dictionary',next(x[1] for x in scenarios if x[0]==sid))
 text(c,32,H-97,'Each F-number on the preceding diagram identifies the named data flow listed below; it does not indicate execution order.',11)
 text(c,32,H-124,'FLOW',11,True);text(c,100,H-124,'FROM',11,True);text(c,360,H-124,'TO',11,True);text(c,630,H-124,'DATA',11,True)
 names={**externals,**procs,**{k:k+' '+v for k,v in stores.items()}}
 y=H-151
 for i,(a,b,label) in enumerate(edges,1):
  text(c,32,y,f'F{i:02d}',11,True);text(c,100,y,names[a],10);text(c,360,y,names[b],10);wrap(c,630,y,label,W-670,11,12)
  c.setStrokeColor(colors.HexColor('#D6E0E7'));c.line(32,y-9,W-32,y-9);y-=25
 wrap(c,32,80,notes,W-64,10,14);c.showPage();c.save()
 temp=out/(sid+'_DFD_Combined.pdf');assemble([dest,dictpath],temp);temp.replace(dest)
assemble(dfds,out/'Q3_Dataflow_Diagrams.pdf')
# Required text responses: general 6 sentences, specific 6, completeness 5.
general='Entity relationship diagrams describe the structure of persistent data, while dataflow diagrams describe how the system receives, transforms and stores that data. The first connection is between ER entities and DFD data stores: a store can group several related entity types rather than requiring one store per table. The second connection is between ER attributes and the information carried by named data flows, such as identifiers, due times and condition values. The third connection is between ER relationships and the processes that create, validate or change those relationships, such as linking a patron to a copy through a loan. The ER view supplies cardinality and integrity constraints that those processes must preserve. An external Patron or Staff actor in a DFD is a participant role, whereas a PATRON entity in the ER view is the stored record describing a person.'
specific='In scenario S2, D1 groups PATRON and LOAN_POLICY, D3 groups COPY and DEPARTMENT, D4 stores RESERVATION, and D5 stores LOAN. These are concrete examples of ER entities represented by DFD data stores. The issue and return flows carry loan_id, patron_id, copy_id, due_at and condition values, illustrating the connection between ER attributes and flow contents. Process 2.2 creates the Patron-to-Copy association represented by LOAN, changes the linked reservation to Fulfilled and marks the copy OnLoan. Process 2.3 updates returned_at and condition_in without deleting the loan, preserving the same relationships for borrower traceability. Process 2.4 reads those retained records to provide authorized staff with the copy history, so the event trace, ER view and DFD describe the same lifecycle.'
complete='For these three selected scenarios, I checked every event-trace input, response and persistent state change against a corresponding DFD process, data flow or store. I also checked that every persistent store maps to ER entities, every identifier and stored outcome has an appropriate attribute, and the required relationships have keys and explicit cardinalities. The diagrams include the important refusal paths and integrity rules: facility authorization, duplicate reservations, copy eligibility, loan limits, preserved return history and entitlement checks. Successful and unsuccessful outcomes are distinguished, and no DFD flow connects an external actor directly to a data store. This establishes traceable coverage of the modeled scenarios, not a claim that every future acquisition, registration, supplier or administrative workflow of the entire university has been specified.'
(out/'Q4_Explanation.txt').write_text('GENERAL RELATIONSHIP (6 sentences)\n'+general+'\n\nSPECIFIC EXAMPLE: S2 (6 sentences)\n'+specific+'\n\nCOMPLETENESS (5 sentences)\n'+complete+'\n')
# Supplementary model assumptions and scope.
(out/'Model_Notes.txt').write_text('''UWON LIBRARY SYSTEM — MODEL NOTES

Three representative patron scenarios are modeled; this is not a complete design of every university workflow. Registration is a precondition, and supplier comparison/order submission is a separate staff acquisition workflow outside these three selected scenarios.

Logical stores D1-D7 are grouped views of a common persistent library database, not necessarily separate physical databases. Cross-store issue/reservation updates are therefore modeled as atomic transactions. Session authentication and category-based facility permissions are checked on every restricted operation; credential/session protocol details and policy administration are outside the displayed ER projections.

Reservation allocation: Waiting has no allocated copy; Ready has a matching eligible copy marked Reserved; issue changes Ready to Fulfilled and the copy to OnLoan. No more than one active allocation or active loan can occupy a copy. Physical Binding, Missing or Damaged copies are unavailable. A mismatch at the shelf triggers refusal and inventory correction, not a successful loan.

Loan policy: PATRON.policy_id is shown in S2 where its constraints are relevant. Other scenario ER views display relevant projections of the same entity, not conflicting table definitions. Loan history is retained; condition history supports review without proving responsibility for damage.

Digital access: a granted attempt uses exactly one applicable active entitlement source (Subscription or Agreement); rights must cover the route/provider, resource, category and validity interval. Provider acceptance is additionally required. Audit keeps outcome/references, not reusable access tokens.

Multiplicity labels show the number of entities at their adjacent end for one entity at the opposite end. DFD external entity roles are not identical to stored ER records; a store may contain several entities. DFD flows are data movement, not a sequence chart.

No personal author name or submission date is included. No running implementation or tests of a live library service are claimed.
''')
assemble([out/'Q1_Event_Trace_Diagrams.pdf',out/'Q2_Entity_Relationship_Diagrams.pdf',out/'Q3_Dataflow_Diagrams.pdf'],out/'UWON_All_Diagrams.pdf')
# Preview: one PNG per scenario/type.
for kind,paths in [('Event_Trace',seqs),('ER',ers),('DFD',dfds)]:
 for i,f in enumerate(paths,1):
  with fitz.open(f) as d:d[0].get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(out/(f'S{i}_{kind}.png'))
for f in out.rglob('*'):
 if f.is_file():f.chmod(0o644)
out.chmod(0o755)
print('Created 3 event traces, 3 ER diagrams, 3 DFDs, three upload PDFs and text answers.')
