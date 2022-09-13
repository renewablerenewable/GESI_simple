from pyomo.environ import *
from pyomo.opt import SolverFactory

from gesi_model_web.core.configuration import Configuration
from gesi_model_web.core.logger import Logger


class SolverInstance:
    def __init__(self, model, configuration, logger):
        self._logger = Logger(self.__class__.__name__, logger)

        if not isinstance(model, AbstractModel):
            raise TypeError('{} is expected, {} is given instead'.format(type(AbstractModel), type(model)))

        if not isinstance(configuration, Configuration):
            raise TypeError('{} is expected, {} is given instead'.format(type(Configuration), type(configuration)))

        self._name = '{}_instance'.format(name)
        self._model = model
        self._solver = SolverFactory(configuration.solver)
        self._solver.options = configuration.solver_options

        self._instance = None

        self._year = None

        self._verbose = True if configuration.verbose > 0 else False

        self._logger.print_info_line("Solver Instance Initialized")
        self._logger.print_info_line("Solver Options: {}".format(configuration.solver_options))

    def create_instance(self, init_data, year):
        self._set_year(year)
        self._instance = self._model.create_instance(init_data, report_timing=self._verbose, name=self._name)

    def _set_year(self, year):
        self._year = year

    def solve(self):
        self._logger.print_info_line("year {} : Start Solving Model.".format(self._year))
        result = self._solver.solve(self._instance, tee=self._verbose)

        if self._verbose:
            result.write()

        return self._instance, result
