"""
Set Initialize
"""
from pyomo.core import value


def init_t():
    return range(1, 8761)


def init_m():
    return range(1, 13)


def init_d():
    return range(1, 366)


def init_w():
    return range(1, 53)


def init_s():
    return range(1, 1461)


"""
Param Initialize
"""


def init_day(M, t):
    if t % 24 == 0:
        return t // 24.
    else:
        return t // 24. + 1


def init_week(M, t):
    if t >= 8737:
        return 52.
    elif t % 168 == 0:
        return t // 168.
    else:
        return t // 168. + 1


def init_six(M, t):
    if t % 6 == 0:
        return t // 6.
    else:
        return t // 6. + 1


def init_sum_demand(M):
    return sum(M.Distributions[(t, 'Demand')] for t in M.t)


def init_sum_H_demand(M):
    return sum(M.Distributions[(t, 'H_demand')] for t in M.t)


def init_sum_T_demand(M):
    return sum(M.Distributions[(t, 'T_demand')] for t in M.t)


def init_max_wind(M):
    return max(M.Distributions[(t, 'wind')] for t in M.t)


def init_max_solar(M):
    return max(M.Distributions[(t, 'solar')] for t in M.t)


def init_h_demand(M, t):
    return M.Distributions[(t, 'Demand')] / value(M.sum_demand)


def init_h_H_demand(M, t):
    return M.Distributions[(t, 'H_demand')] / value(M.sum_H_demand)


def init_h_wind(M, t):
    return M.Distributions[(t, 'wind')] / value(M.max_wind)


def init_h_solar(M, t):
    return M.Distributions[(t, 'solar')] / value(M.max_solar)


def init_hourlytr(M, t):
    return M.Distributions[(t, 'T_demand')] / value(M.sum_T_demand)


def init_offshore(M, t):
    return M.h_wind[t] * 1 / (1 - value(M.correction_wind) * (1 - M.h_wind[t]))


def init_A_EV(M):
    return value(M.N_Evs) * value(M.av_distance) / value(M.eff_EV)


def init_ch_cap(M):
    return value(M.c_rate) * value(M.N_Evs) * value(M.bat_cap)


def init_hourly_demand(M, t):
    return value(M.EL) * M.h_demand[t] * 1000000


def init_hourly_heat(M, t):
    return value(M.H) * M.h_H_demand[t] * 1000000


def init_annuity(M, f_tech):
    return value(M.discount) * M.cost[(f_tech, 'invest')] / (1 - (1 + value(M.discount)) ** (-M.cost[(f_tech, 'life')]))


def init_annuity_NG(M):
    return value(M.discount) * value(M.inv_NG) / (1 - (1 + value(M.discount)) ** (- M.life_NG))


def init_annuity_coal(M):
    return value(M.discount) * value(M.inv_coal) / (1 - (1 + value(M.discount)) ** (- M.life_coal))


def init_el_g2v(M, t):
    return value(M.A_EV) * M.hourlytr[t] / 1000.


def init_max_tr_distribution(M):
    return max(M.Distributions[(t, 'T_demand')] for t in M.t)


def init_hourly_capacity_EV(M, t):
    return value(M.ch_cap) * value(M.C_share) * ((1 - value(M.M_share)) + value(M.M_share) * (1 - M.Distributions[(t, 'T_demand')] / value(M.max_tr_distribution)))


def init_nuke_P(M, t):
    return 0.8 * M.specs[('Nuke', 'cap')] * M.Distributions[(t, 'constant')]


def init_industry_gas(M, t):
    return value(M.gas_D) * 1000000. / 8760.


def init_E_heat_fixed(M, t):
    return (value(M.el_h_new) + value(M.el_h_old)) * 1000000 * (1 - value(M.smart_share)) * M.h_H_demand[t] * 3


def init_E_heat_smart(M, t):
    return (value(M.el_h_new) + value(M.el_h_old)) * 1000000 * value(M.smart_share) * M.h_H_demand[t] * 3


def init_Stor_H_ind(M):
    return sum(M.E_heat_smart[t] for t in M.t) * 12. / 8760.
