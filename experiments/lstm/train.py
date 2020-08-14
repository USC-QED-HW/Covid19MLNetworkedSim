#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import argparse

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from tensorflow import keras

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Flatten
from keras.layers import Dropout
from keras.layers import LSTM
from keras.layers import Input

# Import dataset
from datasets import *

# Returns uncompiled LSTM model
def build_model(input_shape, output_shape):
    model = Sequential()
    model.add(Input(shape=input_shape))

    for i in range(num_lstm-1):
        model.add(LSTM(lstm_hidden, return_sequences=True))
        model.add(Dropout(percent_dropout))

    model.add(LSTM(lstm_hidden))
    model.add(Dropout(percent_dropout))

    for i in range(num_dense-1):
        model.add(Dense(dense_hidden, activation='relu'))

    if categorical:
        model.add(Dense(output_shape, activation='softmax'))
    else:
        model.add(Dense(output_shape, activation='relu'))

    return model

def determine_model_type(X, y, ds, variable):
    X_shape = X.shape[1:]
    loss = None
    metrics = []

    if categorical:
        loss = keras.losses.CategoricalCrossentropy()
        metrics = ['accuracy']
        y_shape = len(ds.y[variable].cat.categories)
    else:
        loss = keras.losses.MeanSquaredError()
        metrics = []
        y_shape = 1

    return X_shape, y_shape, loss, metrics

def determine_optimizer():
    optimizer = keras.optimizers.Adam(learning_rate=learning_rate)

    if gradient_clipping:
        optimizer.clipvalue = 100

    return optimizer

def train_model(model, X, y, X_val, y_val):
    model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=1, validation_data=(X_val, y_val))

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

    # Whether to use cumulative/daily time-series data
    parser.add_argument('--cumulative', type=bool, default=True)

    # Number of epochs to use when training
    parser.add_argument('--epochs', type=int, default=32)

    # Which variable to train on
    parser.add_argument('--variable', type=str, choices=variables, default='infectiousness')

    # Batch size
    parser.add_argument('--batch_size', type=int, default=32)

    # Value to use for dropout layers after LSTM model
    parser.add_argument('--percent_dropout', type=float, default=0)

    # Number of dense layers
    parser.add_argument('--num_dense', type=int, default=2)

    # Number of LSTM layers
    parser.add_argument('--num_lstm', type=int, default=2)

    # Number of hidden units in dense layer
    parser.add_argument('--dense_hidden', type=int, default=128)

    # Number of hidden units in LSTM layer
    parser.add_argument('--lstm_hidden', type=int, default=16)

    # Rate of learning in ADAM gradient descent
    parser.add_argument('--learning_rate', type=float, default=0.01)

    # Whether or not to add gradient clipping
    parser.add_argument('--gradient_clipping', type=bool, default=True)

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
    cumulative        = args.cumulative
    variable          = args.variable

    # Import synthetic data set
    synda = SyntheticDataset('synthetic-1595801342.297447.tar.gz', cumulative=cumulative)

    # Tell if variable is categorical or not
    categorical = variable in synda.categorical_vars

    # Data set size
    print("dataset_size: {}".format(len(synda)))

    # Get split dataset
    train_percentage = 0.5
    test_percentage = 0.25
    validation_percentage = 1 - train_percentage - test_percentage

    train, test, valid = synda.split(valid=True, train=train_percentage, test=test_percentage)

    print("train_size: {}".format(len(train)))
    print("valid_size: {}".format(len(valid)))

    # Split train into X and y
    X, y = train.tensors(variable)

    # Split into validate X + y
    X_val, y_val = valid.tensors(variable)

    # Split into test X + y
    X_test, y_test = test.tensors(variable)

    # Determine shapes, metrics, and loss function
    X_shape, y_shape, loss, metrics = determine_model_type(X, y, synda, variable)

    # Determine the optimizer
    optim = determine_optimizer()

    # Build the uncompiled model
    model = build_model(X_shape, y_shape)

    # Compile the model
    model.compile(metrics=metrics, loss=loss, optimizer=optim)

    # Run model .fit
    train_model(model, X, y, X_val, y_val)
