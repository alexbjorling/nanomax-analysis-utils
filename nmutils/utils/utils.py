""" This file contains isolated helper functions. """

import numpy as np
import pyfftw
import scipy.signal
import math

def shift(a, shifts):
    """ Shifts an array periodically. """
    a_ = np.copy(a)
    shifts = map(int, shifts)
    # shift the first index: turns out to work with negative shifts too
    if shifts[0]:
        a_[shifts[0]:, :] = a[:-shifts[0], :]
        a_[:shifts[0], :] = a[-shifts[0]:, :]
        a = np.copy(a_)
    # shift the second index: same here
    if shifts[1]:
        a_[:, shifts[1]:] = a[:, :-shifts[1]]
        a_[:, :shifts[1]] = a[:, -shifts[1]:]
    return a_

def gaussian2D(n, sigma):
    """ Returns an n-by-n matrix containing a circular 2d gaussian with variance sigma**2 in pixels. """
    mat = np.zeros((n, n))
    mu = (n - 1) / 2.0
    twoSigma2 = float(2 * sigma**2)
    prefactor = 1 / (twoSigma2 * np.pi)
    for i in range(n):
        for j in range(n):
            mat[i, j] = prefactor * np.exp(- ((i - mu)**2 + (j - mu)**2) / twoSigma2 )
            # the convolution darkens the image, not sure why, but this happens both with the scipy methods and
            # with a slow manual doulbe loop convolution... this number was obtained from a numerical test.
            mat[i, j] *= 100.0 / 77.9484
    return mat
    
def circle(n, radius=None, dtype='float'):
    """ Returns an n-by-n array of zeros with a filled circle of ones in its center, with default radius n/2. """
    result = np.zeros((n,n), dtype=dtype)
    if not radius:
        radius = n / 2.0
    I, J = result.shape
    for i in range(I):
        for j in range(J):
            result[i, j] = int((i-(I-1)/2.0)**2 + (j-(J-1)/2.0)**2 < radius**2)
    return result
    
def pseudoCircle(n, radius=None, exponent=1.5, dtype='float'):
    """ Returns an n-by-n array of zeros with a filled circle of ones in its center, with default radius n/2. """
    result = np.zeros((n,n), dtype=dtype)
    if not radius:
        radius = n / 2.0
    I, J = result.shape
    for i in range(I):
        for j in range(J):
            result[i, j] = int(  np.abs(i-(I-1)/2.0)**exponent + np.abs((j-(J-1)/2.0))**exponent < radius**exponent ) 
    return result
    
def poisson(mean, k):
    """ Returns the normalized Poisson probability for observing k counts in a distribution described by the mean. """
    if type(k) in [list, tuple, np.ndarray]:
        result = []
        for k_ in k:
            result.append(mean**k_ * np.exp(-mean) / math.factorial(k_))
        return np.array(result)
    else:
        return mean**k * np.exp(-mean) / math.factorial(k)
    
def smoothImage(image, sigma):
    """ Returns a smoothened copy of the input image, which is convolved by a gaussian of standard deviation sigma. """
    gaussian = gaussian2D(3*sigma, sigma)
    # fftconvolve() is faster than convolve2d (tested)
    # a copy of the image is created (also tested)
    smoothImage = scipy.signal.fftconvolve(image, gaussian, mode='same')
    return smoothImage
    
def noisyImage(image, photons):
    """ Returns a noisy copy of the input image, with simulated photon-counting noise (Poisson noise) corresponding to an overall average number of photons per pixel. """
    result = np.zeros(image.shape)
    averagePhotonsPerPixelValue = np.prod(image.shape) * photons / float(np.sum(image))
    hist = []
    for i in range(result.shape[0]):
        for j in range(result.shape[1]):
            hist.append(image[i, j] * averagePhotonsPerPixelValue)
            result[i, j] = np.random.poisson(image[i, j] * averagePhotonsPerPixelValue) / averagePhotonsPerPixelValue
    return result

# at this point, with a 300x300 image, FFTW is about twice as fast as numpy. Threading doesn't help at this point. 
# FFTW can be improved using the pyfftw.FFTW class or the pyfftw.builders functions.
def fft(a):
    #a = np.fft.fftn(a)
    a = pyfftw.interfaces.numpy_fft.fftn(a, threads=1)
    a = np.fft.fftshift(a)
    return a
    
def ifft(a):
    a = np.fft.ifftshift(a)
    a = pyfftw.interfaces.numpy_fft.ifftn(a, threads=1)
    #a = np.fft.ifftn(a)
    return a
    
def biggestBlob(image):
    """ Takes an image and returns a version with only the biggest continuous blob of non-zero elements left. """
    labeledImage, N = scipy.ndimage.label(image)
    # first, work out which is the biggest blob (except the background)
    areas = []
    for i in range(1, N + 1): # N doesn't include the background
        areas.append(sum(sum(labeledImage == i)))
    biggest = np.where(areas == max(areas))[0] + 1
    return (labeledImage == biggest)
    
def embedMatrix(block, wall, position, mode='center'):
    """ Embeds a small matrix into a bigger one. If a length-2 tuple is given instead of a big matrix, a zero matrix of that size is used. """
    if type(wall) == tuple:
        wall = np.zeros(wall, dtype=block.dtype)
    try: 
        if mode == 'corner':
            wall[position[0] : position[0] + block.shape[0], position[1] : position[1] + block.shape[1]] = block
        if mode == 'center':
            wall[position[0]-block.shape[0]/2 : position[0]-block.shape[0]/2 + block.shape[0], position[1]-block.shape[1]/2 : position[1]-block.shape[1]/2 + block.shape[1]] = block
    except ValueError:
        raise ValueError('Trying to put embedded matrix outside the boundaries of the embedding matrix.')
    return wall
    
def shiftAndMultiply(block, wall, position, mode='center'):
    """ Does the same as embedMatrix() but returns the product of the two, with dimensions of the small matrix. """
    try: 
        if mode == 'corner':
            return block * wall[position[0] : position[0] + block.shape[0], position[1] : position[1] + block.shape[1]]
        if mode == 'center':
            return block * wall[position[0]-block.shape[0]/2 : position[0]-block.shape[0]/2 + block.shape[0], position[1]-block.shape[1]/2 : position[1]-block.shape[1]/2 + block.shape[1]]
    except ValueError:
        print block.shape, wall.shape, position
        raise ValueError('Shifting out of bounds.')
        
def binPixels(image, n=2):
    """ Downsamples an image by an integer amount, by binning adjacent pixels n-by-n. Odd pixels on the bottom and right are discarded. """
    size = np.array(image.shape)
    size[0] = size[0] // n
    size[1] = size[1] // n
    new = np.zeros(size, dtype=image.dtype)
    for i in range(size[0]):
        for j in range(size[1]):
            new[i, j] = np.round(np.mean(image[i * n : (i + 1) * n, j * n : (j + 1) * n], axis=(0, 1)))
    return new

def propagateNearfield(A, psize, distances, energy):     

    """           

    Propagates the complex wavefront in N-by-N ndarray to the plane(s)
    specified as distances. The physical spacing of array elements is 
    psize, and the beam energy is specified in keV. An array 
    length(distances) x N x N is returned.

    The underlying code is ptypy's Geo class, which is essentially
    wrapped here.
    """     

    import ptypy

    # check for square matrix
    try:
        assert len(A.shape) == 2
        assert A.shape[0] == A.shape[1]
    except AssertionError:
        raise RuntimeError("Wavefront array must be N x N")

    # passing a single distance is allowed too
    try:
        len(distances)
    except TypeError:
        distances = [distances]

    # parameters for the propagator
    geo_pars = ptypy.core.geometry.DEFAULT.copy(depth=10)
    geo_pars.energy = energy
    geo_pars.distance = distances[0]
    geo_pars.resolution = psize
    geo_pars.psize = psize
    geo_pars.shape = A.shape[0]
    geo_pars.propagation = 'nearfield'

    # create the propagator
    geo = ptypy.core.geometry.Geo(pars=geo_pars)

    # prepare a 3D matrix for propagated wavefronts
    N = len(distances)
    result = np.zeros((N,) + A.shape, dtype=A.dtype)

    # iterate over the distances and propagate to there
    for i in range(N):
        geo.p.distance = distances[i]
        geo.update()
        result[i, :, :] = geo.propagator.fw(A)

    return result
    
# constants
from matplotlib.colors import LinearSegmentedColormap
alpha2red = LinearSegmentedColormap('alpha2red', 
                                    {
          'red':   ((0.0, 0.0, 0.0),
                   (1.0, 1.0, 1.0)) ,
         'green': ((0.0, 0.0, 0.0),
                   (1.0, 0.0, 0.0)),
         'blue': ((0.0, 0.0, 0.0),
                   (1.0, 0.0, 0.0)),
         'alpha': ((0.0, 0.0, 0.0),
                   (1.0, 1.0, 1.0)) 
                   })
                   
alpha2redTransparent = LinearSegmentedColormap('alpha2red', 
                                    {
          'red':   ((0.0, 0.0, 0.0),
                   (1.0, 1.0, 1.0)) ,
         'green': ((0.0, 0.0, 0.0),
                   (1.0, 0.0, 0.0)),
         'blue': ((0.0, 0.0, 0.0),
                   (1.0, 0.0, 0.0)),
         'alpha': ((0.0, 0.0, 0.0),
                   (1.0, 0.5, 0.5)) 
                   })

alpha2black = LinearSegmentedColormap('alpha2black', 
                                    {
          'red':   ((0.0, 0.0, 0.0),
                   (1.0, 0.0, 1.0)) ,
         'green': ((0.0, 0.0, 0.0),
                   (1.0, 0.0, 0.0)),
         'blue': ((0.0, 0.0, 0.0),
                   (1.0, 0.0, 0.0)),
         'alpha': ((0.0, 0.0, 0.0),
                   (1.0, 1.0, 1.0))
                   })