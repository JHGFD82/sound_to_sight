for i in range(18):
	s = n/x*i/30
	print(str(math.floor(s)) + ':' + str(f"{math.floor(s%1*30):02d}"))