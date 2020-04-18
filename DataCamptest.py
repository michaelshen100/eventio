#created by Melissa
#parseImage(name) takes in an image and returns a string

from google.cloud import vision

import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="oauth_credentials.json"



def parseImage(name):
	client = vision.ImageAnnotatorClient()

	#from google
	import io

	with io.open(name, 'rb') as image_file:
	        content = image_file.read()

	image = vision.types.Image(content=content)

	response = client.document_text_detection(image=image)

	line = ""

	for page in response.full_text_annotation.pages:
	    for block in page.blocks:
	        print('\nBlock confidence: {}\n'.format(block.confidence))

	        for paragraph in block.paragraphs:
	            print('Paragraph confidence: {}'.format(
	                paragraph.confidence))

	            for word in paragraph.words:
	                word_text = ''.join([
	                    symbol.text for symbol in word.symbols
	                ])
	                print('Word text: {} (confidence: {})'.format(
	                    word_text, word.confidence))

	                '''for symbol in word.symbols:
	                    print('\tSymbol: {} (confidence: {})'.format(
	                        symbol.text, symbol.confidence)) '''

	                if (word_text == ":" or word_text == "," or word_text == ".") is False:
	                	line += " "

	                line += word_text
	return line
