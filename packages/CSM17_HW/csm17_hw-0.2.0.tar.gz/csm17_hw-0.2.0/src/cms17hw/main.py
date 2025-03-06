import sys

from cms17hw.utils import extractXml, parseXml, hwpx2latex

def extract():
	print("HWPX 파일의 경로를 입력해주세요. (ex. /Users/Desktop/tmp.hwpx)")
	path = sys.stdin.readline().strip()
	extractXml(path)

def parse():
	print("XML 파일의 경로를 입력해주세요. (ex. /Users/Desktop/tmp.xml)")
	path = sys.stdin.readline().strip()
	parseXml(path)

def runHwpx2latex():
	print("HWPX 수식을 입력해주세요")
	value = sys.stdin.readline().strip()
	print("*** 변환결과 ***\n", hwpx2latex(value), end="\n****************\n")
