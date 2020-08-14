#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import argparse

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow as tf

from tensorflow import keras

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.layers import Input

# Import dataset
from datasets import *

# Returns uncompiled LSTM model
def build_model(X_shape, variable):
    model = Sequential()
    model.add(Input(shape=X_shape))

    for i in range(num_lstm-1):
        model.add(LSTM(lstm_hidden, return_sequences=True))
        model.add(Dropout(percent_dropout))

    model.add(LSTM(lstm_hidden))
    model.add(Dropout(percent_dropout))

    for i in range(num_dense-1):
        model.add(Dense(dense_hidden, activation='relu'))

    if categorical:
        categories = len(synda.y[variable].cat.categories)
        model.add(Dense(categories, activation='softmax'))
    else:
        model.add(Dense(1, activation='relu'))

    return model

def determine_F():
    loss = None
    metrics = []
    optimizer = keras.optimizers.Adam(learning_rate=learning_rate)
    callbacks = []

    if early_stopping:
        callbacks.append(keras.callbacks.EarlyStopping(monitor='loss', patience=7, mode='min', verbose=1))

    if categorical:
        loss = keras.losses.SparseCategoricalCrossentropy()
        metrics = ['accuracy']
    else:
        loss = keras.losses.MeanSquaredError()
        metrics = []

    return loss, metrics, optimizer, callbacks

def determine_optimizer():
    optimizer = keras.optimizers.Adam(learning_rate=learning_rate)

    if gradient_clipping:
        optimizer.clipvalue = 100

    return optimizer

def train_model(model, train, valid, callbacks):
    model.fit(train, epochs=epochs, batch_size=batch_size, verbose=1, validation_data=valid, callbacks=callbacks)

if __name__ == "__main__":
    # Seed random number generators to start w/ same weights + biases
    MAGIC = 0xDEADBEEF
    from numpy.random import seed
    seed(MAGIC)
    from tensorflow.random import set_seed
    set_seed(MAGIC)

    # Variable choices
    variables = [
        'i_rec_prop',
        'infectiousness',
        'i_out',
        'k',
        'network',
        'initial_infected',
        'population'
    ]

    # Import arguments
    parser = argparse.ArgumentParser()

    # Number of epochs to use when training
    parser.add_argument('--epochs', type=int, default=32)

    # Which variable to train on
    parser.add_argument('--variable', type=str, choices=variables, default='infectiousness')

    # Batch size
    parser.add_argument('--batch_size', type=int, default=32)

    # Value to use for dropout layers after LSTM model
    parser.add_argument('--percent_dropout', type=float, default=0)

    # Number of dense layers
    parser.add_argument('--num_dense', type=int, default=1)

    # Number of LSTM layers
    parser.add_argument('--num_lstm', type=int, default=2)

    # Number of hidden units in dense layer
    parser.add_argument('--dense_hidden', type=int, default=8)

    # Number of hidden units in LSTM layer
    parser.add_argument('--lstm_hidden', type=int, default=16)

    # Rate of learning in ADAM gradient descent
    parser.add_argument('--learning_rate', type=float, default=0.01)

    # Whether or not to add gradient clipping
    parser.add_argument('--gradient_clipping', type=bool, default=True)

    # Whether or not to use early stopping
    parser.add_argument('--early_stopping', type=bool, default=False)

    args = parser.parse_args()

    # Hyperparameters
    epochs            = args.epochs
    batch_size        = args.batch_size
    percent_dropout   = args.percent_dropout
    num_dense         = args.num_dense
    num_lstm          = args.num_lstm
    dense_hidden      = args.dense_hidden
    lstm_hidden       = args.lstm_hidden
    learning_rate     = args.learning_rate
    gradient_clipping = args.gradient_clipping
    variable          = args.variable
    early_stopping    = args.early_stopping

    # Import synthetic data set
    synda = SyntheticDataset('synthetic-dataset-100.csv.gz')

    # Tell if variable is categorical or not
    categorical = variable in synda.categorical_variables

    # Data set size
    print("dataset_size: {}".format(len(synda)))

    # Get split train and validation set
    train, valid = synda.split([0.8, 0.2])

    # Grab the input shape
    input_shape = train.X.shape[1:]

    print("train_size: {}".format(len(train.X)))
    print("valid_size: {}".format(len(valid.X)))

    # Convert to tensorflow datasets
    train = tf.data.Dataset.from_tensors((train.X, train.variable(variable)))
    valid = tf.data.Dataset.from_tensors((valid.X, valid.variable(variable)))

    # Determine shapes, metrics, and loss function
    loss, metrics, optimizer, callbacks = determine_F()

    # Build the uncompiled model
    model = build_model(input_shape, variable)

    # Compile the model
    model.compile(metrics=metrics, loss=loss, optimizer=optimizer)

    print(model.summary())

    # Run model .fit
    train_model(model, train, valid, callbacks)
