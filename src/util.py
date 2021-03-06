import os
import random
import numpy as np
import pandas as pd
import tifffile as tiff
from shapely import wkt
from shapely.geometry import MultiPolygon, Polygon

'''
Global constants
'''
data_directory = '/media/sf_school/project/data/'
num_class = 10
wkt_shapes_fn = os.path.join(data_directory, 'train_wkt_v4.csv')

'''
Preprocessing
'''
def load_image(image_id, image_type=None, bands='all'):
    '''
    Load an image as a numpy ndarray
    image_type:
        -P
        -M
        -A
        -None = load the three-band RGB image
    bands:
        -all = load all bands for that type
        -list of bands to load, zero-indexed (i.e. [1, 3, 4])
    '''
    if image_type == None:
        image_folder = 'three_band'
        image_name = '{}.tif'.format(image_id)
    elif image_type in ['P', 'M', 'A']:
        image_folder = 'sixteen_band/'
        image_name = '{}_{}.tif'.format(image_id, image_type)
    else:
        raise InputError('incorrect image type: {}'.format(image_type))
    filename = os.path.join(data_directory, image_folder, image_name)
    image = tiff.imread(filename)
    # put image in shape (H x W x bands)
    image = np.rollaxis(image, 0, 3)
    if bands != 'all':
        bands = np.array(bands)
        image = image[..., bands]
    return image

def normalize_image(image):
    '''
    Normalize the image
    '''
    # TODO: what type of normalization should we do for the models we plan to build?
    # color? contrast? mean-normalized? values in what range?
    pass

def load_wkt_shape(image_id, classes):
    '''
    Load WKT shape as a list of Shapely geometric object
    classes:
        -all = load all classes
        -list of the classes to load, zero-indexed (i.e. [0, 3, 5])
    '''
    shapes = []
    shapes_df = pd.read_csv(wkt_shapes_fn,
            names=['ImageId', 'ClassType', 'MultipolygonWKT'], skiprows=1)
    image_shapes = shapes_df[shapes_df.ImageId == image_id]
    if classes == 'all':
        classes = list(range(num_class))
    for cls in classes:
        if cls not in range(num_class):
            raise InputError('Class {} is not one of {} valid classes.'.format(cls, num_class))
        wkt_shape = image_shapes[image_shapes.ClassType == cls].MultipolygonWKT
        shapes.append(wkt.loads(wkt_shape))
    pass

def create_mask(image_id, classes):
    '''
    Load the masks for an image
    classes:
        -all = load all classes
        -list of the classes to load, zero-indexed (i.e. [0, 3, 5])
    '''
    pass

'''
Scoring functions
'''
def my_jaccard(true, pred):
    '''
    Calculate the union over intersection of the true and predicted mask
    true, pred = binary masks of the same size representing the actual and predicted mask
    '''
    true = true.flatten()
    pred = np.rint(pred.flatten())
    intersection = np.sum(true * pred)
    union = true + pred
    union[union > 1] = 1
    union = np.sum(union)
    return intersection/union

