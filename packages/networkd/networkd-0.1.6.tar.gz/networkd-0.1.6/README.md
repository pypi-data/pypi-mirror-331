# networkd

Hi! Thanks for checking out networkd. networkd seamlessly builds bipartite networks/graphs. Examples of data in bipartite form include songs in playlists or users and the movies they watch. These data are very popular in studying consumer trends, building recommendation engines, and other research related to network science. However, no package in Python seems to seamlessly and efficiently embed such data into a graph/network in order to summarize the relationship between categories (songs, users) with respect to their entities (playlists, movies). networkd fills this gap by making the network/graph building process efficient and seamless!

See Usage below for an example case of how to quickly embed the data into a co-occurence matrix using the embed class. More functionality to come! 

## Installation

```bash
$ pip install networkd
```

## Usage

import networkd as nd
import pandas as pd

#create pandas data frame of bipartite data. (also accepts dictionary)

data = pd.DataFrame({
    0: ['cat1', 'cat1', 'cat2', 'cat3', 'cat2', 'cat3'],
    1: ['ent1', 'ent2', 'ent1', 'ent3', 'ent2', 'ent1'],
    2: [2, 3, 4, 5, 7, 9]
}) 

#create co-occurrence matrix (output is pandas df)

nd.embed(data, self_loops = False)

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`networkd` was created by Lorenzo Giamartino. It is licensed under the terms of the MIT license.

## Credits

`networkd` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
