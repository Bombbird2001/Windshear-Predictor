import sys
import re
import random


def matchWindSpd(metar):
	spd = re.search(r"(VRB|\d{3})(\d{2})G?(\d{2})?KT ", metar)
	if spd is None:
		return (None, None, None)
	return (spd.group(1), spd.group(2), spd.group(3))


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


def matchCeiling(metar):
	result = re.search(r" (VV\d{3})| (BKN\d{3})| (OVC\d{3})", metar)
	if result is None:
		return "99999"
	else:
		cloudToUse = ""
		if result.group(1) is not None:
			cloudToUse = result.group(1)
		elif result.group(2) is not None:
			cloudToUse = result.group(2)
		elif result.group(3) is not None:
			cloudToUse = result.group(3)
		return str(int(cloudToUse[-3:]) * 100)


def matchVisibility(metar):
	result = re.search(r" (\d{4}) ", metar)
	if result is None:
		cavok_res = re.search(r" (CAVOK) ", metar)
		if cavok_res is not None and cavok_res.group(1):
			return "9999"
		na_vis = re.search(r" (\d*?)/?(\d{1,2})SM ", metar)
		if na_vis.group(1):
			return str(round(int(na_vis.group(1)) / int(na_vis.group(2)) * 1600))
		if na_vis.group(2):
			return str(round(int(na_vis.group(2)) * 1600))
		return None
	return result.group(1)


def matchQnh(metar):
	qnh_match = re.search(r" Q(\d{4})[= ]?", metar)
	if qnh_match is not None:
		return qnh_match.group(1)
	inhg_to_hpa = 0.3386389
	inhg_match = re.search(r" A(\d{4})[= ]?", metar)
	return str(round(int(inhg_match.group(1)) * inhg_to_hpa))

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

parseAll = True
test_ratio = 0.3
files = sys.argv
files.pop(0)
for file in files:
	print(file)
	with open(file + "/" + file + ".txt", "r") as f:
		data = f.read().split("\n")
		downSampling = 1
		with open(file + "/downsample.txt", "r") as ds:
			downSampling = float(ds.read())
		with open(file + "/" + file + "_train.csv", "w+") as output:
			with open(file + "/" + file + "_test.csv", "w+") as test:
				output.write("month,windDir,windSpdKts,gustKts,windVrbDeg,intensity,rain,ceilingFt,visibilityMtrs,qnh,ws")
				test.write("month,windSpdKts,gustKts,windVrbDeg,intensity,rain,visibilityMtrs,qnh,ws")
				for line in data:
					month = line[4:6]
					filterData = " ".join(line.split("BECMG")[0].split("TEMPO")[0].split("PROB30")[0].split("PROB40")[0].split("RMK")[0].split(" ")[4:])
					try:
						windDir, windSpd, windGust = matchWindSpd(filterData)
						if windSpd is None:
							print("Invalid wind speed:", filterData)
							continue
						if windGust is None:
							windGust = "0"
						intensity, rain = matchRain(filterData)
						ws = matchWs(filterData)
						text = "\n" + month + "," + windDir + "," + windSpd + "," + windGust + "," + matchWindVrb(filterData) + "," + intensity + "," + rain + "," + matchCeiling(filterData) + "," + matchVisibility(filterData) + "," + matchQnh(filterData) + "," + ws
						if random.random() <= test_ratio and not parseAll:
							test.write(text)
						else:
							if ws == "0" and random.random() > 1 / downSampling and not parseAll:
								continue
							output.write(text)
					except Exception as e:
						print(e)
						print("Invalid METAR:", filterData)
				
