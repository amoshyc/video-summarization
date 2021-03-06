import json
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm

import tensorflow as tf
from keras.backend.tensorflow_backend import set_session
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
set_session(tf.Session(config=config))

from keras.models import Sequential, Model
from keras.preprocessing import image
from keras.layers import *
from keras.layers.normalization import BatchNormalization
from keras.optimizers import *
from keras.callbacks import Callback, ModelCheckpoint, CSVLogger


def get_model():
    model = Sequential()
    model.add(Conv2D(4, kernel_size=5, strides=3, activation='relu', input_shape=(224, 224, 3)))
    model.add(Conv2D(8, kernel_size=5, strides=2, activation='relu'))
    model.add(Conv2D(12, kernel_size=3, strides=1, activation='relu'))
    model.add(MaxPooling2D(pool_size=3))
    model.add(Flatten())
    model.add(Dense(30))
    model.add(Dropout(0.3))
    model.add(Dense(1, activation='sigmoid'))
    return model

def main():
    with tf.device('/gpu:3'):
        model = get_model()

    model.compile(loss='binary_crossentropy', optimizer='sgd', metrics=['binary_accuracy'])
    model.summary()

    x_train = np.load('x_train_std.npy')
    y_train = np.load('y_train.npy')
    x_val = np.load('x_val_std.npy')
    y_val = np.load('y_val.npy')

    arg = {
        'x': x_train,
        'y': y_train,
        'batch_size': 40,
        'epochs': 30,
        'validation_data': (x_val, y_val),
        'shuffle': True,
        'callbacks': [
            CSVLogger('cnn.log'),
            ModelCheckpoint(filepath="./cnn_epoch{epoch:02d}_{val_binary_accuracy:.3f}.h5")
        ]
    } # yapf: disable

    model.fit(**arg)


if __name__ == '__main__':
    main()