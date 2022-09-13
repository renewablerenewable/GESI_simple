# GESI Open Source Project

## Introduction
Gesi Model is designed for modeling electricity demand and power generation in Republic of Korea, in order to estimate the proper number of additional renewable energy production facility while gradually decreasing classic
power plants. <br>
<br>
This project is powered by Green Energy Strategy Institute(GESI) and (c) Entropy Paradox<br>

## Package Structure
`data/` : Contains Sector_coupling_data_2_XXXX.xlsx datasets<br>
`data_preprocessing/`: Constains data preprocessors. Not directly used.<br>
`examples/`: Contains example codes for running Gesi Model<br>
`gams_original/`: Direct conversion from gams to pyomo<br>
`gesi_model/`: Main source directory for Gesi Model Project <br>
`multiple_models/`: Another way of implementation for pre-made multiple model<br>
`notebook/`: Miscellaneous notebook file used for brainstorming and testing during implementing gesi model<br>

## Setting up Environment
- Create Virtual Environment

You can use any python virtual environment.

```
# Create conda environment
# python version must be 3.7 or 3.8
$ conda create -n [env name] python=[python version]

# Create virtualenv
$ python3 -m venv [virtualenv path] --python=[python path]
```

- Install Packages
```
# Install packages via requirements.txt
$ pip install -r requirements.txt

# Direct Installation
$ pip install conda-forge pyomo cplex pandas openpyxl jupyter

# Installation using conda
$ conda install -c conda-forge pyomo cplex 
$ conda install pandas openpyxl jupyter
```

## Running Gesi Model
It is possible to look up example code for running default Gesi Model using Sector_coupling_data_2_gesi.xlsx data in `examples/` directory.<br>
The code below is `examples/gesi.py`.

```
# examples/gesi.py

import os
import sys

parent_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_dir)

from gesi_model import *

datapath = '../data/Sector_coupling_data_2_gesi.xlsx'
name = 'gesi'

model = create_model(name=name)
solver = ModelSolver(model, datapath, name=name, save_result=True, solver='cplex', verbose=1)

solver.solve_and_update()
```
Then the results will be saved at `examples/results_gesi` directory. 

