# dind

`dind` is a lightweight Python library that automatically imports NumPy and Pandas as `np` and `pd`.

## Installation
```sh
pip install dind
```
## Usage
```sh
from dind import np, pd

print(np.array([1, 2, 3]))
print(pd.DataFrame({"A": [1, 2, 3]}))

```