import sys

from cms17hw.utils import extractXml, parseXml

def extract():
	print("HWPX 파일의 경로를 입력해주세요. (ex. /Users/Desktop/tmp.hwxp)")
	path = sys.stdin.readline().strip()
	extractXml(path)

def parse():
	print("XML 파일의 경로를 입력해주세요. (ex. /Users/Desktop/tmp.xml)")
	path = sys.stdin.readline().strip()
	parseXml(path)