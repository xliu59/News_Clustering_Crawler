# -*- coding: utf-8 -*- 
import reportlab.lib.fonts   
from reportlab.lib import colors           
from reportlab.lib.units import inch   
from reportlab.platypus import PageBreak


def pdf_head(canvas, news):
    index = -1
    while index < len(news): 
        canvas.setFont("Helvetica-Bold", 11.5)
        canvas.drawString(1*inch, 1*inch, "Tech News Cluster")
        canvas.rect(1*inch, 1.2*inch, 6.5*inch, 0.12*inch,fill=1)
        for i in range(5): 
            index += 1
            if index < len(news):
                #text_width = 8 if len(news[index]['headline']) > 65 else 11.5
                text_width = 8.5
                canvas.setFont("Helvetica-Bold", text_width)
                canvas.drawString(3*inch, (1.7 + i*2)*inch, news[index]['headline'])
                r1 = (3*inch, 9*inch - ((1.7 + i*2)*inch - 1.55*inch), 4*inch, 9*inch - ((1.7 + i*2)*inch - 1.35*inch)) # this is x1,y1,x2,y2
                canvas.linkURL(news[index]['link'], r1)
                canvas.drawString(3*inch, (1.7 + i*2)*inch + 1.3*inch, 'Read More.')
                
                if len(news[index]) > 3 and news[index]['related_link1'] is not None:
                    r1 = (5*inch, 9*inch - ((1.7 + i*2)*inch - 1.55*inch), 6*inch, 9*inch - ((1.7 + i*2)*inch - 1.35*inch)) # this is x1,y1,x2,y2
                    canvas.linkURL(news[index]['related_link1'], r1)
                    canvas.drawString(5*inch, (1.7 + i*2)*inch + 1.3*inch, 'Related News 1.')

                if len(news[index]) > 4 and news[index]['related_link2'] is not None:
                    r1 = (6*inch, 9*inch - ((1.7 + i*2)*inch - 1.55*inch), 7*inch, 9*inch - ((1.7 + i*2)*inch - 1.35*inch)) # this is x1,y1,x2,y2
                    canvas.linkURL(news[index]['related_link2'], r1)
                    canvas.drawString(6*inch, (1.7 + i*2)*inch + 1.3*inch, 'Related News 2.')

                if news[index]['image'] is not None:
                    canvas.drawImage('./picture_rotation/' + news[index]['image'].split('/')[-1], 1*inch, (1.7 + i*2)*inch, width = 1.8 * inch, height = 1.2 * inch, preserveAspectRatio = True, anchor = 'c')
                else:
                    canvas.drawImage('./picture_rotation/news.jpg', 1*inch, (1.7 + i*2)*inch, width = 1.8 * inch, height = 1.2 * inch, preserveAspectRatio = True, anchor = 'c')

                if i == 4:
                    P = PageBreak()
                    canvas.showPage()
                    break