
#DOWNLOADING THE WALL STREET JOURNAL (SECTIONS A&B) AS PDF

import requests as rq
import os
import pandas as pd

basePath = 'BASE PATH'
fileOutPath = 'OUTPUT PATH'

startDate = 'START DATE' #format 'YYYY-MM-DD'
endDate = 'END DATE' #format 'YYYY-MM-DD'

dates = pd.bdate_range(startDate, endDate, freq='C', weekmask='Mon Tue Wed Thu Fri Sat')

def dateFormat(x):
    date = str(x).split('-')
    correctFmt = str(date[0]+date[1]+date[2]).split(' ')
    return correctFmt[0]
    
dateRange = [dateFormat(date) for date in dates]

pageRange = [str(num).zfill(3) for num in range(1,26)]

baseURL = 'http://online.wsj.com/public/resources/documents/print/WSJ_-'
sections = ['A','B']

#for time and request monitoring
from time import time
start_time = time()
requests = 0

for date in dateRange:

    filePaths = []
    
    for section in sections:
        for page in pageRange:
            url = baseURL + section + page + '-' + date + '.pdf'
            response = rq.get(url)
            if response.status_code == 200:
                location = basePath + date + '-' + section + '-' + page
                filePaths.append(location)           
                with open(location, 'wb') as f:
                    f.write(response.content)
                print('Added ' + date + '-' + section + '-' + page)
            else:
                pass

#merge PDFs
    from PyPDF2 import PdfFileMerger
    merger = PdfFileMerger()

    for file in filePaths:
        if os.path.getsize(file) < 2500*1024:
            merger.append(file)
        else:
            print('Page skipped from merge. ' + file + ' is too large')
            pass        
    finalName = 'wsj-' + date    
    merger.write(fileOutPath + finalName + '.pdf')
    print('Merged ' + date)


#email PDF to self
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders
     
    fromaddr = 'SENDING EMAIL ADDRESS'
    toaddr = 'RECEIVING EMAIL ADDRESS'
    password = 'SENDING EMAIL ADDRESS PASSWORD'
     
    msg = MIMEMultipart()
     
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = 'WSJ - ' + date
     
    body = 'Your emailed copy of the WSJ from ' + date
     
    msg.attach(MIMEText(body, 'plain'))
     
    filename = finalName
    attachment = open(fileOutPath + finalName + '.pdf', 'rb')
     
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
     
    msg.attach(part)
     
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, password)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()

    print('Emailed - WSJ ' + date)

#time monitoring (one request per date)
    requests += 1
    elapsed_time = time() - start_time
    print('WSJ editions completed: {}; Total Time: {} min; Frequency: {} sec/edition'.format(requests, round(elapsed_time/60,2), \
    round(elapsed_time/requests,2)))


# NOTE
#   - email code from http://naelshiab.com/tutorial-send-email-python/ 
#   - PDF merging code from https://www.youtube.com/watch?v=aaciXxmsMqs
