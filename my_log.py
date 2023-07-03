def log(*body):
	return


def err(*body):
	print("!ERROR!")
	print(body)


def t_to_n(num):
	chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJELMNOPQRSTUVWXYZ"
	base = len(chars)
	string = ""
	while True:
		string = chars[num % base] + string
		num = num // base
		if num == 0:
			break
	return string


def n_to_t(string):
	chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJELMNOPQRSTUVWXYZ"
	base = len(chars)
	num = 0
	for char in string:
		num = num * base + chars.index(char)
	return num
