"""
This module contains the default point generator.

It also contains functions to check validity of the configuration setting.
"""

from selector.pool import Configuration, ParamType, Generator


def check_conditionals(s, config_setting):
    """
    Check if conditionals are violated.

    Parameters
    ----------
    s : selector.scenario.Scenario
        AC scenario.
    config_setting : dict
        Configuration setting to be checked.

    Returns
    -------
    list
        List of parameter names to turn off.
    """
    cond_vio = []
    for condition in s.conditionals:
        for cond in s.conditionals[condition]:
            for param in s.parameter:
                if param.name == cond:
                    if cond in config_setting:
                        if config_setting[cond] is not None:
                            if type(s.conditionals[condition][cond][0]) == int:
                                config_setting[cond] = \
                                    int(config_setting[cond])
                            if type(s.conditionals[condition][cond][0]) \
                                    == float:
                                config_setting[cond] = \
                                    float(config_setting[cond])
                            if param.type == ParamType.categorical and \
                                    (config_setting[cond] not in
                                     s.conditionals[condition][cond] and
                                     condition not in cond_vio and
                                     condition in config_setting):
                                cond_vio.append(condition)
                            elif (param.type == ParamType.continuous or
                                    param.type == ParamType.integer) and \
                                    (config_setting[cond] >
                                     s.conditionals[condition][cond][1] or
                                     config_setting[cond] <
                                     s.conditionals[condition][cond][0]) and \
                                    condition not in cond_vio and \
                                    condition in config_setting:
                                cond_vio.append(condition)

    return cond_vio


def check_no_goods(s, config_setting):
    """
    Check if no goods are violated.

    Parameters
    ----------
    s : selector.scenario.Scenario
        AC scenario.
    config_setting : dict
        Configuration setting to be checked.

    Returns
    -------
    bool
        True if no goods are violated, False otherwise.
    """
    check = False
    for ng in s.no_goods:
        params = list(ng.keys())

        if all([i in config_setting for i in params]):
            check = all([ng[i] == config_setting[i] for i in params])
            if check:
                return check

    return check


def default_point(s, identity):
    """
    Generate the default parameter setting in Configuration format.

    Parameters
    ----------
    s : selector.scenario.Scenario
        AC scenario.
    identity : uuid.UUID
        UUID to identify the configuration.

    Returns
    -------
    selector.pool.Configuration
        Default configuration.
    """
    config_setting = {}

    # Generate configuration with default values
    for param in s.parameter:
        config_setting[param.name] = param.default

    # Fill Configuration class with ID and parameter values
    configuration = Configuration(identity, config_setting, Generator.default)

    return configuration
