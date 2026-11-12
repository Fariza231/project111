from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib import colors
from reportlab.lib.utils import simpleSplit
import fitz,json
OUT=Path(__file__).resolve().parents[1]
W,H=landscape(A3)
INK=colors.HexColor('#173344');MUTED=colors.HexColor('#415460');RULE=colors.HexColor('#A8BAC4');ACCENT=colors.HexColor('#E7F0F4')
blocks={
'Key Partnerships':[
'University career centers: student referrals and cohort access agreements.',
'Student societies: outreach and trusted introductions.',
'Qualified career coaches and content experts: specialist guidance.',
'Graduate employers: hiring expectations and current opportunities.',
'Hosting, video-call and payment providers: service infrastructure.'],
'Key Activities':[
'Create and update practical career guidance content.',
'Assess student goals and identify suitable career directions.',
'Deliver tailored CV reviews and interview practice.',
'Maintain the platform and support users.',
'Acquire university partners and reach students.'],
'Key Resources':[
'Accessible online platform, student profiles and learning tools.',
'Qualified career advisers and coaches.',
'Career assessments, CV templates and reusable learning materials.',
'Reliable graduate job-market information.',
'University and employer relationships.'],
'Value Propositions':[
'For students: affordable, personalized help to move from university into a suitable first full-time job.',
'Career exploration, tailored CV feedback and interview preparation in one place.',
'Clear action plans and practical next steps that build job-search confidence.',
'Flexible online access around study commitments.',
'For universities: extend career-support capacity with reusable learning and targeted adviser support.'],
'Customer Relationships':[
'Personalized onboarding and individual action plans.',
'Progress check-ins and useful reminders.',
'Trusted adviser support through messaging and video consultations.',
'Clear service allowances and timely responses.',
'Dedicated contact for university cohort accounts.'],
'Channels':[
'Awareness: university career centers, student societies and targeted social media.',
'Sign-up: website explaining service plans and university access.',
'Delivery: online platform, video calls and messaging.',
'Retention: email and in-platform progress updates.'],
'Customer Segments':[
'PRIMARY USERS / BUYERS',
'Final-year university students actively seeking their first full-time job.',
'Students with limited access to personalized career guidance and a need for affordable support.',
'SECONDARY BUYERS',
'Universities purchasing access packages for graduating student cohorts.',
'Initial focus: students reached through partner university career centers.'],
'Cost Structure':[
'Fixed costs: platform development and maintenance; content creation; partnership management and administration.',
'Variable costs: adviser time for CV feedback and coaching; payment processing; hosting and support as usage grows.',
'Acquisition costs: student outreach and targeted marketing campaigns.',
'Cost controls: reuse self-paced resources, define included feedback allowances and charge separately for intensive coaching.'],
'Revenue Streams':[
'Affordable student subscriptions for career assessments, learning resources, CV feedback and interview preparation.',
'Optional fees for individual coaching and additional personalized support.',
'University-funded access packages for final-year cohorts, reducing direct student payments.',
'Pricing logic: tiered support allowances align adviser workload with recurring revenue; test prices and renewal demand in a pilot.']}
def text(c,x,y,s,size=10,bold=False,color=INK):
 c.setFillColor(color);c.setFont('Helvetica-Bold' if bold else 'Helvetica',size);c.drawString(x,y,s)
def box(c,title,x,y,w,h):
 c.setFillColor(colors.white);c.setStrokeColor(RULE);c.setLineWidth(.8);c.rect(x,y,w,h,fill=1,stroke=1)
 c.setFillColor(ACCENT);c.rect(x+.5,y+h-32,w-1,31.5,fill=1,stroke=0)
 text(c,x+12,y+h-22,title.upper(),10.5,True)
 cursor=y+h-50
 size=10.3;leading=14.3;gap=9
 for item in blocks[title]:
  if item in ['PRIMARY USERS / BUYERS','SECONDARY BUYERS']:
   text(c,x+12,cursor,item,8.6,True,color=MUTED);cursor-=18
   continue
  wrapped=simpleSplit(item,'Helvetica',size,w-37)
  text(c,x+12,cursor,'•',size)
  for line in wrapped:
   text(c,x+24,cursor,line,size);cursor-=leading
  cursor-=gap
 assert cursor>=y+4,(title,cursor,y,h)
raw=OUT/'draft.pdf';c=canvas.Canvas(str(raw),pagesize=(W,H))
text(c,28,H-28,'BUSINESS MODEL CANVAS',11,True,color=MUTED)
text(c,28,H-58,'Affordable Career Support for University Students',24,True)
challenge='How can we help university students access affordable, personalized career guidance so they can identify suitable career paths and find their first jobs?'
text(c,28,H-79,challenge,10.3)
left=28;bottom=48;totalW=W-56;col=totalW/5;top=H-100;upperBottom=256;upperH=top-upperBottom;half=upperH/2
box(c,'Key Partnerships',left,upperBottom,col,upperH)
box(c,'Key Activities',left+col,upperBottom+half,col,half)
box(c,'Key Resources',left+col,upperBottom,col,half)
box(c,'Value Propositions',left+2*col,upperBottom,col,upperH)
box(c,'Customer Relationships',left+3*col,upperBottom+half,col,half)
box(c,'Channels',left+3*col,upperBottom,col,half)
box(c,'Customer Segments',left+4*col,upperBottom,col,upperH)
box(c,'Cost Structure',left,bottom,totalW/2,208)
box(c,'Revenue Streams',left+totalW/2,bottom,totalW/2,208)
text(c,28,25,'Proposed model: validate willingness to pay, adviser capacity and university cohort renewals through a small pilot.',9,color=MUTED)
c.showPage();c.save()
d=fitz.open(raw);d.set_metadata({'title':'Affordable Career Support for University Students - Business Model Canvas','author':'','creator':'','producer':'','creationDate':'','modDate':''});d.save(OUT/'Career_Support_Business_Model_Canvas.pdf');d.close();raw.unlink()
d=fitz.open(OUT/'Career_Support_Business_Model_Canvas.pdf');assert len(d)==1
content=d[0].get_text()
for heading in blocks:assert heading.upper() in content
assert not d.metadata['author'] and not d.metadata['creationDate']
d[0].get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(OUT/'Career_Support_Business_Model_Canvas.png')
(OUT/'Canvas_Content.json').write_text(json.dumps({'project_title':'Affordable Career Support for University Students','challenge_statement':challenge,'building_blocks':blocks},indent=2))
print('Created one-page PDF and PNG; all nine building blocks verified; metadata cleared.')
