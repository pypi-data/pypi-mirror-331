"""
cve_evaluator

===========

This module provides functions to calculate the `cvss_score` based on the `cvss_vector` of a `CVE`.

Author:
    Pengfei liu

Date:
    2025-02-25
"""
import math
from typing import Dict, List


def parse_cvss_vector(cvss_vector: str) -> Dict[str, str]:
    """
    This function parses the cvss vector string into a cvss vector dictionary. For example, a vector string
     "AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H" will be converted to a dictionary like {"AV":"N", "AC","L"}.

     Need to handle some exceptions:
     1. CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H : has extra values

    :param cvss_vector: The cvss vector string, e.g. AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H
    :return: a dictionary with key as vector type, and value as vector value e.g. {"AV":"N", "AC","L"}
    """
    # for now, we don't keep the CVSS version
    if (cvss_vector is not None) and (cvss_vector.strip()!=""):
        metrics_parts = cvss_vector.split("/")
        if metrics_parts:
            metrics=metrics_parts[1:]
            metric_dict = {metric.split(":")[0]: metric.split(":")[1] for metric in metrics}
        else:
            error_msg = "The given cvss vector does not contain any metrics!"
            metric_dict={}
    else:
        metric_dict = {}
        error_msg = "The given cvss vector is empty"
    return metric_dict


def vector_str_to_value(vector_val_score_map: dict, vector_val: str, vector_type: str) -> float:
    """
    This function converts a vector string into a severity score (float value). The input vector_val_score_map must
    be tested for validly. We don't want to test it each time when this function is called. If nothing found return 0
    :param vector_val_score_map: A dict with primary key as a vector type, for each vector type, it has a sub dict with
               a key as vector value, value as the matching severity score.
    :param vector_val: The enum value of the vector, each vector type has its own enum value
    :param vector_type: The type of the CVSS vector, e.g. AV->Attack Vector, A->Availability Impact
    :return: A score value between 0 and 1, the higher numbers representing a higher degree of severity
    """
    # this may raise `KeyError` if the input vector type is not supported.
    try: 
        vector = vector_val_score_map[vector_type]
        vector_value = float(vector.get(vector_val,0.0))
    except KeyError:
        print(f"The given cvss vector type {vector_type} is not supported!")
        vector_value = 0
    return vector_value


def check_vector_score_mapping_validity(vector_value_score_map: dict) -> (bool, str):
    """
    This function checks whether a vector value score mapping is valid. The input map must contain all required vector
    types, and each vector type must contain all required vector values for the vector type.
    :param vector_value_score_map: The input vector value score mapping, if a user does not provide one, use the default
    :return: A tuple of result and comments
    """
    expected_vector_types = {"AV": ['N', 'A', 'L', 'P'],
                             "AC": ['L', 'H'],
                             "PR": ['N', 'L', 'H'],
                             "UI": ['N', 'R'],
                             "S": ['U', 'C'],
                             "C": ['H', 'L', 'N'],
                             "I": ['H', 'L', 'N'],
                             "A": ['H', 'L', 'N']}

    actual_vector_types = vector_value_score_map.keys()
    if vector_value_score_map is None:
        return False, "The provided vector_value_score_map is empty"
    else:
        # 1. check the map contains all the required vector type
        missing_vec_type = [vec_type for vec_type in list(expected_vector_types.keys()) if
                            vec_type not in actual_vector_types]
        if missing_vec_type:
            return False, f"Missing required vector type: {missing_vec_type}"
        else:
            # 2. check for each vector type, it contains the required values
            for vec_type in actual_vector_types:
                expected_vec_vals: List[str] = list(expected_vector_types[vec_type])
                missing_vec_val = [vec_val for vec_val in expected_vec_vals if
                                   vec_val not in list(vector_value_score_map[vec_type].keys())]
                if missing_vec_val:
                    return False, f"Vector type {vec_type} is missing required value: {missing_vec_val}"
            return True, "The provided vector_value_score_map is valid"


def get_cvss_score(vector_val_score_map: dict, cvss_vector: str) -> Dict[str, float]:
    """
    This function converts a cvss vector string into a cvss score dictionary. The key is vector type and the value
    is the severity score.
    :param cvss_vector: Input CVSS vector of a cve
    :param vector_val_score_map: A dict with primary key as a vector type, for each vector type, it has a sub dict with
               a key as vector value, value as the matching severity score.
    :return: A dict with key as cvss vector type, and value as the matching severity score value of the vector value.
    """
    # get the vector value dict
    vectors = parse_cvss_vector(cvss_vector)
    # transform the vector value from str to float
    return {
        vec_type: vector_str_to_value(vector_val_score_map, vec_val, vec_type)
        for vec_type, vec_val in vectors.items()
    }


def get_exploit_score_from_vector(vector_val_score_map: dict, cvss_vector: str) -> float:
    """
    This function calculates the exploitability score of a CVSS vector in string form.
    :param cvss_vector: Input CVSS vector of a cve
    :return:
    """
    cvss_score: Dict[str, float] = get_cvss_score(vector_val_score_map, cvss_vector)
    return calculate_exploit_score(cvss_score)


def get_impact_score_from_vector(vector_val_score_map: dict, cvss_vector: str) -> float:
    """
    This function calculates the impact score of a CVSS vector in string form.
    :param cvss_vector: Input CVSS vector of a cve
    :return:
    """
    cvss_score: Dict[str, float] = get_cvss_score(vector_val_score_map, cvss_vector)
    return calculate_impact_score(cvss_score)


def calculate_exploit_score(cvss_score: Dict[str, float]) -> float:
    """
    This function calculates the exploitability score of a CVSS vector in dictionary form.
    :param cvss_score: Input CVSS vector score of a cve in dictionary form.
    :return: The exploitability score of a cve
    """
    av = cvss_score.get("AV", 0.0)
    ac = cvss_score.get("AC", 0.0)
    pr = cvss_score.get("PR", 0.0)
    ui = cvss_score.get("UI", 0.0)
    exploit_score = float(8.22 * av * ac * pr * ui)
    return exploit_score


def calculate_impact_score(cvss_score: Dict[str, float]) -> float:
    """
    This function calculates the impact score of a CVSS vector in dictionary form.
    :param cvss_score: Input CVSS vector score of a cve in dictionary form.
    :return: The impact score of a cve
    """
    c = cvss_score.get("C", 0.0)
    i = cvss_score.get("I", 0.0)
    a = cvss_score.get("A", 0.0)
    # after conversion, the value 1.0 means unchanged, 1.08 means changed
    s = cvss_score.get("S", 1.0)

    # Impact Calculation
    iss = 1 - ((1 - c) * (1 - i) * (1 - a))
    # Unchanged Scope
    if s == 1.0:
        impact_score = 6.42 * iss
    else:  # Changed Scope
        impact_score = 7.52 * (iss - 0.029) - 3.25 * ((iss - 0.02) ** 15)
    # Ensure non-negative impact
    impact_score = max(impact_score, 0) 
    return impact_score
   


def get_cvss_base_score(vector_val_score_map: dict, cvss_vector: str) -> float:
    """
    This function calculates the cvss base score based on a given CVSS vector. It uses the impact score and exploitbility
    score to calculate the cvss base score.
    :param cvss_vector: Input CVSS vector of a cve
    :return:
    """
    cvss_score: Dict[str, float] = get_cvss_score(vector_val_score_map, cvss_vector)
    s = cvss_score.get("S", "U")
    impact = calculate_impact_score(cvss_score)
    exploit = calculate_exploit_score(cvss_score)
    # if scope is unchanged
    if impact <= 0:
        base_score = 0
    else:
        if s == 1.0:  # Unchanged Scope
            base_score = min(round_up(impact + exploit), 10.0)
        else:  # Changed Scope
            base_score = min(round_up(1.08 * (impact + exploit)), 10.0)
    return base_score

def round_up(in_value:float):
    """
    This function rounds up the input value to the nearest integer. The formula rounds up at 0.05 and above
    :param in_value:
    :return:
    """
    return math.ceil(in_value * 10) / 10