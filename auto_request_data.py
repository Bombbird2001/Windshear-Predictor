import requests
import sys
import json
from bs4 import BeautifulSoup
from pathlib import Path
import time

newText = []
index = -1
index1 = 0

arpt = input("Enter airport ICAO code: ")
year_start = year_end = int(input("Enter end year: "))
month_start = month_end = int(input("Enter end month: "))
day_start = day_end = int(input("Enter end day: "))
day_start += 1
hour_start = hour_end = int(input("Enter end hour: "))
months = int(input("Enter time in months: "))
assert months >= 1, "At least 1 month of data must be requested"
for i in range(months):
	month_start -= 1
	if month_start <= 0:
		month_start += 12
		year_start -= 1
	
	assert year_start < year_end or month_start < month_end or day_start < day_end or hour_start <= hour_end, "Start date must be earlier than end date"

	url = 'http://www.ogimet.com/display_metars2.php?lang=en&lugar=' + arpt + '&tipo=SA&ord=REV&nil=NO&fmt=txt&ano=' + str(year_start) + '&mes=' + str(month_start) + '&day=' + str(day_start) + '&hora=' + str(hour_start) + '&anof=' + str(year_end) + '&mesf=' + str(month_end) + '&dayf=' + str(day_end) + '&horaf=' + str(hour_end) + '&minf=59&send=send'
	
	month_end -= 1
	if month_end <= 0:
		month_end += 12
		year_end -= 1
	
	r = requests.get(url)
	data = r.text
	soup = BeautifulSoup(data, "html.parser")

	# kill all script and style elements
	for script in soup(["script", "style"]):
		script.extract()    # rip it out

	# get text
	text = soup.get_text()

	# break into lines and remove leading and trailing space on each
	lines = (line.strip() for line in text.splitlines())
	# break multi-headlines into a line each
	chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
	# drop blank lines
	text = '\n'.join(chunk for chunk in chunks if chunk)

	for line in text.split("\n"):
		try:
			if index1 <= 15 or line[0] == '#':
				index1 += 1
				continue
			if len(line.split(" ")[0]) < 12:
				newText[index] = newText[index] + " " + line
			else:
				newText.append(line)
				index += 1
			index1 += 1
		except e:
			print(line)
			print(e)
	
	print(i + 1, "of", months, "months retrieved")
	#Don't overload the server
	if (i + 1) % 3 == 0 and i + 1 < months:
		print("Pausing for 1 minute to prevent overloading...")
		time.sleep(60)
	else:
		time.sleep(5)

Path(arpt).mkdir(parents=True, exist_ok=True)
f = open(arpt + "/" + arpt + ".txt", "w+")
f.write('\n'.join(newText))
f.close()

print(months, "month(s) of data for", arpt, "retrieved successfully")