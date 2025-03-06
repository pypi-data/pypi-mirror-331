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

	return outputPath




def hwpx2latex(value):
	import sys
	"""
	HWPX의 수식을 LaTex문법으로 변환
	"""

	"""
	rm P LEFT ( it A SMALLINTER B ^{C}  RIGHT ) = rm P LEFT ( it A RIGHT ) rm P LEFT ( it B ^{C}  RIGHT ) = rm P LEFT ( it A RIGHT ) TIMES  {3} over {8} = {1} over {8}
	\mathrm { P } \left ( A \cap B ^ { C } \right ) = \mathrm { P } \left ( A \right ) \mathrm { P } \left ( B ^ { C } \right ) = \mathrm { P } \left ( A \right ) \times \dfrac{ 3 } { 8 } = \dfrac{ 1 } { 8 }
	"""

	def equal(string):
		tmp = string.split("=")
		tmp = list(map(lambda x:hwpx2latex(x), tmp))

		return "=".join(tmp)

	def brankets(string):
		i=0
		tmp=[]

		for s in string:

			if s=="{":
				v, idx = brankets(string[i+1:])
				tmp.append(v)
				i+=idx
			elif s=="}":
				return hwpx2latex(" ".join(tmp)),i
			else:
				tmp.append(s)
			i+=1


	preset = {
        "rm" : r"\mathrm",
        "LEFT" : r"\left",
        "it" : "",
        "SMALLINTER" : r"\cap",
        "RIGHT" : r"\right",
        "TIMES" : r"\times"
    }


	value = equal(value) if "=" in value else value
	value=value.replace("{{","{ {")
	value=value.replace("}}","} }")

	rst=[]
	#tmp=[]
	svalue=value.split(" ")

	for i in range(len(svalue)):
		if svalue[i] in preset:
			rst.append(preset[svalue[i]])
		#elif svalue[i] == "{":
		#	tmp.append(svalue(i))
		#elif svalue[i] == "}":
		#	rst.append(hwpx2latex("".join(tmp)))
		#	tmp=[]
		elif svalue[i].lower() == "over":

			tmp=rst.pop()
			rst.append(r"\dfrac")
			rst.append(tmp)
		elif svalue[i] == "{":

			v,idx=brankets(svalue[i:])
			rst.append(v)
			i+=idx
		#	tmp, j=0, i-1
		#	a, b = "",""

		#	while True:
		#		if svalue[j]=="}":
		#			tmp+=1
		#		elif svalue[j]=="{":
		#			tmp-=1
		#		a=a+svalue[j]
		#		j-=1


		#		if tmp==0:
		#			break
		#	j=i+1
		#	while True:
		#		if svalue[j]=="{":
		#			tmp+=1
		#		elif svalue[j]=="}":
		#			tmp-=1
		#		b+=svalue[j]
		#		j+=1


		#		if tmp==0:
		#			i=j

		#			break
		#	rst.append(f"\dfrac {a} {b}")

		else:
			rst.append(svalue[i])

	return " ".join(rst)