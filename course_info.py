import mechanicalsoup as ms
from bs4 import BeautifulSoup as bs
import time
import json

# Course Info
course_jsons = {}
output_file = open('course_info.json', 'w')

# Generate current unix time in milisecond for request.
millis = int(round(time.time() * 1000))
print(millis)

# Pull information from CUSP.
br = ms.StatefulBrowser()
response = br.open("https://cusp.sydney.edu.au/students/view-units-page/did//get_table/1/?sEcho=2&iColumns=2&sColumns=&iDisplayStart=0&iDisplayLength=-1&sSearch=&bRegex=false&sSearch_0=&bRegex_0=false&bSearchable_0=true&sSearch_1=&bRegex_1=false&bSearchable_1=true&_=" + str(millis))
data = json.loads(response.text)

# Extract Course information.
for item in data['aaData']:
    course_code = bs(item[0], features="lxml").find('a').text.strip()
    course_name = bs(item[1], features="lxml").find('a').text.strip()
    course_jsons.update({course_code:course_name})

# Save to json file.
output_file.write(json.dumps(course_jsons))
output_file.close()


# This is just testing.
'''
temp = open('course_info.json', 'r')
data = json.loads(temp.read())

for k, v in data.items():
    print(k + " " + v)
'''
