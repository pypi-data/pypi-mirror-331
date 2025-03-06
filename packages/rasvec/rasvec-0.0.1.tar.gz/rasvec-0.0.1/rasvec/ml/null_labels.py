import os
import glob
from PIL import Image
import numpy as np
import random


def seg_null_and_data(label_path):
    """_summary_

    Args:
        label_path (_type_): _description_

    Returns:
        _type_: _description_
    """

    null_label = []
    nonnull_label = []
    labels = [i for i in glob.glob(label_path + r'/labels/*.tif')]

    for path in labels:
        label = Image.open(path)
        label = np.asarray(label)

        if label.sum() == 0 :

            null_label.append(path)

        else:
            nonnull_label.append(path)

    return nonnull_label, null_label

def keep_list_ratio(null_label, ratio):
    random.shuffle(null_label)
    return null_label[:int(len(null_label)*ratio)]


def get_label_path(img_path):
    filename = os.path.basename(img_path)
    label_path = os.path.split(os.path.split(img_path)[0])[0] + rf'\label\{filename}'
    return label_path

