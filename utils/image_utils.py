import numpy as np
import cv2 as cv
import random
import scipy.ndimage as nd
import math

def hflip_2d(img, random_mode=True, probability=0.5):
	if random_mode:
		if random.random() < probability:
			return img

	return cv.flip(img, 0)

def vflip_2d(img, random_mode=True, probability=0.5):
	if random_mode:
		if random.random() < probability:
			return img

	return cv.flip(img, 1)

def rotate_2d(img, angle_in_degrees,random_mode=True, probability=0.5):
	if random_mode:
		if random.random() < probability:
			return img

	rot_mat = cv.getRotationMatrix2D(tuple(np.array(img.shape)/2), angle, 1.0)
	return apply_affine(img, rot_mat)

def translate_2d(img, dxdy, random_mode=True, probability=0.5):
	if random_mode:
		if random.random() < probability:
			return img

	dx, dy = dxdy
	shift_mat = np.array([[1, 0, dx], [0, 1, dy]])
	return apply_affine(img, shift_mat)

def shear_2d(img, dxdy, random_mode=True, probability=0.5):
	if random_mode:
		if random.random() < probability:
			return img

	dx, dy = dxdy
	shear_mat = np.array([[1, dx, 0], [dy, 1, 0]])
	return apply_affine(img, shear_mat)

def elastic_transform_2d(img, alpha, sigma, random_mode=True, probability=0.5):
	#Taken from: https://gist.github.com/chsasank/4d8f68caf01f041a6453e67fb30f8f5a
	if random_mode:
		if random.random() < probability:
			return img

	dx = nd.gaussian_filter((random_state.rand(img.shape) * 2 - 1), sigma, mode="constant", cval=0) * alpha
	dy = nd.gaussian_filter((random_state.rand(img.shape) * 2 - 1), sigma, mode="constant", cval=0) * alpha

	x, y = np.meshgrid(np.arange(img.shape[0]), np.arange(img.shape[1]), indexing='ij')
	indices = np.reshape(x+dx, (-1, 1)), np.reshape(y+dy, (-1, 1))

	return nd.map_coordinates(img, indices, order=1).reshape(img.shape)

def resize_2d(img, new_size):
	return cv.resize(img, new_size)

def resize_3d(img, new_size):
	if new_size[0] == -1:
		#Resize 2D wise!
		if new_size[1] != img[0].shape[0] and new_size[2] != img[0].shape[1]:
			return np.array([cv.resize(img[idx], (new_size[1], new_size[2])) \
				for idx in range(img.shape[0])])
		else:
			return img
	else:
		resize_factor = [a/float(b) for a,b in zip(new_size, img.shape)]
		if resize_factor == (1.0, 1.0, 1.0):
			return img
			
		return nd.interpolation.zoom(img, resize_factor, mode='nearest')

def apply_affine(img, mat):
	return cv.warpAffine(img, mat, img.shape, flags=cv.INTER_LINEAR)

def img_affine_aug_pipeline_2d(img, op_str='rts', rotate_angle_range=5, translate_range=3, shear_range=3, random_mode=True, probability=0.5):
	if random_mode:
		if random.random() < 0.5:
			return img

	mat = np.identity(3)
	for op in op_str:
		if op == 'r':
			rad = math.radian(((random.random() * 2) - 1) * rotate_angle_range)
			cos = math.cos(rad)
			sin = math.sin(rad)
			rot_mat = np.identity(3)
			rot_mat[0][0] = cos
			rot_mat[0][1] = sin
			rot_mat[1][0] = -sin
			rot_mat[1][1] = cos
			mat = np.dot(mat, rot_mat)
		elif op == 't':
			dx = ((random.random() * 2) - 1) * translate_range
			dy = ((random.random() * 2) - 1) * translate_range
			shift_mat = np.identity(3)
			shift_mat[0][2] = dx
			shift_mat[1][2] = dy
			mat = np.dot(mat, shift_mat)
		elif op == 's':
			dx = ((random.random() * 2) - 1) * shear_range
			dy = ((random.random() * 2) - 1) * shear_range
			shear_mat = np.identity(3)
			shear_mat[0][1] = dx
			shear_mat[1][0] = dy
			mat = np.dot(mat, shear_mat)
		else:
			continue

	affine_mat = np.array([mat[0], mat[1]])
	return apply_affine(img, affine_mat), affine_mat