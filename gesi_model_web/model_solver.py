import datetime
import logging

from gesi_model_web.core.configuration import Configuration
from gesi_model_web.core.logger_core import LoggerCore
from gesi_model_web.core.logger import Logger

from gesi_model_web.data_loader import DataLoader
from gesi_model_web.model_2030 import create_2030_model
from gesi_model_web.model_2050 import create_2050_model
from gesi_model_web.solver_instance import SolverInstance
from gesi_model_web.reporter import Reporter


class ModelSolver:
    def __init__(self, *args, **kwargs):

        if len(args) != 1:
            raise TypeError('{} takes exactly one positional argument ({} given)'
                            .format(self.__class__.__name__, len(args)))

        data_path = args[0]
        # 미리 빼둬야 configuration에서 에러가 안남
        logger = kwargs.pop('logger', None)

        if not isinstance(data_path, str):
            raise TypeError('{} is expected, {} is given instead'.format(type(str), type(data_path)))

        self._configuration = Configuration(data_path, **kwargs)

        if logger is None:
            logger = LoggerCore(self._configuration.name)

        self._logger = Logger(self.__class__.__name__, logger)

        # Create Data Loader Instance
        self._data_loader = DataLoader(self._configuration, logger)
        self._data_loader.load_data()

        self._configuration.load_control(**self._data_loader.load_control())

        # Create Solver Instance
        if self._configuration.year < 2035:
            model = create_2030_model(self._configuration.name)
        elif self._configuration.year > 2034:
            model = create_2050_model(self._configuration.name)
        else:
            # Not possible
            raise ValueError('year {} is Invalid. Please Choose valid year'.format(self._configuration.year))

        self._init_time = datetime.datetime.now()
        self._solver_instance = SolverInstance(model, self._configuration, logger)

        # Create Reporter Instance
        self._save_result = self._configuration.save_result
        self._reporter = Reporter(self._configuration, self._data_loader.load_result_data(), logger)

        self._logger.print_info_line("Model Solver Initialized")
        self._logger.print_info_line("Chosen year: {}".format(self._configuration.year))

        if self._configuration.year < 2035 :
            self._logger.print_info_line(
                "ndc: {}, ratio_pv: {}, ratio_wt: {}"
                    .format(self._configuration.ndc, self._configuration.ratio_pv, self._configuration.ratio_wt
                            ))

        elif self._configuration.year > 2034 :
            self._logger.print_info_line(
                "ratio_pv: {}, ratio_wt: {}"
                    .format(self._configuration.ratio_pv, self._configuration.ratio_wt
                            ))

    def print_running_time(self):
        self._logger.print_info_line("Running Time: {}".format(datetime.datetime.now() - self._init_time))

    def solve(self):
        self._logger.print_info_line("Create Solver Instance. Year : {}".format(self._configuration.year))
        self._solver_instance.create_instance(self._data_loader.load_model_data(), self._configuration.year)

        self._logger.print_info_line("Start Solving Model")
        instance, result = self._solver_instance.solve()

        if self._save_result:
            self._reporter.save_result(instance, result)

        self._logger.print_info_line("Model Solver Operation Completed")
        self.print_running_time()

        return result
