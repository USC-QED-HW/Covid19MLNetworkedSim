- Loss for estimating "infectiousness" and "i_out" variables doesn't seem to improve after 32 epochs.
- SGD optimizer cannot go below ~5e-3 for mean squared error, and ~0.07 for root mean squared error ("infectiousness"). Choose ADAM for continuous variables.

- Ask QED lab about how to choose optimizer (SGD/ADAM/???) and whether or not to use early stopping (non reproducible experiments).
