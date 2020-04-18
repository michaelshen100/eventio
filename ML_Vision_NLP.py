import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./oauth_credentials.json"

#############################################

import six
from google.cloud import vision  # pip install google-cloud-vision
from google.cloud import language  # pip install google-cloud-language
from google.cloud.language import enums
from google.cloud.language import types

#from google
import io

def parseImage(base64_data):
    client = vision.ImageAnnotatorClient()

    # with io.open(name, 'rb') as image_file:
    #         content = image_file.read()

    image = vision.types.Image(content=base64_data)

    response = client.document_text_detection(image=image)

    line = ""

    for page in response.full_text_annotation.pages:
        for block in page.blocks:

            for paragraph in block.paragraphs:

                for word in paragraph.words:
                    word_text = ''.join([
                        symbol.text for symbol in word.symbols
                    ])

                    if (word_text == ":" or word_text == "," or word_text == ".") is False:
                        line += " "

                    line += word_text
    return line

# takes in a string of text, outputs an
def analyze_event_text(string_input):
    client = language.LanguageServiceClient()

    result_dict = {}
    # setting up desc
    result_dict["description"] = string_input

    if isinstance(string_input, six.binary_type):
        string_input = string_input.decode('utf-32')  # UTF-32 because we are working in Python!

    # Instantiates a plain text document.
    document = types.Document(
        content=string_input,
        type=enums.Document.Type.PLAIN_TEXT)

    entities = client.analyze_entities(document).entities

    # Entities we need: LOCATION, ORGANIZATION, EVENT, ADDRESS, DATE
    entity_list = ["LOCATION", "ORGANIZATION", "EVENT", "ADDRESS", "DATE"]
    temp_dict = {}

    for entity in entities:
        entity_type = enums.Entity.Type(entity.type)
        if entity_type.name in entity_list:
            if entity_type.name in result_dict:
                temp_dict[entity_type.name] = temp_dict[entity_type.name] + " " + entity.name
            else:
                temp_dict[entity_type.name] = entity.name

    # setting up name
    if "ORGANIZATION" in temp_dict:
        result_dict["name"] = temp_dict["ORGANIZATION"]
    if "EVENT" in temp_dict:
        if "name" in result_dict.keys():
            result_dict["name"] = result_dict["name"] + " " +temp_dict["EVENT"]
        else:
            result_dict["name"] = "n/a"

    # setting up date-time
    if "DATE" in temp_dict:
        result_dict["date-time"] = temp_dict["DATE"]

    # setting up location
    if "LOCATION" in temp_dict:
        result_dict["location"] = temp_dict["LOCATION"]
    if "ADDRESS" in temp_dict:
        result_dict["location"] = result_dict["location"] + " " + temp_dict["ADDRESS"]

    return result_dict

'''
name: path to image file
returns a dictionary with the keys "name", "location", "date-time", and "desc"
'''
def getEventFromImage(name):
    text = parseImage(name)
    return analyze_event_text(text)

# test code
# text = parseImage("test_img.jpg")
# for item in analyze_event_text(text).items():
#     print(item)
#     print("\n")
