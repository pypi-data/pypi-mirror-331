# Causal Modeling with Stationary Diffusions

[![PyPi](https://img.shields.io/pypi/v/stadion?logo=PyPI)](https://pypi.org/project/stadion/)

This is the Python package for 
*"Causal Modeling with Stationary Diffusions"*
([Lorch et al., 2024](https://arxiv.org/abs/2310.17405)).
To install the latest version, run:
```bash
pip install stadion
```
The `stadion` package allows learning **stationary** systems of
**stochastic differential equations (SDEs)**, whose stationary densities
match the empirical distribution of a target dataset.
The target dataset for learning the SDEs
contains i.i.d. samples from the stationary density, 
not a time series.
Put differently, we perform system identification 
from the stationary distribution.
When provided with [several datasets](#multiple-interventional-datasets) 
(e.g., from different experimental conditions),
the algorithm learns one SDE model that fits all observed distributions
using jointly-learned intervention parameters that perturb 
the SDE model. 


The objective for learning the SDE parameters is the 
**kernel deviation from stationarity (KDS)**.
The KDS depends on the SDEs and a kernel function, and 
its sample approximation is computed using only the target dataset. 
Hence, optimizing the KDS does not require rolling-out trajectories 
from the SDE model or backpropagating gradients through time.
The SDE drift and diffusion functions can 
be **arbitrary nonlinear, differentiable functions**.
This package also provides the KDS as a stand-alone [loss function](#kds-loss-function).

Our implementation leverages efficient vectorization, auto-diff, 
JIT compilation, and (multi-device) hardware acceleration 
with [JAX](https://github.com/google/jax). 


## Quick Start

The following code demonstrates how to use the `stadion` package. 
In this example, we use the KDS to learn a linear stationary SDE model from 
a dataset sampled from a Gaussian distribution.
```python
from jax import random
from stadion.models import LinearSDE

key = random.PRNGKey(0)
n, d = 1000, 5

# generate a dataset
key, subk = random.split(key)
w = random.normal(subk, shape=(d, d))

key, subk = random.split(key)
data = random.normal(subk, shape=(n, d)) @ w

# fit stationary diffusion model
model = LinearSDE()
key, subk = random.split(key)
model.fit(subk, data)

# sample from model and get parameters
key, subk = random.split(key)
x_pred = model.sample(subk, 100)
params = model.param
```
Currently, the following SDE model classes are implemented in `stadion.models`:

- [`LinearSDE`](stadion/models/linear.py)
- [`MLPSDE`](stadion/models/mlp.py)

The `MLPSDE` model is a generalization of the `LinearSDE` model to
nonlinear drift functions.
o support the inference functionality in the code snippet above, 
new model classes have to inherit from
[`SDE`](stadion/sde.py) and [`KDSMixin`](stadion/inference.py)
and implement the methods decorated with `@abstractmethod`
like `LinearSDE` and `MLPSDE`.

## Additional Examples

### KDS loss function

The `stadion` package provides the KDS as an 
off-the-shelf loss function.
In the below, we define custom SDE functions `f` and `sigma`
and a kernel `k` and use [`kds_loss`](stadion/kds.py) to create the
corresponding loss function and its gradient with respect to the parameters of `f` and `sigma`.
This may be useful when using the KDS loss in
custom implementations that do not subclass from 
[`SDE`](stadion/sde.py) and [`KDSMixin`](stadion/inference.py).
Here, `f` and `sigma` can be arbitrary differentiable, possibly
nonlinear, functions.


```python
...

from jax import numpy as jnp, value_and_grad
from stadion import kds_loss

# SDE functions
def f(x, param):
    return param["w"] @ x + param["b"]

def sigma(x, param):
    return jnp.exp(param["c"]) * jnp.eye(d)

# kernel
def k(x, y):
    return jnp.exp(- jnp.square(x - y).sum(-1) / 100)

# create KDS loss function
loss_fun = kds_loss(f, sigma, k)

# compute loss and parameter gradient for dataset and a parameter setting
key, *subk = random.split(key, 4)
params = {
    "w": random.normal(subk[0], shape=(d, d)),
    "b": random.normal(subk[1], shape=(d,)),
    "c": random.normal(subk[2], shape=(d,)),
}

loss, dparams = value_and_grad(loss_fun, argnums=1)(data, params)
```

### Multiple Interventional Datasets

Provided multiple datasets, 
the algorithm jointly learns one causal SDE model with 
separate intervention parameters for each dataset.
The intervention parameters are used to
fit all observed distributions through interventions 
in the shared SDE model.
Below, we add two interventional datasets and assume we know they 
intervened on the variables 2 and 4, respectively, which 
restricts the learnable intervention parameters to these variables.


```python
...

# sample two more datasets with shift interventions
a, targets_a =  3, jnp.array([0, 1, 0, 0, 0])
b, targets_b = -5, jnp.array([0, 0, 0, 1, 0])

key, subk_0, subk_1 = random.split(key, 3)
data_a = (random.normal(subk_0, shape=(n, d)) + a * targets_a) @ w
data_b = (random.normal(subk_1, shape=(n, d)) + b * targets_b) @ w

# fit stationary diffusion model
model = LinearSDE()
key, subk = random.split(key)
model.fit(
    subk,
    [data, data_a, data_b],
    targets=[jnp.zeros(d), targets_a, targets_b],
)

# get inferred model and intervention parameters
param = model.param
intv_param = model.intv_param

# sample from model under intervention parameters learned for 1st environment
intv_param_a = intv_param.index_at(1)
x_pred_a = model.sample(subk, 100, intv_param=intv_param_a)
```


## Custom Installation and Branches

The latest release is published on PyPI, 
so the best way to install `stadion` is using `pip`
as explained above.
For custom installations, we recommend using `conda` and generating a new environment 
via `conda env create --file environment.yaml`.

The repository consists of two branches:
- `main` (recommended): Lightweight and easy-to-use package for using `stadion` in your research or applications.
- `aistats`: Code to reproduce the results in [Lorch et al. (2024)](https://arxiv.org/abs/2310.17405). 
The purpose of this branch is reproducibility; the branch is not updated anymore and may contain outdated notation and documentation.

## Reference

```
@inproceedings{lorch2024causal,
  title={Causal Modeling with Stationary Diffusions},
  author={Lorch, Lars and Krause, Andreas and Sch{\"o}lkopf, Bernhard},
  booktitle={International Conference on Artificial Intelligence and Statistics},
  pages={1927--1935},
  year={2024},
  organization={PMLR}
}
```
