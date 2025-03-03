import os


def extractXml(hwpxPath):
	"""
	hwpx에서 xml을 추출하는 함수
	"""

	import zipfile
	import subprocess


	if hwpxPath.split(".")[-1] != "hwpx":
		raise Exception("hwpx 파일이 아닙니다.")

	originPath = os.path.dirname(hwpxPath)
	tmpPath = f"{os.path.dirname(os.path.abspath(__file__))}/tmp.zip"

	subprocess.run(["cp", hwpxPath, tmpPath])   # hwpx -> tmp.zip

	with zipfile.ZipFile(tmpPath, "r") as z:
		with z.open("Contents/section0.xml") as f:
			xml = f.read().decode()

	xmlPath=f"{os.path.dirname(tmpPath)}/extr.xml"
	with open(xmlPath ,"w") as f:
		f.write(xml)
		print(f"xml파일이 추출되었습니다. ::: {xmlPath}")
		subprocess.run(["rm", tmpPath])

	return xmlPath


def parseXml(xmlPath=f"{os.path.dirname(os.path.abspath(__file__))}/extr.xml",outputPath=f"{os.path.dirname(os.path.abspath(__file__))}/formula.txt"):
	"""
	XML파일을 파싱하여 수식만 추출
	"""

	if xmlPath.split(".")[-1] != "xml":
		raise Exception("xml 파일이 아닙니다.")

	#import re
	from bs4 import BeautifulSoup


	with open(xmlPath,"rb") as f:
		xml=f.read().decode()

	soup = BeautifulSoup(xml, features="xml")

	with open(outputPath, "w") as f:
		for s in soup.find_all("hp:script"):
			f.write(f"{s.text}\n")

	print(f"xml으로부터 수식이 추출되었습니다. ::: {outputPath}")