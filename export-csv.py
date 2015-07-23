import urllib2, base64, json
import socket
import xlwt
import json
import inflection
import sys
from datetime import datetime 
import csv

# set timeout
# timeout in seconds
timeout = 10000
socket.setdefaulttimeout(timeout)

URL = "http://118.91.130.18:9979"
USERLOGIN = "demo1"
PASSWORDLOGIN = "1"

resultJson = ""
formNames = {}

allUsers = ['user1', 'user2', 'user3', 'user4', 'user5', 'user6', 'user8', 'user9', 'user10', 'user11', 'user12', 'user13', 'user14']

# fetch forms
for user in allUsers:
	apiUrl = URL + "/form-submissions?anm-id="+user+"&timestamp=0&batch-size=100"
	try:
		print("Fetch form submissions %s" % user)
		req = urllib2.Request(apiUrl)
		base64String = base64.encodestring('%s:%s' % (USERLOGIN, PASSWORDLOGIN)).replace('\n', '')
		req.add_header("Authorization", "Basic %s" % base64String)
		result = urllib2.urlopen(req)
		resultJson = json.load(result.fp)
		jsonData = json.loads(json.dumps(resultJson))

		for row in jsonData:
			if not row["formName"] in formNames:
				formNames[row["formName"]] = []
			jsondata = (json.loads(row["formInstance"]))
			jsonfield = []
			jsonfield.append({'name' : "userID", 'value' : row["anmId"]})
			jsonfield.extend(jsondata["form"]["fields"])
			jsonfield.append({'name' : "clientVersionSubmissionDate", 'value' : datetime.fromtimestamp(int(row["clientVersion"])/1000.0).strftime('%Y-%m-%d %H:%M:%S')})
			jsonfield.append({'name' : "serverVersionSubmissionDate", 'value' : datetime.fromtimestamp(int(row["serverVersion"])/1000.0).strftime('%Y-%m-%d %H:%M:%S')})
			formNames[row["formName"]].append(jsonfield)

		result.close()
	except(socket.timeout, urllib2.HTTPError) as e:
		print("Error : %s " % e)
		sys.exit(1)

# create csv
for sheet in formNames:
	print("Create %s" % sheet)

	# create worksheet
	worksheetTitle = inflection.humanize(sheet[0:30])
	titleArray = []
	formData = []
	allForms = []
	
	# put the json data to array
	for idx1, data1 in enumerate(formNames[sheet]):
		formData.append([])
		formData[idx1] = {}
		for idx2, data2 in enumerate(data1):
			if not data2['name'] in titleArray:
				titleArray.insert(idx2, data2['name'])
			value = data2.get('value')
			if value is None:
				value = '-'
			formData[idx1][data2['name']] = value

	allForms.append(titleArray)
	for idx1, data1 in enumerate(formData):
		aForm = []
		for idx2, data2 in enumerate(titleArray):
			if data2 in data1:
				value = data1[data2]
				aForm.append(value)
			else:
				aForm.append("-")
		allForms.append(aForm)

	with open(sheet+".csv", "wb") as csv_file:
		writer = csv.writer(csv_file, delimiter=',')
		for line in allForms:
			writer.writerow(line)
