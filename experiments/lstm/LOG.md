# LSTM Training Notes (Kosi Nwabueze)

## Tips

- Loss for estimating "infectiousness" and "i_out" variables doesn't seem to improve after 32 epochs.
- SGD optimizer cannot go below ~5e-3 for mean squared error, and ~0.07 for root mean squared error ("infectiousness"). Choose ADAM for continuous variables.
- Ask QED lab about how to choose optimizer (SGD/ADAM/???) and whether or not to use early stopping (non reproducible experiments).
- Use less hidden nodes. Use GRUs.
- Use a scheduled learning rate. (starting w/ .01).
- Smooth loss function. Look at different loss functions.
- Use partial dataset for initial search.
- Use 32, 64, 128 batch size if I have lots of memory. See how long each epoch takes.
- Starting w/ 0.2 dropout go to ~0.5. Usually in between. Prevents overfitting.
- Advantage to using multiple LSTM layers (deeper networks) will help with underfitting. Model might need more layers to learn.
- If validation accuracy > training accuracy is underfitting.
- High dropout percentage may cause underfitting.

- **From Marco**:
    - Critical parameters: learning rate, gradient clipping, and dropout
    - Just choose a reasonable size (optimize size + speed) for batch size
    - Epochs: Keep increasing until convergance can be seen.
    - 

- **From Sara**:

- **Hyperlinks**:
    - https://stanford.edu/~shervine/teaching/cs-229/cheatsheet-machine-learning-tips-and-tricks
    - https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5840242/ 
    - https://my.guild.ai/t/guild-ai-documentation/64 
    - https://www.tensorflow.org/api_docs 

## Quantitative variables

- Doing hyperparameter search initially with infectiousness (other quantitative variables should use same hypermodels).
- Not messing w/ loss functions or optimizers initially (after all other hyperparams have been optimized).
- Doing grid search, just choosing values I think would be good and testing them out.

- Optimizer: ADAM (without scheduling)
- Loss: Mean-squared error

- **TODO**: Try dropping out STEP column and seeing if that improves performance after all other hyperparameters are optimized.

### Finding initial parameters

- **Hyperparameters**:
    - Epochs = [10, 20], patience = 5, batch size = 16, 32, 64, learning rate = 0.01
    - Dropout = [0.1, 0.2, 0.3, 0.4, 0.5]
    - Early stopping = [yes, no]
    - Gradient clipping = [yes, no]
    - Number of LSTM layers = 1
    - Number of LSTM nodes = 8
    - Number of dense layers = 1
    - Hidden layer activation = relu

- Batch size
    - Computer can handle batch size of 64, stick with it.

- Epochs
    - Number of epochs don't affect learning at this stage. Learning sucks.
    - Use early stopping, seems to be useful.

- Gradient clipping
    - Seems to make no difference.

- All models are not learning, either summarizing or loss doesn't change at all.

- **Next Steps**:
    - Experiment with number of LSTM layers.

### Changing Number of LSTM layers (1, 2, 3, 4, 5, 6)

- **Hyperparameters**:
    - Epochs = 10, patience = 5, batch size = 64, learning rate = 0.01, dropout = 0
    - Number of dense layers = 1
    - Number of LSTM layers = [1, 2, 3, 4, 5, 6]
    - Number of LSTM nodes = 8
    - Early stopping = yes
    - Gradient clipping = [yes, no]
    - Hidden layer activation = relu

- Gradient clipping has negligible effect on training

- For 1, 4, and 5 layers:
    - No learning occurred **AT ALL**
    - **TODO**: Perhaps try again with lower learning rate?
    - 1 is probably just not sophisticated enough to learn.
    - 4 + 5 should not have performed that differently from 3 + 6 (maybe bad initial seed)?

- For 2, 3, and 6 layers:
    - 3 layers had lowest validation loss (but wasn't changing), maybe generalization?
    - 6 layers exhibit similar behavior to 3 layers.
    - 2 layers had the worst final loss + val loss, but seemed to be training (bumpy).
    - 2 layers also generalizes as validation loss only increases as in-set loss decreases.

- **Best Values**:
    - 2 LSTM layers
    - 3 LSTM layers
    - 6 LSTM layers

- **Generalization**:
    - Deep learning may be a good investment to look into (i.e. using more layers).
    - Learning rate is too high to be effective for learning. Increase epochs while I'm at it.

- **Next Steps**:
    - Tamper with number of hidden LSTM nodes (powers of 2 like 8, 16, 32, 64).

### Changing number of hidden nodes in LSTM layers (8, 16, 32, 64*)
> My GPU (1070 Ti w/ 8GB VRAM) cannot handle 64 LSTM nodes and too many layers.

- **Hyperparameters**:
    - Epochs = 20, patience = 7, batch size = 64, learning rate = [0.01, 0.001], dropout=0
    - Number of dense layers = 1
    - Number of LSTM layers = [2, 3, 6]
    - Number of LSTM nodes = [8, 16, 32, 64*]
    - Early stopping = yes
    - Gradient clipping = no (wasn't a problem before)
    - Hidden layer activation = relu

- For 2 LSTM layers:
    - Only 8 hidden nodes seems to learn with larger learning rate (larger number of nodes can't learn)
    - 64 + 32 nodes doesn't seem to learn very well (add dropout layers) even w/ small learning rate
    - 16 nodes seems to be the sweet spot (used in Tessemer, best looking curve)
    - 8 nodes also seems to work very well (lowest validation + training loss)
    
- For 3 LSTM layers:
    - Larger learning rate (0.01) does worse training (not smoothed at all)
    - 8 and 32 hidden nodes performed worse with larger learning rate
    - 8, 16, 32 perform about as well with smaller learning rate (0.001)

- For 6 LSTM layers:
    - Tensorflow wouldn't allow many values to compile bc of VRAM limit
    - 8 hidden nodes w/ smaller learning rate performed the best loss wise out of all experiments
    - 16 hidden nodes performed well but bumpier loss curves (a lot of peaks + valleys)
    - 16 nodes couldn't learn with higher learning rate
    - 8 nodes had bumpier performance with higher learning rate

- **Best Values**:
    1) 8 hidden LSTM nodes, 6 LSTM layers, 0.001 learning rate
    2) 8 hidden LSTM nodes, 2 LSTM layers, 0.001 learning rate
    3) 16 hidden LSTM nodes, 2 LSTM layers, 0.001 learning rate
    4) 8 hidden LSTM nodes, 3 LSTM layers, 0.001 learning rate

- **Generalizations**:
    - Learning rate should be no larger than 0.001 for further experiments.
    - Lower number of LSTM nodes seems to be good. Increasing nodes doesn't increase performance.
    - Deep learning may be good, i.e. using **MORE** layers may be more beneficial.

- **Next steps**:
    - **TODO**: Try with more LSTM layers, maybe 8, 9, 12 (want to see if powers of 3 are special).
    - **TODO**: Retry with RMSprop. Retry with gradient descent and a scheduler.
    - Experiment with number of hidden layers **THEN** number of hidden nodes in that order.