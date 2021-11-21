import math
import string
import numpy as np
from PIL import Image, ImageOps, ImageFont, ImageDraw

def char_to_pixels(text, path, fontsize):
	font = ImageFont.truetype(path, fontsize)

	image = Image.new('L', font.getsize(text), 1)
	ImageDraw.Draw(image).text((0, 0), text, font = font)

	arr = np.where(np.asarray(image), 0, 1)
	arr = (arr[(arr != 0).any(axis = 1)])[:, (arr != 0).any(axis = 0)]

	return arr

def gen_pixels(chars, path = 'fonts/CourierPrime-Bold.ttf', fontsize = 40, border = 0):
	num_chars = len(chars)
	pixels = [np.array([], dtype = np.ubyte)] * num_chars
	intensity = [0] * num_chars

	n = 0
	m = 0

	for i in range(num_chars):
		pixels[i] = char_to_pixels(chars[i], path = path, fontsize = fontsize)
		n = max(n, pixels[i].shape[0])
		m = max(m, pixels[i].shape[1])

	n += 2 * border
	m += 2 * border

	for i in range(num_chars):
		x, y = pixels[i].shape
		tmp = np.zeros((n, m), dtype = np.ubyte)
		tmp[(n-x)//2:(n+x)//2, (m-y)//2:(m+y)//2] = pixels[i]
		pixels[i] = tmp
		intensity[i] = np.sum(pixels[i])

	return pixels, intensity, n, m;

def match(pixels, image, scale):
	num_chars = len(pixels)
	n, m, _ = image.shape

	r = np.average(image[:, :, 0])
	g = np.average(image[:, :, 1])
	b = np.average(image[:, :, 2])

	R = np.copy(pixels)
	R[R != 0] = int(min(r * scale + 1, 255))
	R[R == 0] = 255
	G = np.copy(pixels)
	G[G != 0] = int(min(g * scale + 1, 255))
	G[G == 0] = 255
	B = np.copy(pixels)
	B[B != 0] = int(min(b * scale + 1, 255))
	B[B == 0] = 255

	return np.moveaxis(np.array([R, G, B]), 0, -1)

def main(filename, fontsize = 50, words = 'HAPPYBIRTHDAYALISON', signature = '--TIM--', scale = 1, border = 1):
	# num_chars = 95
	# chars = list(string.printable[:num_chars])

	w_len = len(words)
	s_len = len(signature)

	chars = list(set(list(words+signature)))
	num_chars = len(chars)
	pixels, intensity, n, m = gen_pixels(chars, fontsize = fontsize, border = border)
	indices = [chars.index(c) for c in (words+signature)]

	# for i in range(num_chars - 1):
	# 	for j in range(i+1, num_chars):
	# 		if intensity[i] < intensity[j]:
	# 			chars[i], chars[j] = chars[j], chars[i]
	# 			pixels[i], pixels[j] = pixels[j], pixels[i]
	# 			intensity[i], intensity[j] = intensity[j], intensity[i]

	image1 = np.asarray(Image.open(filename))
	nn, mm, _ = image1.shape
	N, M = math.ceil(nn/n)*n, math.ceil(mm/m)*m
	image2 = np.zeros((N, M, 3), dtype = np.ubyte)
	image2[(N-nn)//2:(N+nn)//2, (M-mm)//2:(M+mm)//2, :] = image1
	image1 = image2
	image2 = np.zeros((N, M, 3), dtype = np.ubyte)

	idx = 0
	for i in range(N//n):
		print(i, N//n)
		for j in range(M//m):
			x = i * n
			y = j * m

			if i == N//n - 1 and j >= M//m - s_len:
				image2[x:x+n, y:y+m, :] = match(pixels[indices[j - M//m + s_len + w_len]], image1[x:x+n, y:y+m, :], 0.5 if (i < 2 or i > N//n - 3 or j < 2 or j > M//m - 3) else (1000 if (i < 4 or i > N//n - 5 or j < 4 or j > M//m - 5) else scale))
			else:
				image2[x:x+n, y:y+m, :] = match(pixels[indices[idx]], image1[x:x+n, y:y+m, :], 0.5 if (i < 2 or i > N//n - 3 or j < 2 or j > M//m - 3) else (1000 if (i < 4 or i > N//n - 5 or j < 4 or j > M//m - 5) else scale))
				idx += 1
				idx %= w_len

	Image.fromarray(image2).show()

main("images/Ali.jpg", 125, scale = 1.6)
# main("images/Marcus.jpg", 30, words = 'HAPPYBIRTHDAYMARCUS')
# main("images/Anakin.jpg", 100, words = 'HAPPYBIRTHDAYANAKIN', scale = 1.2, border = 0)