from flask import Flask, render_template, url_for, request
import sys
import json
from ML_Vision_NLP import parseImage
import boto3

AWS_KEY = 'AKIAI4O2XF25JG6TC5UQ'
AWS_SECRET = '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'
REGION = 'us-east-1'

def readAll():
	dynamodb = boto3.resource('dynamodb',aws_access_key_id=AWS_KEY,aws_secret_access_key=AWS_SECRET,region_name=REGION)

	table = dynamodb.Table('Test')

	print("All events:")

	response = table.scan(
		TableName= 'Test'
	    )

	for i in response['Items']:
	    print(i['Key'], ":", i['desc'])
	    dict[i['Key']] =  {'desc': i['desc']}

	return dict
   