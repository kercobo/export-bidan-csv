import urllib2, base64, json
import socket
import inflection
from datetime import datetime 
import csv
import os
import time

# set timeout
# timeout in seconds
timeout = 10000
socket.setdefaulttimeout(timeout)

URL = "http://localhost:9979"
USERLOGIN = "demo1"
PASSWORDLOGIN = "1"
csvPathFolder = "csv/"
bindTypesId = {'kartu_ibu': 'kiId', 'ibu': 'motherId', 'anak': 'childId'}

resultJson = ""
formNames = {}

allUsers = ['user1', 'user2', 'user3', 'user4', 'user5', 'user6', 'user8', 'user9', 'user10', 'user11', 'user12', 'user13', 'user14']


def create_csv():

	# fetch forms
	for user in allUsers:
		apiUrl = URL + "/form-submissions?anm-id=" + user + "&timestamp=0"
		try:
			print("Fetch form submissions %s" % user)
			req = urllib2.Request(apiUrl)
			base64String = base64.encodestring('%s:%s' % (USERLOGIN, PASSWORDLOGIN)).replace('\n', '')
			req.add_header("Authorization", "Basic %s" % base64String)
			result = urllib2.urlopen(req)
			resultJson = json.load(result.fp)
			for row in resultJson:
				if not row["formName"] in formNames:
					formNames[row["formName"]] = []
				jsondata = (json.loads(row["formInstance"]))
				jsonfield = []
				jsonfield.append({'name': "userID", 'value': row["anmId"]})
				jsonfield.append({'name': bindTypesId.get(jsondata["form"]["bind_type"], "none"), 'value': row["entityId"]})
				jsonfield.extend(jsondata["form"]["fields"])
				jsonfield.append({'name': "clientVersionSubmissionDate", 'value' : datetime.fromtimestamp(int(row["clientVersion"])/1000.0).strftime('%Y-%m-%d %H:%M:%S')})
				jsonfield.append({'name': "serverVersionSubmissionDate", 'value' : datetime.fromtimestamp(int(row["serverVersion"])/1000.0).strftime('%Y-%m-%d %H:%M:%S')})
				formNames[row["formName"]].append(jsonfield)

			result.close()
		except(socket.timeout, urllib2.HTTPError) as e:
			print("Error : %s " % e)
			# sys.exit(1)

	# create csv
	for sheet in formNames:
		print("Create %s" % sheet)

		# create worksheet
		worksheetTitle = inflection.humanize(sheet[0:30])
		title_array = []
		form_data = []
		all_form = []
		
		# put the json data to array
		for idx1, data1 in enumerate(formNames[sheet]):
			form_data.append([])
			form_data[idx1] = {}
			for idx2, data2 in enumerate(data1):
				if data2['name'] != 'id':
					if not data2['name'] in title_array:
						title_array.insert(idx2, data2['name'])
					value = str(data2.get('value'))
					if value is None:
						value = '-'
					form_data[idx1][data2['name']] = value

		for idx1, data1 in enumerate(form_data):
			aForm = []
			for idx2, data2 in enumerate(title_array):
				if data2 in data1:
					value = data1[data2].replace(",", "-")
					aForm.append(value)
				else:
					aForm.append("-")
			all_form.append(aForm)

		_titleArray = list(title_array)
		for idx1, data1 in enumerate(title_array):
			index = 0
			_titleArray.remove(data1)
			if data1.upper() in (name.upper() for name in _titleArray):
				print data1
				title_array[idx1] = data1 + str(index)
				index = index+1

		all_form.insert(0, title_array)

		if not os.path.exists(csvPathFolder):
			os.makedirs(csvPathFolder)

		with open(csvPathFolder+sheet+".csv", "wb") as csv_file:
			writer = csv.writer(csv_file, delimiter=',')
			for line in all_form:
				writer.writerow(line)
		os.system("sh "+csvPathFolder+"run.sh "+csvPathFolder+sheet+".csv "+sheet+"")

def start():
    while True:
            create_csv()
            time.sleep(3600)

if __name__ == '__main__':
	start()

    

