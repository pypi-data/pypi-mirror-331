"""
cve_evaluator

===========

This module provides a class and functions to calculate the `cvss_score` based on the `cvss_vector` of a `CVE`.

Author:
    Pengfei liu

Date:
    2025-02-25
"""
from typing import Dict, List


def parse_cvss_vector(cvss_vector: str)-> Dict[str, str]:
    """
    This function parses the cvss vector string into a cvss vector dictionary. For example, a vector string
     "AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H" will be converted to a dictionary like {"AV":"N", "AC","L"}.

    :param cvss_vector: The cvss vector string, e.g. AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H
    :return: a dictionary with key as vector type, and value as vector value e.g. {"AV":"N", "AC","L"}
    """
    metrics = cvss_vector.split("/")
    metric_dict = {metric.split(":")[0]: metric.split(":")[1] for metric in metrics}
    return metric_dict


def vector_str_to_value(vector_val_score_map:dict, vector_val: str, vector_type: str) -> float:
    """
    This function converts a vector string into a severity score (float value). The input vector_val_score_map must
    be tested for validly. We don't want to test it each time when this function is called. If nothing found return 0
    :param vector_val_score_map:
    :param vector_val: The enum value of the vector, each vector type has its own enum value
    :param vector_type: The type of the CVSS vector, e.g. AV->Attack Vector, A->Availability Impact
    :return: A score value between 0 and 1, the higher numbers representing a higher degree of severity
    """

    return vector_val_score_map[vector_type].get(vector_val, 0.0)

def check_vector_score_mapping_validity(vector_value_score_map:dict)-> (bool,str):
    """
    This function checks whether a vector value score mapping is valid. The input map must contain all required vector
    types, and each vector type must contain all required vector values for the vector type.
    :param vector_value_score_map: The input vector value score mapping, if a user does not provide one, use the default
    :return: A tuple of result and comments
    """
    expected_vector_types = {"AV":['N', 'A', 'L', 'P'],
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
        missing_vec_type = [vec_type for vec_type in list(expected_vector_types.keys()) if vec_type not in actual_vector_types]
        if missing_vec_type:
            return False, f"Missing required vector type: {missing_vec_type}"
        else:
            # 2. check for each vector type, it contains the required values
            for vec_type in actual_vector_types:
                expected_vec_vals:List[str] = list(expected_vector_types[vec_type])
                missing_vec_val = [vec_val for vec_val in expected_vec_vals if vec_val not in list(vector_value_score_map[vec_type].keys())]
                if missing_vec_val:
                    return False, f"Vector type {vec_type} is missing required value: {missing_vec_val}"
            return True, "The provided vector_value_score_map is valid"






class CveEvaluator:
    """
    Represents a cve evaluator in the system.
    This class calculates the basic scores with a given CVSS vector. The equation is from
    https://www.first.org/cvss/v3.1/specification-document. You can find all equation details in
    section 7.1

    :param cvss_vector: The cvss vector of the cve
    :type cvss_vector: str


    :ivar cvss_vector: The cvss vector of the cve in string format
    :vartype cvss_vector: str
    :ivar cvss_vec_dict: vss vector of the cve in dictionary format
    :vartype cvss_vec_dict: Dict[str, str]
    :ivar cvss_score: The cvss score of the cve
    :vartype cvss_score: float

    """

    def __init__(self, cvss_vector: str):
        """
        Initializes a cve evaluator
        :param cvss_vector: The cvss vector of the cve
        """
        self.cvss_vector:str = cvss_vector
        self.cvss_vec_dict:Dict[str,str] = parse_cvss_vector(cvss_vector)
        self.cvss_score:Dict[str, float] = self.get_cvss_score()

    def get_cvss_score(self) -> Dict[str, float]:
        """
        This function converts a cvss vector string into a cvss score dictionary.
        :return:
        """
        # get the vector value dict
        vectors = parse_cvss_vector(self.cvss_vector)
        # transform the vector value in str to float
        return {
            vec_type: vector_str_to_value(vec_val, vec_type)
            for vec_type, vec_val in vectors.items()
        }

    def get_exploit_score(self) -> float:
        """
        This function calculates the exploitability score of a CVSS vector.
        :return:
        """
        av = self.cvss_score.get("AV", 0.0)
        ac = self.cvss_score.get("AC", 0.0)
        pr = self.cvss_score.get("PR", 0.0)
        ui = self.cvss_score.get("UI", 0.0)

        return 8.22 * av * ac * pr * ui

    def get_impact_score(self) -> float:
        """
        This function calculates the impact score of a CVSS vector.
        :return:
        """
        c = self.cvss_score.get("C", 0.0)
        i = self.cvss_score.get("I", 0.0)
        a = self.cvss_score.get("A", 0.0)
        # if scope is unchanged
        if self.cvss_score.get("S") == "U":
            return 1 - (1 - c) * (1 - i) * (1 - a)
        else:
            return 7.52 * (1 - (1 - c) * (1 - i) * (1 - a)) - 3.25

    def get_cvss_base_score(self)->float:
        """
        This function calculates the cvss base score of a CVSS vector.
        :return:
        """
        impact = self.get_impact_score()
        exploit = self.get_exploit_score()
        # if scope is unchanged
        if self.cvss_score.get("S") == "U":
            return round(min(10, (impact + exploit)))
        else:
            return round(min(10, 1.08 * (impact + exploit)))
