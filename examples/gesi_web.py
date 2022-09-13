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