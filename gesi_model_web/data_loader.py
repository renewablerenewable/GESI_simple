import copy
import json
import os
import pandas as pd

from gesi_model_web.core.logger import Logger


class DataLoader:
    def __init__(self, configuration, logger):
        self.logger = Logger(self.__class__.__name__, logger)

        self.data_path = configuration.data_path

        fname, ext = os.path.splitext(self.data_path)

        if ext not in ['.xlsx', '.json']:
            raise TypeError("Not allowed data file format: {}".format(ext))

        self.data_type = ext

        with open(configuration.set_path) as f:
            self.sets = json.load(f)

        self._data = None
        self._control = dict()

        self._result_data = None

    def load_control(self):
        return self._control

    def load_data(self):
        if self.data_type == '.xlsx':
            self.load_data_excel()

        elif self.data_type == '.json':
            self.load_data_json()

    def load_data_json(self):
        pass

    # GESI customized excel format
    def load_data_excel(self):
        self.logger.print_info_line("Load Data")
        init_data = dict()
        result_data = dict()

        df_control = self.extract_control()
        self._control['year'] = df_control.loc['year'][1]
        self._control['ndc'] = df_control.loc['NDC'][1]
        self._control['ratio_pv'] = df_control.loc['ratio_PV'][1]
        self._control['ratio_wt'] = df_control.loc['ratio_WT'][1]
        self._control['ratio_wt_off'] = df_control.loc['ratio_WT_off'][1]
        self._control['hydrogen_import_share'] = df_control.loc['hydrogen_import_share'][1]
        # self._control['building_retrofit_rate'] = df_control.loc['building retrofit rate'][1]
        # self._control['bevs_share'] = df_control.loc['BEVs share'][1]
        # self._control['industry_decarbonization'] = df_control.loc['industry decarbonization'][1]

        # Load Set Data
        for k, v in self.sets.items():
            init_data[k] = {None: v}

        # Load Param Data
        df_NGspec = self.extract_NGspec()
        df_NGspec.fillna(0., inplace=True)
        NGspec = dict()

        for P_FN in self.sets['P_FN']:
            for i_trait in self.sets['i_trait']:
                NGspec[(P_FN, i_trait)] = df_NGspec.loc[P_FN][i_trait]

        init_data["NGspec"] = NGspec

        df_Cspec_iter = self.extract_Cspec_iter()
        df_Cspec_iter.fillna(0., inplace=True)
        Cspec_iter = dict()

        for P_FC in self.sets['P_FC']:
            for i_trait in self.sets['i_trait']:
                Cspec_iter[(P_FC, i_trait)] = df_Cspec_iter.loc[P_FC][i_trait]

        init_data["Cspec_iter"] = Cspec_iter

        df_Distributions = self.extract_Distributions()
        df_Distributions.fillna(0., inplace=True)
        Distributions = dict()

        for t in self.sets['t']:
            for dis in self.sets['dis']:
                Distributions[(t, dis)] = df_Distributions.loc[t][dis]

        init_data["Distributions"] = Distributions

        df_cost = self.extract_cost()
        df_cost.fillna(0., inplace=True)
        cost = dict()

        row_costs = df_cost.index.values
        col_costs = df_cost.columns.values

        for tech in self.sets['tech']:
            for c in self.sets['c']:
                if tech in row_costs and c in col_costs:
                    cost[(tech, c)] = df_cost.loc[tech][c]
                else:
                    cost[(tech, c)] = 0.0

        init_data["cost"] = cost

        df_specs = self.extract_specs()
        df_specs.fillna(0., inplace=True)
        specs = dict()

        row_specs = df_specs.index.values
        col_specs = df_specs.columns.values

        for tech in self.sets['tech']:
            for trait in self.sets['trait']:
                if tech in row_specs and trait in col_specs:
                    specs[(tech, trait)] = df_specs.loc[tech][trait]
                else:
                    specs[(tech, trait)] = 0.0

        init_data["specs"] = specs

        df_fossil = self.extract_fossil()
        df_fossil.fillna(0., inplace=True)
        fossil = dict()

        row_fossil = df_fossil.index.values
        col_fossil = df_fossil.columns.values

        for fuel in self.sets['fuel']:
            for coeff in self.sets['coeff']:
                if fuel in row_fossil and coeff in col_fossil:
                    fossil[(fuel, coeff)] = df_fossil.loc[fuel][coeff]
                else:
                    fossil[(fuel, coeff)] = 0.0

        init_data["fossil"] = fossil

        em_cap = self.extract_em_cap().loc['em_cap']['price']
        init_data["em_cap"] = {None: em_cap}

        init_data["ratio_PV"] = {None: self._control['ratio_pv']}
        init_data["ratio_WT"] = {None: self._control['ratio_wt']}
        init_data["ratio_WT_off"] = {None: self._control['ratio_wt_off']}
        init_data["hydrogen_import_share"] = {None: self._control['hydrogen_import_share']}

        init_data['correction_wind'] = {None: 0.55}

        df_Transportation = self.extract_Transportation()

        N_Evs = df_Transportation.loc['N_Evs'][0]
        av_distance = df_Transportation.loc['av_distance'][0]
        bat_cap = df_Transportation.loc['bat_cap'][0]
        c_rate = df_Transportation.loc['c_rate'][0]
        M_share = df_Transportation.loc['M_share'][0]
        C_share = df_Transportation.loc['C_share'][0]
        eff_EV = df_Transportation.loc['eff_EV'][0]

        init_data['N_Evs'] = {None: N_Evs}
        init_data['av_distance'] = {None: av_distance}
        init_data['bat_cap'] = {None: bat_cap}
        init_data['c_rate'] = {None: c_rate}
        init_data['M_share'] = {None: M_share}
        init_data['C_share'] = {None: C_share}
        init_data['eff_EV'] = {None: eff_EV}

        df_Economy = self.extract_Economy()

        EL = df_Economy.loc['EL'][0]
        H = df_Economy.loc['H'][0]
        discount = df_Economy.loc['discount'][0]
        gas_D = df_Economy.loc['gas_D'][0]
        em_heat_r = df_Economy.loc['em_heat_r'][0]
        em_heat_c = df_Economy.loc['em_heat_c'][0]
        em_tr = df_Economy.loc['em_tr'][0]
        em_ind = df_Economy.loc['em_ind'][0]
        el_h_new = df_Economy.loc['el_h_new'][0]
        el_h_old = df_Economy.loc['el_h_old'][0]
        smart_share = df_Economy.loc['smart_share'][0]
        flex_bus = df_Economy.loc['flex_bus'][0]

        init_data['EL'] = {None: EL}
        init_data['H'] = {None: H}
        init_data['discount'] = {None: discount}
        init_data['gas_D'] = {None: gas_D}
        init_data['em_heat_r'] = {None: em_heat_r}
        init_data['em_heat_c'] = {None: em_heat_c}
        init_data['em_tr'] = {None: em_tr}
        init_data['em_ind'] = {None: em_ind}
        init_data['el_h_new'] = {None: el_h_new}
        init_data['el_h_old'] = {None: el_h_old}
        init_data['smart_share'] = {None: smart_share}
        init_data['flex_bus'] = {None: flex_bus}

        init_data['inv_NG'] = {None: 1990000}
        init_data['fx_NG'] = {None: 61600}
        init_data['va_NG'] = {None: 2.2}
        init_data['life_NG'] = {None: 30}
        init_data['inv_coal'] = {None: 651200}
        init_data['fx_coal'] = {None: 26592}
        init_data['va_coal'] = {None: 2.5}
        init_data['life_coal'] = {None: 30}

        self._data = {None: init_data}

        # self.logger.print_info_line('Loading Model Data Completed')

        # df_industry_demand = self.extract_insustry_demand()
        # df_residential_heat = self.extract_resiential_heat()
        # df_commercial_heat = self.extract_commercial_heat()
        # df_transportation_extended = self.extract_transportation_extended()
        df_specs_extended = self.extract_specs_extended()

        # result_data['industry_demand'] = df_industry_demand
        # result_data['residential_heat'] = df_residential_heat
        # result_data['commercial_public_heat'] = df_commercial_heat
        # result_data['transportation_extended'] = df_transportation_extended
        result_data['specs_extended'] = df_specs_extended

        self._result_data = result_data

    def load_model_data(self):
        return self._data

    def load_result_data(self):
        return self._result_data

    def extract_control(self):
        df = pd.read_excel(self.data_path, engine='openpyxl', sheet_name='control', usecols='A:B', nrows=8,
                           index_col=0, header=None)
        df.fillna(0., inplace=True)
        df.index.name = None

        return df

    def extract_table(self, sheet_name, usecols, nrows):
        df = pd.read_excel(self.data_path, engine='openpyxl', sheet_name=sheet_name, usecols=usecols, nrows=nrows,
                           index_col=0)
        df.fillna(0., inplace=True)
        df.index.name = None

        return df

    def extract_partial_table(self, sheet_name, usecols, header, nrows):
        df = pd.read_excel(self.data_path, engine='openpyxl', sheet_name=sheet_name, usecols=usecols, header=header,
                           nrows=nrows, index_col=0)
        df.fillna(0., inplace=True)
        df.index.name = None

        return df

    def extract_scalar_table(self, sheet_name, usecols, header, nrows):
        df = pd.read_excel(self.data_path, engine='openpyxl', sheet_name=sheet_name, usecols=usecols, header=header,
                           nrows=nrows)
        df.fillna(0., inplace=True)

        return df

    def extract_NGspec(self):
        return self.extract_table('NG', 'A:D', 89)

    def extract_Cspec_iter(self):
        return self.extract_table('Coal', 'A:C', 71)

    def extract_Distributions(self):
        return self.extract_table('Hourly', 'A:I', 8760)

    def extract_cost(self):
        return self.extract_table('costs', 'A:E', 25)

    def extract_specs(self):
        return self.extract_table('specs', 'A:G', 23)

    def extract_fossil(self):
        return self.extract_table('Fuel_costs', 'A:C', 4)

    def extract_em_cap(self):
        return self.extract_table('Fuel_costs', 'A:B', 7)

    def extract_Transportation(self):
        return self.extract_table('Transportation', 'A:B', 7)

    def extract_Transportation_yearly(self):
        return self.extract_scalar_table('Transportation', 'D:I', 35, 4)

    def extract_Economy(self):
        return self.extract_table('Economy', 'A:B', 12)

    def extract_Economy_yearly(self):
        return self.extract_scalar_table('Economy', 'A:G', 17, 11)

    # Data for Result Excel
    def extract_insustry_demand(self):
        return self.extract_partial_table('Industry demand', 'G:O', 118, 18)

    # def extract_resiential_heat(self):
        # return self.extract_table('Residential heat', 'A:N', 118)

    # def extract_commercial_heat(self):
        # return self.extract_table('Commercial_public heat', 'A:O', 118)

    # def extract_transportation_extended(self):
        # return self.extract_table('Transportation', 'A:AR', 34)

    def extract_specs_extended(self):
        return self.extract_partial_table('specs', 'A:H', 29, 23)