# Main Entry
from reportlab.pdfgen.canvas import Canvas  
from reportlab.lib.units import inch   
from PIL import Image
from PIL import ImageOps
import os
from urllib.request import urlopen
import readJson 
import newPDF

data = []
#data = readJson.load('news.json')
#data += readJson.load('res.json')
data = readJson.load('../from_list_to_dict/show.json')

stemmed_data = [x for x in data if x['headline'] is not None]

def get_image():
    """ Download images """
    for x in  stemmed_data:
        if (x['image'] is not None) and (not os.path.exists('./picture/' + x['image'].split('/')[-1])):
            response = urlopen(
                x['image'])
            f = open('./picture/' + x['image'].split('/')[-1], 'wb')
            f.write(response.read())
            f.close()

def convert_image():
    for x in  stemmed_data:
        if (x['image'] is not None) and (not os.path.exists('./picture_rotation/' + x['image'].split('/')[-1])):
            img = Image.open('./picture/' + x['image'].split('/')[-1])
            img = ImageOps.mirror(img)
            img = img.rotate(180)
            img.save('./picture_rotation/' + x['image'].split('/')[-1])

get_image()
convert_image()

can = Canvas('newsCluster.pdf', bottomup = 0)     
newPDF.pdf_head(can, stemmed_data)
#can.drawImage(imageName_2, 1*inch, 2 * inch, width = 1.5 * inch, height = 1 * inch, preserveAspectRatio = True, anchor = 'c')
#can.drawImage(filename, 1*inch, 2 * inch)
#can.rotate(180)
#can.showPage()                      
can.save()   