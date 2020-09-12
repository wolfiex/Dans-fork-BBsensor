import os 

lat,lon = [float(i) for i in  os.popen('curl ipinfo.io/loc').read().split(',')]


if __name__ == '__main__':
	print(lat,lon)
