import os
import sys

parent_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_dir)

from core.logger_core import LoggerCore
from core.logger import Logger
from model_solver import ModelSolver


class ModelExecutor:
    def __init__(self, *args, **kwargs):
        if len(args) != 1:
            raise TypeError('{} takes exactly one positional argument ({} given)'
                            .format(self.__class__.__name__, len(args)))

        self.dataset_path = args[0]

        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError("{} does not exist".format(self.dataset_path))

        self.name = kwargs.pop('name', 'gesi_web')
        self.tag = 'RunScript'

        self.save_result = kwargs.pop('save_result', True)
        self.solver = kwargs.pop('solver', 'cplex')
        self.verbose = kwargs.pop('verbose', 1)

        # For Macro Execution
        self.save_point = None
        self.executed_dataset = list()

        logger = LoggerCore.create_logger(self.name)
        self.logger = Logger(self.tag, logger)

        self.logger.print_info_line('RunScript Initialized')

    def run_once(self):
        if not os.path.isfile(self.dataset_path):
            raise ValueError("Input Dataset must be a file")

        filename, ext = os.path.splitext(self.dataset_path)

        if ext != '.xlsx':
            raise ValueError("Input Dataset must be an EXCEL workbook")

        model_solver = ModelSolver(self.dataset_path,

                                   name=self.name,
                                   logger=self.logger.get_logger(),

                                   save_result=self.save_result,
                                   solver=self.solver,
                                   verbose=self.verbose)

        model_solver.solve()
        return model_solver

    def run(self, **kwargs):
        if not os.path.isdir(self.dataset_path):
            raise ValueError("Input Dataset for multiple execution must be a directory")

        self.save_point = kwargs.pop('save_point', None)
        default_path = os.path.join(os.getcwd(), 'results_{}'.format(self.name), 'save_point.txt')

        if self.save_point is None:
            if os.path.exists(default_path):
                self.save_point = default_path

        if self.save_point is not None:
            if not os.path.exists(self.save_point):
                raise ValueError("Invalid Save point: {}".format(self.save_point))

            savefile, ext = os.path.splitext(self.save_point)

            if ext != '.txt':
                raise ValueError("The savepoint must be a json format")

            self.logger.print_info_line("Load Savepoint: {}".format(self.save_point))
            with open(self.save_point, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()

                for line in lines:
                    self.executed_dataset.append(line.strip())

        # Set New Savepoint
        if self.save_point is None:
            self.save_point = default_path

        dataset = os.listdir(self.dataset_path)
        total = len(dataset)
        count = 0
        self.logger.print_info_line("Total Dataset: {}".format(total))

        for data in dataset:
            if data in self.executed_dataset:
                count += 1
                self.logger.print_info_line("[{} / {}] {} : Execution result already executed - PASSED".format(count, total, data))
                continue

            data_path = os.path.join(self.dataset_path, data)

            model_solver = ModelSolver(data_path,
                                       name=self.name,
                                       logger=self.logger.get_logger(),

                                       save_result=self.save_result,
                                       solver=self.solver,
                                       verbose=self.verbose)

            model_solver.solve()

            self.save(data)

            count += 1
            self.logger.print_info_line("[{} / {}] {} : Execution completed and saved".format(count, total, data))

    def save(self, dataset):
        with open(self.save_point, 'a', encoding='utf-8-sig') as f:
            f.write(dataset + '\n')


if __name__ == '__main__':

    name = 'gesi_web'

    # data_path = "../data/web/data/2030_0.4_1_9_0.5_0.1_강.xlsx"
    # data_path = "../data/web/data/2050_1_9_0.5_강.xlsx"
    # executor = ModelExecutor(data_path, name=name, save_result=True, solver='cplex', verbose=1)
    # executor.run_once()

    data_path = "../data/web/run_batch/2050_v4"
    executor = ModelExecutor(data_path, name=name, save_result=True, solver='cplex', verbose=0)
    executor.run()
