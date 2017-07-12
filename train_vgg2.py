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
from keras.callbacks import Callback, ModelCheckpoint
from keras.applications.vgg16 import VGG16


class MyLogger(Callback):
    def __init__(self, prefix=None):
        self.train_loss = []
        self.train_acc = []
        self.loss_path = Path('{}_loss.json'.format(prefix))
        self.acc_path = Path('{}_acc.json'.format(prefix))

        # self.loss_path = self.loss_path.resolve()
        # self.acc_path = self.acc_path.resolve()
        # self.loss_path.parent.mkdir(parents=True, exist_ok=True)
        # self.acc_path.parent.mkdir(parents=True, exist_ok=True)

    def on_epoch_end(self, epoch, logs):
        self.train_loss.append(logs.get('loss'))
        self.train_acc.append(logs.get('acc'))

        df_loss = pd.DataFrame()
        df_loss['train_loss'] = self.train_loss
        df_loss.to_json(str(self.loss_path), orient='split')

        df_loss = pd.DataFrame()
        df_loss['train_acc'] = self.train_acc
        df_loss.to_json(str(self.acc_path), orient='split')


def get_model():
    vgg = VGG16(weights='imagenet', include_top=False, pooling='max')
    x = vgg.output
    x = Dense(32, activation='relu')(x)
    x = Dropout(0.5)(x)
    x = Dense(8, activation='relu')(x)
    x = Dropout(0.5)(x)
    x = Dense(1, activation='softmax')(x)

    return Model(inputs=vgg.input, outputs=x)


def main():
    with tf.device('/gpu:3'):
        model = get_model()

    opt = RMSprop()
    model.compile(loss='mse', optimizer=opt, metrics=['acc'])
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
        'validation_data': (x_val, y_val)
        'shuffle': True,
        'callbacks': [
            MyLogger(prefix='vgg'),
            ModelCheckpoint(filepath="./vgg_epoch{epoch:02d}_{loss:.3f}.h5")
        ]
    } # yapf: disable

    model.fit(**arg)


if __name__ == '__main__':
    main()