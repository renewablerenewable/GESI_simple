import json
import os
import pandas as pd
from pyomo.core import value

from gesi_model_web.core.logger import Logger


class Reporter:
    def __init__(self, configuration, data, logger):
        self._result_path = configuration.result_path
        self._data = data
        self._graph_data = dict()
        self._logger = Logger(self.__class__.__name__, logger)

        if not os.path.exists(self._result_path):
            os.mkdir(self._result_path)

        self.t = 8760
        result_set_path = configuration.result_set_path
        with open(result_set_path) as f:
            self.result_sets = json.load(f)

        self.year = configuration.year
        # self.ndc = configuration.ndc
        # self.ratio_pv = configuration.ratio_pv
        # self.ratio_wt = configuration.ratio_wt
        # self.building_retrofit_rate = configuration.building_retrofit_rate
        # self.BEVs_share = configuration.BEVs_share
        # self.industry_decarbonization = configuration.industry_decarbonization

        self.result_yaml = None
        self.result_xlsx = None
        self.result_json = None

        if self.year < 2035:
            filename = '{}'.format(self.year)

        elif self.year > 2034:
            filename = '{}'.format(self.year)

        else:
            return

        self.result_yaml = os.path.join(self._result_path, '{}.yaml'.format(filename))
        self.result_xlsx = os.path.join(self._result_path, '{}.xlsx'.format(filename))
        self.result_json = os.path.join(self._result_path, '{}.json'.format(filename))

    def save_result(self, instance, result):
        # Report solver result
        result.write(filename=self.result_yaml)

        # Report xlsx results
        self._logger.print_info_line("Start reporting result.")
        index = [i for i in range(1, self.t + 1)]
        index = index + ['total sum']
        scalar_index = ['value']
        year_index = [' ', self.year]

        rep = self.report_rep(instance)
        rep_h = self.report_rep_h(instance)
        rep_g = self.report_rep_g(instance)
        new_invest = self.report_new_invest(instance)
        rep_annual = self.report_rep_annual(instance)
        rep_ind_h = self.report_rep_ind_h(instance)
        rep_economic = self.report_rep_economic(instance)
        # energy_demand_index, energy_demand = self.report_energy_demand()
        facility_configuration = self.report_facility_configuration()
        power_generation = self.report_power_generation()
        emissions = self.report_emissions()
        p2h = self.report_p2h()
        # p2h_extended_index, p2h_extended = self.report_p2h_extended()
        # p2g = self.report_p2g()
        # p2g_extended = self.report_p2g_extended()

        df1 = pd.DataFrame(rep, index=index)
        df2 = pd.DataFrame(rep_h, index=index)
        df3 = pd.DataFrame(rep_g, index=index)
        df4 = pd.DataFrame(new_invest, index=scalar_index)
        df5 = pd.DataFrame(rep_annual, index=scalar_index)
        df6 = pd.DataFrame(rep_ind_h, index=index)
        df7 = pd.DataFrame(rep_economic, index=scalar_index)
        # df8 = pd.DataFrame(energy_demand, index=energy_demand_index)
        df9 = pd.DataFrame(facility_configuration, index=scalar_index)
        df10 = pd.DataFrame(power_generation, index=scalar_index)
        df11 = pd.DataFrame(emissions, index=scalar_index)
        # df12 = pd.DataFrame(p2h, index=year_index)
        # df13 = pd.DataFrame(p2h_extended, index=p2h_extended_index)
        # df14 = pd.DataFrame(p2g, index=year_index)
        # df15 = pd.DataFrame(p2g_extended, index=year_index)

        writer = pd.ExcelWriter(self.result_xlsx, engine='xlsxwriter')

        df1.to_excel(writer, sheet_name='rep')
        df2.to_excel(writer, sheet_name='rep_h')
        df3.to_excel(writer, sheet_name='rep_g')
        df4.to_excel(writer, sheet_name='new_invest')
        df5.to_excel(writer, sheet_name='rep_annual')
        df6.to_excel(writer, sheet_name='rep_ind_h')
        df7.to_excel(writer, sheet_name='rep_economic')
        # df8.to_excel(writer, sheet_name='에너지수요')
        df9.to_excel(writer, sheet_name='설비구성')
        df10.to_excel(writer, sheet_name='발전량')
        df11.to_excel(writer, sheet_name='배출량')
        # df12.to_excel(writer, sheet_name='P2H')
        # df13.to_excel(writer, sheet_name='P2H_EXT')
        # df14.to_excel(writer, sheet_name='P2G')
        # df15.to_excel(writer, sheet_name='P2G_EXT')

        # Merge Cell
        # workbook = writer.book
        # worksheet = writer.sheets['P2H']
        # merge_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 2})
        # worksheet.merge_range('B1:C1', 'F2H', merge_format)
        # worksheet.merge_range('D1:E1', 'P2H', merge_format)

        # worksheet = writer.sheets['P2H_EXT']
        # merge_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 2})
        # worksheet.merge_range('B1:C1', '가정', merge_format)
        # worksheet.merge_range('D1:E1', '상업', merge_format)

        # worksheet = writer.sheets['P2G']
        # merge_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 2})
        # worksheet.merge_range('B1:E1', '부문별 수소 수요', merge_format)

        # worksheet = writer.sheets['P2G_EXT']
        # merge_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 2})
        # worksheet.merge_range('B1:D1', '주요 지표', merge_format)

        writer.save()
        self._logger.print_info_line("Reporting Excel Data Complete")

        with open(self.result_json, 'w') as f:
            json.dump(self._graph_data, f)

        self._logger.print_info_line("Reporting Json Data Complete")

    def report_rep(self, instance):
        rep = dict()
        graph_data = dict()

        sum_el_demand = 0
        sum_nuke = 0
        sum_pv = 0
        sum_wt = 0
        sum_other = 0
        sum_pp = 0
        sum_chp = 0
        sum_fcell = 0
        sum_ng_pp = 0
        sum_coal_pp = 0
        sum_battery_out = 0
        sum_pumped_out = 0
        sum_p2h = 0
        sum_battery_in = 0
        sum_pumped_in = 0
        sum_e_boiler = 0
        sum_dh_boiler = 0
        sum_ev = 0
        sum_electrolysis = 0
        sum_curtail = 0
        sum_pumped_soc = 0
        sum_battery_soc = 0
        sum_lng = 0
        sum_coal_consumption = 0
        sum_ng_consumption = 0

        for key in self.result_sets['representation']:
            rep[key] = list()
            graph_data[key] = dict()

        for t in range(1, self.t + 1):
            el_demand = value(instance.hourly_demand[t]
                              + value(instance.el_h_new) * 1000000 * (1 - value(instance.smart_share)) * instance.h_H_demand[t]
                              - value(instance.el_h_old) * 1000000 * value(instance.smart_share) * instance.h_H_demand[t])

            rep['el_demand'].append(el_demand)
            graph_data['el_demand'][t] = el_demand
            sum_el_demand += el_demand

            rep['Nuke'].append(value(instance.nuke_P[t]))
            graph_data['Nuke'][t] = value(instance.nuke_P[t])
            sum_nuke += value(instance.nuke_P[t])

            pv = value(instance.h_solar[t] * (instance.specs[('PV', 'cap')] + instance.New['PV']))
            graph_data['PV'][t] = pv
            rep['PV'].append(pv)
            sum_pv += pv

            wt = value(instance.h_wind[t] * (instance.specs[('Wind_on', 'cap')] + instance.New['Wind_on'])
                       + instance.offshore[t] * (instance.specs[('Wind_off', 'cap')] + instance.New['Wind_off']))
            rep['WT'].append(wt)
            graph_data['WT'][t] = wt
            sum_wt += wt

            other = value(instance.elp[(t, 'Waste')] + instance.Distributions[(t, 'ocean')]
                          + instance.Distributions[(t, 'river')])
            rep['other'].append(other)
            graph_data['other'][t] = other
            sum_other += other

            rep['PP'].append(value(instance.elp[(t, 'PP')]))
            graph_data['PP'][t] = value(instance.elp[(t, 'PP')])
            sum_pp += value(instance.elp[(t, 'PP')])

            rep['CHP'].append(value(instance.elp[(t, 'CHP')]))
            graph_data['CHP'][t] = value(instance.elp[(t, 'CHP')])
            sum_chp += value(instance.elp[(t, 'CHP')])

            rep['Fcell'].append(value(instance.elp[(t, 'Fcell')]))
            graph_data['Fcell'][t] = value(instance.elp[(t, 'Fcell')])
            sum_fcell += value(instance.elp[(t, 'Fcell')])

            ng_pp = value(sum([instance.elp[(t, P_FN)] for P_FN in instance.P_FN]))
            rep['NG_PP'].append(ng_pp)
            graph_data['NG_PP'][t] = ng_pp
            sum_ng_pp += ng_pp

            coal_pp = value(sum([instance.elp[(t, P_FC)] for P_FC in instance.P_FC]))
            rep['coal_PP'].append(coal_pp)
            graph_data['coal_PP'][t] = coal_pp
            sum_coal_pp += coal_pp

            rep['battery_out'].append(value(instance.elp[(t, 'b_interface')]))
            graph_data['battery_out'][t] = value(instance.elp[(t, 'b_interface')])
            sum_battery_out += value(instance.elp[(t, 'b_interface')])

            rep['pumped_out'].append(value(instance.elp[(t, 'pumped')]))
            graph_data['pumped_out'][t] = value(instance.elp[(t, 'pumped')])
            sum_pumped_out += value(instance.elp[(t, 'pumped')])

            p2h = value(instance.eld[(t, 'DH_HP')] + instance.E_H_ind[t])
            rep['P2H'].append(p2h)
            graph_data['P2H'][t] = p2h
            sum_p2h += p2h

            rep['battery_in'].append(value(instance.eld[(t, 'b_interface')]))
            graph_data['battery_in'][t] = value(instance.eld[(t, 'b_interface')])
            sum_battery_in += value(instance.eld[(t, 'b_interface')])

            rep['pumped_in'].append(value(instance.eld[(t, 'pumped')]))
            graph_data['pumped_in'][t] = value(instance.eld[(t, 'pumped')])
            sum_pumped_in += value(instance.eld[(t, 'pumped')])

            rep['E_boiler'].append(value(instance.eld[(t, 'E_boiler')]))
            graph_data['E_boiler'][t] = value(instance.eld[(t, 'E_boiler')])
            sum_e_boiler += value(instance.eld[(t, 'E_boiler')])

            rep['DH_Boiler'].append(value(instance.eld[(t, 'DH_Boiler')]))
            graph_data['DH_Boiler'][t] = value(instance.eld[(t, 'DH_Boiler')])
            sum_dh_boiler += value(instance.eld[(t, 'DH_Boiler')])

            ev = value(instance.eld[(t, 'EV')] + instance.el_flexible_bus[t])
            rep['EV'].append(ev)
            graph_data['EV'][t] = ev
            sum_ev += ev

            rep['electrolysis'].append(value(instance.eld[(t, 'electrolysis')]))
            graph_data['electrolysis'][t] = value(instance.eld[(t, 'electrolysis')])
            sum_electrolysis += value(instance.eld[(t, 'electrolysis')])

            rep['curtail'].append(value(instance.curtail[t]))
            graph_data['curtail'][t] = value(instance.curtail[t])
            sum_curtail += value(instance.curtail[t])

            rep['pumped_soc'].append(value(instance.SOC[t]))
            graph_data['pumped_soc'][t] = value(instance.SOC[t])
            sum_pumped_soc += value(instance.SOC[t])

            rep['battery_soc'].append(value(instance.SOC_battery[t]))
            graph_data['battery_soc'][t] = value(instance.SOC_battery[t])
            sum_battery_soc += value(instance.SOC_battery[t])

            if t == 1:
                LNG = value(sum([instance.LNG[(t, tech)] for t in instance.t for tech in instance.tech]))
                sum_lng = LNG
                graph_data['LNG'][1] = LNG
            else:
                LNG = ""

            rep['LNG'].append(LNG)

            coal_consumption = value(sum([instance.coal[(t, P_FC)] for P_FC in instance.P_FC]))
            rep['coal_consumption'].append(coal_consumption)
            graph_data['coal_consumption'][t] = coal_consumption
            sum_coal_consumption += coal_consumption

            ng_consumption = value(sum([instance.LNG[(t, P_FN)] for P_FN in instance.P_FN]))
            rep['NG_consumption'].append(ng_consumption)
            graph_data['NG_consumption'][t] = ng_consumption
            sum_ng_consumption += ng_consumption

        rep['el_demand'].append(sum_el_demand)
        rep['Nuke'].append(sum_nuke)
        rep['PV'].append(sum_pv)
        rep['WT'].append(sum_wt)
        rep['other'].append(sum_other)
        rep['PP'].append(sum_pp)
        rep['CHP'].append(sum_chp)
        rep['Fcell'].append(sum_fcell)
        rep['NG_PP'].append(sum_ng_pp)
        rep['coal_PP'].append(sum_coal_pp)
        rep['battery_out'].append(sum_battery_out)
        rep['pumped_out'].append(sum_pumped_out)
        rep['P2H'].append(sum_p2h)
        rep['battery_in'].append(sum_battery_in)
        rep['pumped_in'].append(sum_pumped_in)
        rep['E_boiler'].append(sum_e_boiler)
        rep['DH_Boiler'].append(sum_dh_boiler)
        rep['EV'].append(sum_ev)
        rep['electrolysis'].append(sum_electrolysis)
        rep['curtail'].append(sum_curtail)
        rep['pumped_soc'].append(sum_pumped_soc)
        rep['battery_soc'].append(sum_battery_soc)
        rep['LNG'].append(sum_lng)
        rep['coal_consumption'].append(sum_coal_consumption)
        rep['NG_consumption'].append(sum_ng_consumption)

        graph_data['el_demand']['total'] = sum_el_demand
        graph_data['Nuke']['total'] = sum_nuke
        graph_data['PV']['total'] = sum_pv
        graph_data['WT']['total'] = sum_wt
        graph_data['other']['total'] = sum_other
        graph_data['PP']['total'] = sum_pp
        graph_data['CHP']['total'] = sum_chp
        graph_data['Fcell']['total'] = sum_fcell
        graph_data['NG_PP']['total'] = sum_ng_pp
        graph_data['coal_PP']['total'] = sum_coal_pp
        graph_data['battery_out']['total'] = sum_battery_out
        graph_data['pumped_out']['total'] = sum_pumped_out
        graph_data['P2H']['total'] = sum_p2h
        graph_data['battery_in']['total'] = sum_battery_in
        graph_data['pumped_in']['total'] = sum_pumped_in
        graph_data['E_boiler']['total'] = sum_e_boiler
        graph_data['DH_Boiler']['total'] = sum_dh_boiler
        graph_data['EV']['total'] = sum_ev
        graph_data['electrolysis']['total'] = sum_electrolysis
        graph_data['curtail']['total'] = sum_curtail
        graph_data['pumped_soc']['total'] = sum_pumped_soc
        graph_data['battery_soc']['total'] = sum_battery_soc
        graph_data['LNG']['total'] = sum_lng
        graph_data['coal_consumption']['total'] = sum_coal_consumption
        graph_data['NG_consumption']['total'] = sum_ng_consumption

        self._graph_data['rep'] = graph_data

        return rep

    def report_rep_h(self, instance):
        rep_h = dict()
        graph_data = dict()

        for key in self.result_sets['H_representation']:
            rep_h[key] = list()
            graph_data[key] = dict()

        sum_heat_demand = 0
        sum_chp_h = 0
        sum_fcell_h = 0
        sum_dh_hp_h = 0
        sum_dh_boiler = 0
        sum_e_boiler_h = 0
        sum_soc_th = 0
        sum_dis_th = 0
        sum_ch_th = 0

        for t in range(1, self.t + 1):
            rep_h['heat_demand'].append(value(instance.hourly_heat[t]))
            graph_data['heat_demand'][t] = value(instance.hourly_heat[t])
            sum_heat_demand += value(instance.hourly_heat[t])

            rep_h['CHP_h'].append(value(instance.heatP[(t, 'CHP')]))
            graph_data['CHP_h'][t] = value(instance.heatP[(t, 'CHP')])
            sum_chp_h += value(instance.heatP[(t, 'CHP')])

            rep_h['Fcell_h'].append(value(instance.heatP[(t, 'Fcell')]))
            graph_data['Fcell_h'][t] = value(instance.heatP[(t, 'Fcell')])
            sum_fcell_h += value(instance.heatP[(t, 'Fcell')])

            rep_h['DH_HP_h'].append(value(instance.heatP[(t, 'DH_HP')]))
            graph_data['DH_HP_h'][t] = value(instance.heatP[(t, 'DH_HP')])
            sum_dh_hp_h += value(instance.heatP[(t, 'DH_HP')])

            rep_h['DH_Boiler'].append(value(instance.heatP[(t, 'DH_Boiler')]))
            graph_data['DH_Boiler'][t] = value(instance.heatP[(t, 'DH_Boiler')])
            sum_dh_boiler += value(instance.heatP[(t, 'DH_Boiler')])

            rep_h['E_boiler_h'].append(value(instance.heatP[(t, 'E_boiler')]))
            graph_data['E_boiler_h'][t] = value(instance.heatP[(t, 'E_boiler')])
            sum_e_boiler_h += value(instance.heatP[(t, 'E_boiler')])

            rep_h['SOC_th'].append(value(instance.SOC_th[t]))
            graph_data['SOC_th'][t] = value(instance.SOC_th[t])
            sum_soc_th += value(instance.SOC_th[t])

            rep_h['dis_th'].append(value(instance.dis_th[t]))
            graph_data['dis_th'][t] = value(instance.dis_th[t])
            sum_dis_th += value(instance.dis_th[t])

            rep_h['ch_th'].append(value(instance.ch_th[t]))
            graph_data['ch_th'][t] = value(instance.ch_th[t])
            sum_ch_th += value(instance.ch_th[t])

        rep_h['heat_demand'].append(sum_heat_demand)
        rep_h['CHP_h'].append(sum_chp_h)
        rep_h['Fcell_h'].append(sum_fcell_h)
        rep_h['DH_HP_h'].append(sum_dh_hp_h)
        rep_h['DH_Boiler'].append(sum_dh_boiler)
        rep_h['E_boiler_h'].append(sum_e_boiler_h)
        rep_h['SOC_th'].append(sum_soc_th)
        rep_h['dis_th'].append(sum_dis_th)
        rep_h['ch_th'].append(sum_ch_th)

        graph_data['heat_demand']['total'] = sum_heat_demand
        graph_data['CHP_h']['total'] = sum_chp_h
        graph_data['Fcell_h']['total'] = sum_fcell_h
        graph_data['DH_HP_h']['total'] = sum_dh_hp_h
        graph_data['DH_Boiler']['total'] = sum_dh_boiler
        graph_data['E_boiler_h']['total'] = sum_e_boiler_h
        graph_data['SOC_th']['total'] = sum_soc_th
        graph_data['dis_th']['total'] = sum_dis_th
        graph_data['ch_th']['total'] = sum_ch_th

        self._graph_data['rep_h'] = graph_data

        return rep_h

    def report_rep_g(self, instance):
        rep_g = dict()
        graph_data = dict()

        for key in self.result_sets['G_representation']:
            rep_g[key] = list()
            graph_data[key] = dict()

        sum_gas_demand = 0
        sum_gas_production = 0
        sum_chp = 0
        sum_fcell = 0
        sum_pp = 0
        sum_gas_charging = 0
        sum_gas_discharging = 0
        sum_gas_soc = 0
        sum_lng_consumption = 0

        for t in range(1, self.t + 1):
            if self.year < 2035:
                gas_demand = value(instance.industry_gas[t] + sum([instance.gas[(t, gas_all)] for gas_all in instance.gas_all]))
            elif self.year > 2034:
                gas_demand = value(instance.industry_gas[t] + sum([instance.gas[(t, gas_all)] for gas_all in instance.gas_all]))
            else:
                raise ValueError('Wrong year')

            rep_g['gas_demand'].append(gas_demand)
            graph_data['gas_demand'][t] = gas_demand
            sum_gas_demand += gas_demand

            rep_g['gas_production'].append(value(instance.gasP[t]))
            graph_data['gas_production'][t] = value(instance.gasP[t])
            sum_gas_production += value(instance.gasP[t])

            rep_g['CHP'].append(value(instance.gas[(t, 'CHP')]))
            graph_data['CHP'][t] = value(instance.gas[(t, 'CHP')])
            sum_chp += value(instance.gas[(t, 'CHP')])

            rep_g['Fcell'].append(value(instance.gas[(t, 'Fcell')]))
            graph_data['Fcell'][t] = value(instance.gas[(t, 'Fcell')])
            sum_fcell += value(instance.gas[(t, 'Fcell')])

            rep_g['PP'].append(value(instance.gas[(t, 'PP')]))
            graph_data['PP'][t] = value(instance.gas[(t, 'PP')])
            sum_pp += value(instance.gas[(t, 'PP')])

            rep_g['gas_charging'].append(value(instance.ch_gas[t]))
            graph_data['gas_charging'][t] = value(instance.ch_gas[t])
            sum_gas_charging += value(instance.ch_gas[t])

            rep_g['gas_discharging'].append(value(instance.dis_gas[t]))
            graph_data['gas_discharging'][t] = value(instance.dis_gas[t])
            sum_gas_discharging += value(instance.dis_gas[t])

            rep_g['gas_SOC'].append(value(instance.SOC_gas[t]))
            graph_data['gas_SOC'][t] = value(instance.SOC_gas[t])
            sum_gas_soc += value(instance.SOC_gas[t])

            lng_consumption = value(sum([instance.LNG[(t, tech)] for tech in instance.tech]))
            rep_g['LNG_consumption'].append(lng_consumption)
            graph_data['LNG_consumption'][t] = lng_consumption
            sum_lng_consumption += lng_consumption

        rep_g['gas_demand'].append(sum_gas_demand)
        rep_g['gas_production'].append(sum_gas_production)
        rep_g['CHP'].append(sum_chp)
        rep_g['Fcell'].append(sum_fcell)
        rep_g['PP'].append(sum_pp)
        rep_g['gas_charging'].append(sum_gas_charging)
        rep_g['gas_discharging'].append(sum_gas_discharging)
        rep_g['gas_SOC'].append(sum_gas_soc)
        rep_g['LNG_consumption'].append(sum_lng_consumption)

        graph_data['gas_demand']['total'] = sum_gas_demand
        graph_data['gas_production']['total'] = sum_gas_production
        graph_data['CHP']['total'] = sum_chp
        graph_data['Fcell']['total'] = sum_fcell
        graph_data['PP']['total'] = sum_pp
        graph_data['gas_charging']['total'] = sum_gas_charging
        graph_data['gas_discharging']['total'] = sum_gas_discharging
        graph_data['gas_SOC']['total'] = sum_gas_soc
        graph_data['LNG_consumption']['total'] = sum_lng_consumption

        self._graph_data['rep_g'] = graph_data

        return rep_g

    def report_new_invest(self, instance):
        new_invest = dict()

        for expand in instance.expand:
            new_invest[expand] = value(instance.New[expand])

        self._graph_data['new_invest'] = new_invest

        return new_invest

    def report_rep_annual(self, instance):
        rep_annual = dict()

        rep_annual['em_power'] = value(instance.em)
        rep_annual['em_heat_r'] = value(instance.em_heat_r)
        rep_annual['em_heat_c'] = value(instance.em_heat_c)
        rep_annual['em_tr'] = value(instance.em_tr)
        rep_annual['em_ind'] = value(instance.em_ind)
        rep_annual['curtailment'] = value(sum([instance.curtail[t] for t in instance.t]))

        RE_sharp_p = (sum([instance.h_wind[t] * (instance.New['Wind_on'] + instance.specs[('Wind_on', 'cap')])
                           + instance.offshore[t] * (instance.New['Wind_off'] + instance.specs[('Wind_off', 'cap')])
                           + instance.h_solar[t] * (instance.New['PV'] * instance.specs[('PV', 'cap')])
                           + instance.Distributions[(t, 'ocean')]
                           + instance.Distributions[(t, 'river')]
                           for t in instance.t])
                      - (sum([instance.curtail[t] for t in instance.t]) / sum([instance.hourly_demand[t] for t in instance.t])))
        rep_annual['RE_share_p'] = value(RE_sharp_p)

        self._graph_data['rep_annual'] = {
            'em_power': value(instance.em),
            'em_heat_r': value(instance.em_heat_r),
            'em_heat_c': value(instance.em_heat_c),
            'em_tr': value(instance.em_tr),
            'em_ind': value(instance.em_ind)
        }

        return rep_annual

    def report_rep_ind_h(self, instance):
        rep_ind_h = dict()
        graph_data = dict()

        for key in self.result_sets['ind_h']:
            rep_ind_h[key] = list()
            graph_data[key] = dict()

        sum_soc_ind = 0
        sum_dis_ind = 0
        sum_charge_ind = 0
        sum_e_heat_sm = 0
        sum_el_demand_ind_h = 0

        for t in range(1, self.t + 1):
            rep_ind_h['SOC_ind'].append(value(instance.SOC_ind_th[t]))
            graph_data['SOC_ind'][t] = value(instance.SOC_ind_th[t])
            sum_soc_ind += value(instance.SOC_ind_th[t])

            rep_ind_h['dis_ind'].append(value(instance.dis_ind_h[t]))
            graph_data['dis_ind'][t] = value(instance.dis_ind_h[t])
            sum_dis_ind += value(instance.dis_ind_h[t])

            rep_ind_h['charge_ind'].append(value(instance.charge_ind_h[t]))
            graph_data['charge_ind'][t] = value(instance.charge_ind_h[t])
            sum_charge_ind += value(instance.charge_ind_h[t])

            rep_ind_h['E_heat_sm'].append(value(instance.E_heat_smart[t]))
            graph_data['E_heat_sm'][t] = value(instance.E_heat_smart[t])
            sum_e_heat_sm += value(instance.E_heat_smart[t])

            rep_ind_h['EL_demand_ind_h'].append(value(instance.E_H_ind[t]))
            graph_data['EL_demand_ind_h'][t] = value(instance.E_H_ind[t])
            sum_el_demand_ind_h += value(instance.E_H_ind[t])

        rep_ind_h['SOC_ind'].append(sum_soc_ind)
        rep_ind_h['dis_ind'].append(sum_dis_ind)
        rep_ind_h['charge_ind'].append(sum_charge_ind)
        rep_ind_h['E_heat_sm'].append(sum_e_heat_sm)
        rep_ind_h['EL_demand_ind_h'].append(sum_el_demand_ind_h)

        graph_data['SOC_ind']['total'] = sum_soc_ind
        graph_data['dis_ind']['total'] = sum_dis_ind
        graph_data['charge_ind']['total'] = sum_charge_ind
        graph_data['E_heat_sm']['total'] = sum_e_heat_sm
        graph_data['EL_demand_ind_h']['total'] = sum_el_demand_ind_h

        self._graph_data['rep_ind_h'] = graph_data

        return rep_ind_h

    def report_rep_economic(self, instance):
        rep_economic = dict()

        investment = (
                sum([instance.New[expand] * instance.annuity[expand] for expand in instance.expand])
                + sum([instance.specs[(f_tech, 'cap')] * instance.annuity[f_tech] for f_tech in instance.f_tech])
                + sum([instance.Cspec_iter[(P_FC, 'i_cap')] * value(instance.annuity_coal) for P_FC in instance.P_FC])
                + sum([instance.NGspec[(P_FN, 'i_cap')] * value(instance.annuity_NG) for P_FN in instance.P_FN])
        )
        rep_economic['investment'] = value(investment)

        fixed_operation = (
                sum([instance.New[expand] * (instance.annuity[expand] + instance.cost[(expand, 'fixed_OM')]) for expand in instance.expand])
                + sum([instance.specs[(tech, 'cap')] * instance.cost[(tech, 'fixed_OM')] for tech in instance.tech])
                + sum([instance.Cspec_iter[(P_FC, 'i_cap')] * value(instance.fx_coal) for P_FC in instance.P_FC])
                + sum([instance.NGspec[(P_FN, 'i_cap')] * value(instance.fx_NG) for P_FN in instance.P_FN]))
        rep_economic['fixed_operation'] = value(fixed_operation)

        v_operation = (
                sum([instance.h_wind[t] * (instance.New['Wind_on'] + instance.specs[('Wind_on', 'cap')]) * instance.cost[('Wind_on', 'variable_OM')] for t in instance.t])
                + sum([instance.offshore[t] * (instance.New['Wind_off'] + instance.specs[('Wind_off', 'cap')]) * instance.cost[('Wind_off', 'variable_OM')] for t in instance.t])
                + sum([instance.h_solar[t] * (instance.New['PV'] + instance.specs[('PV', 'cap')]) * instance.cost[('PV', 'variable_OM')] for t in instance.t])
                + sum([instance.elp[(t, power)] * instance.cost[(power, 'variable_OM')] for t in instance.t for power in instance.power])
                + sum([instance.eld[(t, 'DH_HP')] * instance.cost[('DH_HP', 'variable_OM')] for t in instance.t])
                + sum([instance.dis_gas[t] * instance.cost[('GS_interface', 'variable_OM')] for t in instance.t])
                + sum([instance.eld[(t, 'electrolysis')] * instance.cost[('pumped', 'variable_OM')] for t in instance.t])
                + sum([instance.eld[(t, 'pumped')] * instance.cost[('pumped', 'variable_OM')] for t in instance.t])
                + sum([instance.elp[(t, P_FC)] * value(instance.va_coal) for t in instance.t for P_FC in instance.P_FC])
                + sum([instance.elp[(t, P_FN)] * value(instance.va_NG) for t in instance.t for P_FN in instance.P_FN])
        )
        rep_economic['v_operation'] = value(v_operation)

        fuel = (
            sum([instance.LNG[(t, tech)] * instance.fossil[('NG', 'price')] for t in instance.t for tech in instance.tech])
            + sum([instance.coal[(t, P_FC)] * instance.fossil[('coal', 'price')] for t in instance.t for P_FC in instance.P_FC])
        )
        rep_economic['fuel'] = value(fuel)

        em_cost = value(instance.em) * instance.fossil[('emission', 'price')]
        rep_economic['em_cost'] = value(em_cost)

        self._graph_data['rep_economic'] = rep_economic

        return rep_economic

    # def report_energy_demand(self):
        # energy_demand_index = ['coal', 'oil', 'LNG', 'electricity', 'heat', 'hydrogen', 'other', 'total']

        # energy_demand = {
            # '계': [],
            # '산업': [],
            # '건물': [],
            # '수송': []
        # }

        # sum_industry = 0

        # if self.year < 2035:
            # for i in range(7):
                # industry_value = self._data['industry_demand'].iloc[i][2030]

                # energy_demand['산업'].append(industry_value)
                # sum_industry += industry_value

            # building_coal = (
                    # self._data['residential_heat'].iloc[53][8]
                    # + self._data['commercial_public_heat'].iloc[51][3]
            # )

            # building_oil = (
                    # self._data['residential_heat'].iloc[51][8]
                    # + self._data['residential_heat'].iloc[52][8]
                    # + self._data['commercial_public_heat'].iloc[52][3]
            # )

            # building_lng = (
                # self._data['residential_heat'].iloc[50][8]
                # + self._data['commercial_public_heat'].iloc[59][3]
            # )

            # building_electricity = (
                    # self._data['residential_heat'].iloc[7][11]
                    # + self._data['residential_heat'].iloc[71][8]
                    # + self._data['commercial_public_heat'].iloc[11][13]
                    # + self._data['commercial_public_heat'].iloc[91][3]
                    # - self._data['commercial_public_heat'].iloc[91][1]
            # )

            # building_heat = (
                    # self._data['residential_heat'].iloc[74][8]
                    # + self._data['residential_heat'].iloc[73][8]
                    # + self._data['commercial_public_heat'].iloc[89][3]
            # )

            # building_hydrogen = 0

            # building_other = (
                    # self._data['residential_heat'].iloc[54][8]
                    # + self._data['commercial_public_heat'].iloc[60][3]
            # )

            # transportation_coal = 0
            # transportation_oil = self._data['transportation_extended'].iloc[32][38]
            # transportation_lng = 0
            # transportation_electricity = self._data['transportation_extended'].iloc[30][38]
            # transportation_heat = 0
            # transportation_hydrogen = self._data['transportation_extended'].iloc[31][38]
            # transportation_other = 0

        # elif self.year > 2034:
            # for i in range(7):
                # industry_value = self._data['industry_demand'].iloc[i][2050]

                # energy_demand['산업'].append(industry_value)
                # sum_industry += industry_value

            # building_coal = (
                    # self._data['residential_heat'].iloc[53][12]
                    # + self._data['commercial_public_heat'].iloc[51][7]
            # )

            # building_oil = (
                    # self._data['residential_heat'].iloc[51][12]
                    # + self._data['residential_heat'].iloc[52][12]
                    # + self._data['commercial_public_heat'].iloc[52][7]
            # )

            # building_lng = (
                    # self._data['residential_heat'].iloc[50][12]
                    # + self._data['commercial_public_heat'].iloc[59][7]
            # )

            # building_electricity = (
                    # self._data['residential_heat'].iloc[7][11]
                    # + self._data['residential_heat'].iloc[71][12]
                    # + self._data['commercial_public_heat'].iloc[11][13]
                    # + self._data['commercial_public_heat'].iloc[91][7]
                    # - self._data['commercial_public_heat'].iloc[91][1]
            # )

            # building_heat = (
                    # self._data['residential_heat'].iloc[74][12]
                    # + self._data['residential_heat'].iloc[73][12]
                    # + self._data['commercial_public_heat'].iloc[89][7]
            # )

            # building_hydrogen = 0

            # building_other = (
                    # self._data['residential_heat'].iloc[54][12]
                    # + self._data['commercial_public_heat'].iloc[60][7]
            # )

            # transportation_coal = 0
            # transportation_oil = self._data['transportation_extended'].iloc[32][42]
            # transportation_lng = 0
            # transportation_electricity = self._data['transportation_extended'].iloc[30][42]
            # transportation_heat = 0
            # transportation_hydrogen = self._data['transportation_extended'].iloc[31][42]
            # transportation_other = 0

        # else:
            # raise ValueError('Wrong year')

        # energy_demand['산업'].append(sum_industry)

        # energy_demand['건물'].append(building_coal)
        # energy_demand['건물'].append(building_oil)
        # energy_demand['건물'].append(building_lng)
        # energy_demand['건물'].append(building_electricity)
        # energy_demand['건물'].append(building_heat)
        # energy_demand['건물'].append(building_hydrogen)
        # energy_demand['건물'].append(building_other)
        # energy_demand['건물'].append(building_coal + building_oil + building_lng + building_electricity +
                                   # building_heat + building_hydrogen + building_other)

        # energy_demand['수송'].append(transportation_coal)
        # energy_demand['수송'].append(transportation_oil)
        # energy_demand['수송'].append(transportation_lng)
        # energy_demand['수송'].append(transportation_electricity)
        # energy_demand['수송'].append(transportation_heat)
        # energy_demand['수송'].append(transportation_hydrogen)
        # energy_demand['수송'].append(transportation_other)
        # energy_demand['수송'].append(transportation_coal + transportation_oil + transportation_lng
                                   # + transportation_electricity + transportation_hydrogen + transportation_hydrogen
                                   # + transportation_other)

        # for i in range(8):
            # energy_demand['계'].append(energy_demand['산업'][i] + energy_demand['건물'][i] + energy_demand['수송'][i])

        # graph_data = dict()

        # for idx, val in enumerate(energy_demand_index):
            # graph_data[val] = {
                # 'industry': energy_demand['산업'][idx],
                # 'building': energy_demand['건물'][idx],
                # 'transportation': energy_demand['수송'][idx],
                # 'total': energy_demand['계'][idx]
            # }

        # self._graph_data['energy_demand'] = graph_data

        # return energy_demand_index, energy_demand

    def report_facility_configuration(self):
        ng_pp = 44404
        pumped = 6700

        if self.year < 2035:
            coal_pp = 18991
            nuke = 21129
        elif self.year > 2034:
            coal_pp = 0
            nuke = 8000
        else:
            raise ValueError('Wrong year')

        facility_configuration = {
            'Wind_on': self._data['specs_extended'].loc['Wind_on'][2025] + self._graph_data['new_invest']['Wind_on'],
            'Wind_off': self._data['specs_extended'].loc['Wind_off'][2025] + self._graph_data['new_invest']['Wind_off'],
            'PV': self._data['specs_extended'].loc['PV'][2025] + self._graph_data['new_invest']['PV'],
            'CHP': self._data['specs_extended'].loc['CHP'][2025] + self._graph_data['new_invest']['CHP'],
            'Fcell': self._graph_data['new_invest']['Fcell'],
            'NG_PP(new)': self._graph_data['new_invest']['PP'],
            'NG_PP(existing)': ng_pp,
            'coal_PP': coal_pp,
            # 'Nuke': self._data['specs_extended'].loc['Nuke']['Final'] + self._graph_data['new_invest']['Nuke'],
            'Nuke': nuke,
            'DH_HP': self._graph_data['new_invest']['DH_HP'],
            'DH_boiler': self._graph_data['new_invest']['DH_Boiler'],
            'Electronic boiler': self._graph_data['new_invest']['E_boiler'],
            'Electrolysis': self._graph_data['new_invest']['electrolysis'],
            'Gas_interface': self._graph_data['new_invest']['GS_interface'],
            'b_interface': self._graph_data['new_invest']['b_interface'],
            # 'pumped': self._data['specs_extended'].loc['pumped']['Final'] + self._graph_data['new_invest']['pumped'],
            'pumped': pumped,
            'TES_DH': self._graph_data['new_invest']['TES_DH'],
            'Gas_storage': self._graph_data['new_invest']['Gas_storage'],
            'Battery': self._graph_data['new_invest']['battery']
        }

        self._graph_data['facility_configuration'] = facility_configuration

        return facility_configuration

    def report_power_generation(self):
        power_generation = {
            'WT': self._graph_data['rep']['WT']['total'] / 1000000,
            'PV': self._graph_data['rep']['PV']['total'] / 1000000,
            'CHP': self._graph_data['rep']['CHP']['total'] / 1000000,
            'Fcell': self._graph_data['rep']['Fcell']['total'] / 1000000,
            'NG_PP(new)': self._graph_data['rep']['PP']['total'] / 1000000,
            'NG_PP(existing)': self._graph_data['rep']['NG_PP']['total'] / 1000000,
            'coal_PP': self._graph_data['rep']['coal_PP']['total'] / 1000000,
            'Nuke': self._graph_data['rep']['Nuke']['total'] / 1000000,
            'Other': self._graph_data['rep']['other']['total'] / 1000000,
            'Electrolysis': self._graph_data['rep']['electrolysis']['total'] / 1000000,
            'Electric boiler': self._graph_data['rep']['E_boiler']['total'] / 1000000,
            'EV': self._graph_data['rep']['EV']['total'] / 1000000,
            'Electricity demand': self._graph_data['rep']['el_demand']['total'] / 1000000,
            'P2H': self._graph_data['rep']['P2H']['total'] / 1000000,
            'Curtailment': self._graph_data['rep']['curtail']['total'] / 1000000,
        }

        self._graph_data['power_generation'] = power_generation

        return power_generation

    def report_emissions(self):
        emissions = {
            'em_power': self._graph_data['rep_annual']['em_power'],
            'em_ind': self._graph_data['rep_annual']['em_ind'],
            '건물': self._graph_data['rep_annual']['em_heat_r'] + self._graph_data['rep_annual']['em_heat_c'],
            'em_tr': self._graph_data['rep_annual']['em_tr'],
            '계': (self._graph_data['rep_annual']['em_power']
                  + self._graph_data['rep_annual']['em_heat_r']
                  + self._graph_data['rep_annual']['em_heat_c']
                  + self._graph_data['rep_annual']['em_tr']
                  + self._graph_data['rep_annual']['em_ind'])
        }

        self._graph_data['emissions'] = {
            'em_power': emissions['em_power'],
            'em_ind': emissions['em_ind'],
            'building': emissions['건물'],
            'em_tr': emissions['em_tr'],
            'total': emissions['계']
        }

        return emissions

    def report_p2h(self):
        p2h = {
            'F2H_fuel': [
                'fuel',
                self._graph_data['rep_h']['DH_Boiler']['total'] + (self._graph_data['rep_h']['CHP_h']['total'] / 0.4)
            ],
            'F2H_heat': [
                'heat',
                self._graph_data['rep_h']['CHP_h']['total'] + self._graph_data['rep_h']['DH_Boiler']['total']
            ],
            'P2H_elec': [
                'elec',
                self._graph_data['rep']['P2H']['total']
            ],
            'P2H_heat': [
                'heat',
                self._graph_data['rep_h']['DH_HP_h']['total'] + (self._graph_data['rep_ind_h']['EL_demand_ind_h']['total'] * 3)
            ]
        }

        self._graph_data['P2H'] = {
            'F2H': {
                'fuel': p2h['F2H_fuel'][1],
                'heat': p2h['F2H_heat'][1],
            },
            'P2H': {
                'elec': p2h['P2H_elec'][1],
                'heat': p2h['P2H_heat'][1]
            }
        }

        return p2h

    # def report_p2h_extended(self):
        # p2h_index = ['year', '지역난방', '도시가스', '석유', '석탄', '전력', '기타']

        # home_2020 = [
                # '2020',
                # self._data['residential_heat'].iloc[21][5],
                # self._data['residential_heat'].iloc[15][5],
                # self._data['residential_heat'].iloc[16][5] + self._data['residential_heat'].iloc[17][5],
                # self._data['residential_heat'].iloc[18][5],
                # self._data['residential_heat'].iloc[73][6],
                # self._data['residential_heat'].iloc[19][5]
            # ]

        # commerce_2020 = [
                # '2020',
                # self._data['commercial_public_heat'].iloc[89][1],
                # self._data['commercial_public_heat'].iloc[59][1],
                # self._data['commercial_public_heat'].iloc[52][1],
                # self._data['commercial_public_heat'].iloc[51][1],
                # self._data['commercial_public_heat'].iloc[91][1],
                # self._data['commercial_public_heat'].iloc[60][1]
            # ]

        # if self.year < 2035:
            # p2h = {
                # '가정_2020': home_2020,
                # f'가정_{self.year}': [
                    # f'{self.year}',
                    # self._data['residential_heat'].iloc[74][8],
                    # self._data['residential_heat'].iloc[50][8],
                    # self._data['residential_heat'].iloc[51][8] + self._data['residential_heat'].iloc[52][8],
                    # self._data['residential_heat'].iloc[53][8],
                    # self._data['residential_heat'].iloc[71][8] + self._data['residential_heat'].iloc[73][8],
                    # self._data['residential_heat'].iloc[54][8]
                # ],
                # '상업_2020': commerce_2020,
                # f'상업_{self.year}': [
                    # f'{self.year}',
                    # self._data['commercial_public_heat'].iloc[89][3],
                    # self._data['commercial_public_heat'].iloc[59][3],
                    # self._data['commercial_public_heat'].iloc[52][3],
                    # self._data['commercial_public_heat'].iloc[51][3],
                    # self._data['commercial_public_heat'].iloc[91][3] + self._data['commercial_public_heat'].iloc[90][3],
                    # self._data['commercial_public_heat'].iloc[60][3]
                # ]
            # }
        # elif self.year > 2034:
            # p2h = {
                # '가정_2020': home_2020,
                # f'가정_{self.year}': [
                    # f'{self.year}',
                    # self._data['residential_heat'].iloc[74][12],
                    # self._data['residential_heat'].iloc[50][12],
                    # self._data['residential_heat'].iloc[51][12] + self._data['residential_heat'].iloc[52][12],
                    # self._data['residential_heat'].iloc[53][12],
                    # self._data['residential_heat'].iloc[71][12] + self._data['residential_heat'].iloc[73][12],
                    # self._data['residential_heat'].iloc[54][12]
                # ],
                # '상업_2020': commerce_2020,
                # f'상업_{self.year}': [
                    # f'{self.year}',
                    # self._data['commercial_public_heat'].iloc[89][7],
                    # self._data['commercial_public_heat'].iloc[59][7],
                    # self._data['commercial_public_heat'].iloc[52][7],
                    # self._data['commercial_public_heat'].iloc[51][7],
                    # self._data['commercial_public_heat'].iloc[91][7] + self._data['commercial_public_heat'].iloc[90][7],
                    # self._data['commercial_public_heat'].iloc[60][7]
                # ]
            # }
        # else:
            # raise ValueError('Wrong year')

        # graph_index = ['district_heating', 'city_gas', 'oil', 'coal', 'electric_heating', 'others']
        # graph_data = {
            # 'home': {
                # '2020': {},
                # f'{self.year}': {}
            # },
            # 'commerce': {
                # '2020': {},
                # f'{self.year}': {}
            # }
        # }

        # for idx, val in enumerate(graph_index):
            # graph_data['home']['2020'][val] = home_2020[idx + 1]
            # graph_data['home'][f'{self.year}'][val] = p2h[f'가정_{self.year}'][idx + 1]
            # graph_data['commerce']['2020'][val] = commerce_2020[idx + 1]
            # graph_data['commerce'][f'{self.year}'][val] = p2h[f'상업_{self.year}'][idx + 1]

        # self._graph_data['P2H_consumption_change'] = graph_data

        # return p2h_index, p2h

    # def report_p2g(self):
        # electricity_generation = self._graph_data['rep_g']['CHP']['total'] / 1000000

        # if self.year < 2035:
            # transportation = self._data['transportation_extended'].iloc[31][38]
            # industrial_material = self._data['industry_demand'].loc['Hydrogen'][2030]

        # elif self.year > 2034:
            # transportation = self._data['transportation_extended'].iloc[31][42]
            # industrial_material = self._data['industry_demand'].loc['Hydrogen'][2050]

        # else:
            # raise ValueError('Wrong year')

        # p2g = {
            # 'col1': [
                # '발전',
                # electricity_generation
            # ],
            # 'col2': [
                # '수송',
                # transportation
            # ],
            # 'col3': [
                # '산업원료',
                # industrial_material
            # ],
            # 'col4': [
                # '계',
                # (electricity_generation
                 # + transportation
                 # + industrial_material)
            # ]
        # }

        # self._graph_data['P2G_hydrogen_demand'] = {
            # 'electricity_generation': electricity_generation,
            # 'transportation': transportation,
            # 'industrial_material': industrial_material,
            # 'total': p2g['col4'][1]
        # }

        # return p2g

    # def report_p2g_extended(self):
        # electricity_consumption = self._graph_data['rep']['electrolysis']['total'] / 1000000
        # production = electricity_consumption * 0.7 / 40
        # storage_capacity = self._graph_data['new_invest']['Gas_storage']

        # p2g = {
            # '전력소비량': [
                # 'TWh',
                # electricity_consumption
            # ],
            # '생산량': [
                # 'MTon',
                # production
            # ],
            # '저장용량': [
                # 'GWh',
                # storage_capacity
            # ]
        # }

        # self._graph_data['P2G_core_indicators'] = {
            # 'electricity_consumption': electricity_consumption,
            # 'production': production,
            # 'storage_capacity': storage_capacity
        # }

        # return p2g