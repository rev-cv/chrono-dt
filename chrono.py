from Chrono.ch_transformator import chrono_transformator
from Chrono.ch_catcher import chrono_catcher
from Chrono.ch_pitcher import chrono_pitcher
from Chrono.ch_analyzer import chrono_analyzer
from String.string_deconstruction import Deconstruction
from String.string_construction import Formatter

class chrono(
		chrono_catcher,
		chrono_analyzer,
		chrono_pitcher,
		chrono_transformator,
		Deconstruction,
		Formatter,
	):
	"""docstring for chrono"""
	def __init__(self, 
			y=None, 
			m=None, 
			d=None, 
			H=None, 
			M=None, 
			S=None, 
			shift=None,
			tz="local", 
			auto=True
		):

		super(chrono, self).__init__()

		self.chrono = chrono
		self.y = None
		self.m = None
		self.d = None
		self.H = None
		self.M = None
		self.S = None
		self.tz = None

		self.setTimeZone(tz)
		# в начале задается временная зода, 
		# чтобы не перезаписать временную зону
		# которая может прийти в аргументах
		self.set(y, m, d, H, M, S)

	def __str__(self):
		return self.format("CHRONO %YMD0 %HMS0 %Z")

if __name__ == '__main__':
	# a = chrono("NOW")
	# print(a)
	# b = chrono(a)
	# print(b)
	
	from PyQt5.QtCore import QDateTime

	# time = QDateTime(2022, 11, 20, 11, 34, 34)
	# tz = time.timeZone()

	# for x in QTimeZone().availableTimeZoneIds():
	# 	x = x.__str__()
	# 	print(type(x), x[2:-1], len(x))

	a = chrono()

	print(a.getISO())




