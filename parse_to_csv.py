import sys
import re
import random


def matchWindSpd(metar):
	spd = re.search(r"(VRB|\d{3})(\d{2})G?(\d{2})?KT ", metar)
	if spd is None:
		return (None, None)
	return (spd.group(2), spd.group(3))


def matchWindVrb(metar):
	vrb = re.search(r" (\d{3})V(\d{3}) ", metar)
	if vrb is None:
		return "0"
	vrb1 = int(vrb.group(1))
	vrb2 = int(vrb.group(2))
	result = vrb2 - vrb1
	if result < 0:
		result += 360
	return str(result)


def matchVisibility(metar):
	result = re.search(r" (\d{4}) ", metar)
	if result is None:
		return "9999" if re.search(r" (CAVOK) ", metar).group(1) else None
	return result.group(1)


def matchQnh(metar):
	return re.search(r" Q(\d{4}) ", metar).group(1)


def matchWs(metar):
	return "0" if re.search(r" WS ", metar) is None else "1"


def matchRain(metar):
	result = re.search(r" (-|\+)*[A-Z]*(RA) ", metar)
	if result is None:
		return ("0", "0")
	grp1 = result.group(1)
	grp2 = result.group(2)
	if grp2 != "RA":
		return ("0", "0")
	if grp1 is None:
		return ("0.6", "1")
	elif grp1 == "-":
		return ("0.3", "1")
	elif grp1 == "+":
		return ("1", "1")


test_ratio = 0.3
files = sys.argv
files.pop(0)
for file in files:
	print(file)
	with open(file + "/" + file + ".txt", "r") as f:
		data = f.read().split("\n")
		with open(file + "/" + file + "_train.csv", "w+") as output:
			with open(file + "/" + file + "_test.csv", "w+") as test:
				output.write("month,windSpdKts,gustKts,windVrbDeg,intensity,rain,visibilityMtrs,qnh,ws")
				test.write("month,windSpdKts,gustKts,windVrbDeg,intensity,rain,visibilityMtrs,qnh,ws")
				for line in data:
					month = line[4:6]
					filterData = " ".join(line.split("BECMG")[0].split("TEMPO")[0].split("PROB30")[0].split("PROB40")[0].split("RMK")[0].split(" ")[4:])
					try:
						windSpd, windGust = matchWindSpd(filterData)
						if windSpd is None:
							print("Invalid wind speed:", filterData)
							continue
						if windGust is None:
							windGust = "0"
						intensity, rain = matchRain(filterData)
						text = "\n" + month + "," + windSpd + "," + windGust + "," + matchWindVrb(filterData) + "," + intensity + "," + rain + "," + matchVisibility(filterData) + "," + matchQnh(filterData) + "," + matchWs(filterData)
						test.write(text) if random.random() <= test_ratio else output.write(text)
					except Exception as e:
						print(e)
						print("Invalid METAR:", filterData)
				
