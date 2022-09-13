from configparser import ConfigParser
import os


class Configuration:
    def __init__(self, data_path, **kwargs):
        self._base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_path = data_path
        self._config = None

        if not os.path.exists(data_path):
            raise FileNotFoundError("{} does not exist".format(data_path))

        # solver config
        self._model_component_path = os.path.join(self._base_path, 'model_component')
        self.set_path = os.path.join(self._model_component_path, 'sets.json')
        self.result_set_path = os.path.join(self._model_component_path, 'result_sets.json')

        self.solver_options = dict()

        self.name = kwargs.pop('name', 'gesi_web')
        self.save_result = kwargs.pop('save_result', True)
        self.solver = kwargs.pop('solver', 'cplex')
        self.verbose = kwargs.pop('verbose', 0)

        # Check invalid keyword argument
        if len(kwargs) > 0:
            raise KeyError('{} is invalid keyword argument'.format(next(iter(kwargs))))

        self.result_path = os.path.join(os.getcwd(), 'results_{}'.format(self.name))

        if not isinstance(self.name, str):
            raise TypeError('{} is expected, {} is given instead'.format(type(str), type(self.name)))

        if not isinstance(self.save_result, bool):
            raise TypeError('{} is expected, {} is given instead'.format(type(bool), type(self.verbose)))

        if self.solver not in ['cplex']:
            raise ValueError('{} solver is not supported.'.format(self.solver))

        if not isinstance(self.verbose, int) or self.verbose < 0:
            raise TypeError('non-negative integer is expected, {} is given instead'.format(type(self.verbose)))

        self.years = [2025,2030,2035,2040,2045,2050]
        # self.NDC = [0.35, 0.4, 0.45, 0.5]
        # self.ratio_PV = [i for i in range(1, 10)]
        # self.building_retrofit_rates = [0.5, 1.0, 1.5, 2.0]
        # self.BEVs_shares = [0.1, 0.15, 0.2, 0.25]
        # self.industry_decarbonization_levels = ['약', '중', '강']

        # self.industry_decarbonization_map = {
        #     'low': '약',
        #     'middle': '중',
        #     'high': '강'
        # }

        self.year = None
        self.ndc = None
        self.ratio_pv = None
        self.ratio_wt = None
        self.building_retrofit_rate = None
        self.BEVs_share = None
        self.industry_decarbonization = None

    def load_control(self, **kwargs):
        self.year = kwargs.pop('year', 0)
        self.ndc = kwargs.pop('ndc', 0)
        self.ratio_pv = kwargs.pop('ratio_pv', 0)
        self.ratio_wt = kwargs.pop('ratio_wt', 0)
        self.ratio_WT_off = kwargs.pop('ratio_wt_off', 0)
        self.hydrogen_import_share = kwargs.pop('hydrogen_import_share',0)


        # Check invalid keyword argument
        # if len(kwargs) > 0:
            # raise KeyError('{} is invalid keyword argument'.format(next(iter(kwargs))))

        # if self.year not in self.years:
            # raise ValueError('year must be 2030 or 2050'.format(self.year))

        # if self.ratio_pv not in self.ratio_PV:
            # raise ValueError('Invalid ratio_pv value: {}, expected: {}'.format(self.ratio_pv, self.ratio_PV))

        # if self.ratio_wt not in self.ratio_PV:
            # raise ValueError('Invalid ratio_wt value: {}, expected: {}'.format(self.ratio_wt, self.ratio_PV))

        # if self.ratio_pv + self.ratio_wt != 10:
            # raise ValueError('year must be 2030 or 2050'.format(self.year))

        # if self.building_retrofit_rate not in self.building_retrofit_rates:
            # raise ValueError(
                # 'Invalid building retrofit rate value: {}, expected: {}'.format(self.building_retrofit_rate,
                                                                                # self.building_retrofit_rates))

        # if self.industry_decarbonization not in self.industry_decarbonization_levels:
            # raise ValueError(
                # 'Invalid industry decarbonization level: {}, expected: {}'.format(self.industry_decarbonization,
                                                                                  # self.industry_decarbonization_levels))

        # if self.year < 2035:
            # if self.ndc not in self.NDC:
                # raise ValueError('Invalid NDC value: {}, expected: {}'.format(self.ndc, self.NDC))

            # if self.BEVs_share not in self.BEVs_shares:
                # raise ValueError('Invalid BEVs_share value: {}, expected: {}'.format(self.BEVs_share, self.BEVs_shares))

        # elif self.year == 2050:
        #     self.solver_options['mip strategy subalgorithm'] = 1
        #     self.solver_options['mip tolerances absmipgap'] = 0.05
        #     self.solver_options['solver_io'] = 'mip'