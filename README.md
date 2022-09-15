# GESI Open Source Project

## Introduction
Gesi Model is designed for modeling electricity demand and power generation in Republic of Korea, in order to estimate the proper number of additional renewable energy production facility while gradually decreasing classic
power plants. <br>
<br>
This project is powered by Green Energy Strategy Institute(GESI) and (c) Entropy Paradox<br>


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
The code below is `examples/gesi_web.py`.

```
"""
    Default Gesi Model Example
"""
import os
import sys

parent_dir = os.path.dirname(os.getcwd())
sys.path.append(parent_dir)

web_model_dir = os.path.join(parent_dir, 'gesi_model_web')
sys.path.append(web_model_dir)

from gesi_model_web.run import ModelExecutor

data_path = 'Sector_coupling_data_2_web_custom_v3.xlsx'
# data_path = "../data/web/data/Sector_coupling_data_2_web_v4.xlsx"
name = 'gesi_web_jupyter'

executor = ModelExecutor(data_path, name=name, save_result=True, solver='cplex', verbose=1)
solver = executor.run_once()
