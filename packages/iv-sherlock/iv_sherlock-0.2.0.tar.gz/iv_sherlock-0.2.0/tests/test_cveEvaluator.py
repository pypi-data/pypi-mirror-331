import pytest

from iv_sherlock.cve_evaluator import CveEvaluator, parse_cvss_vector, vector_str_to_value, \
    check_vector_score_mapping_validity


@pytest.fixture(scope='module')
def cveEvaluator():
    vector = "AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:H"
    return CveEvaluator(vector)

@pytest.fixture(scope='module')
def cveEvaluatorWithBadVector():
    vector = "AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/AO:H"
    return CveEvaluator(vector)


def test_parseCvssVector():
    expected_vector = {'AV': 'N', 'AC': 'L', 'PR': 'N', 'UI': 'R', 'S': 'U', 'C': 'H', 'I': 'H', 'A': 'H'}
    vector = "AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H"
    resu = parse_cvss_vector(vector)
    print(resu)
    assert resu == expected_vector


def test_vectorStrToValue():
    expected_score = {'AV': 0.85, 'AC': 0.77, 'PR': 0.85, 'UI': 0.62, 'S': 1.0, 'C': 0.56, 'I': 0.56, 'A': 0.56}
    cvss_score = {}
    vector = {'AV': 'N', 'AC': 'L', 'PR': 'N', 'UI': 'R', 'S': 'U', 'C': 'H', 'I': 'H', 'A': 'H'}
    for vec_type, vec_val in vector.items():
        print(f"type: {vec_type}, val: {vec_val}")
        vec_score = vector_str_to_value(vec_val,vec_type)
        print(f"type: {vec_type}, val: {vec_score}")
        cvss_score[vec_type] = vec_score
    print(cvss_score)
    assert cvss_score == expected_score

def test_CveEvaluator_getCvssScore(cveEvaluator):
    expected_score = {'AV': 0.85, 'AC': 0.77, 'PR': 0.85, 'UI': 0.62, 'S': 1.0, 'C': 0.56, 'I': 0.22, 'A': 0.56}
    cvss_score = cveEvaluator.get_cvss_score()
    print(cvss_score)
    assert cvss_score == expected_score

def test_CveEvaluator_getExploitScore(cveEvaluator):
    expected_score = 2.835
    exploit_score = cveEvaluator.get_exploit_score()
    resu = round(exploit_score, 3)
    print(exploit_score)
    assert resu == expected_score

def test_CveEvaluator_getImpactScore(cveEvaluator):
    expected_score = 3.134
    impact_score = cveEvaluator.get_impact_score()
    print(impact_score)
    resu = round(impact_score, 3)
    assert resu == expected_score

def test_CveEvaluator_getCvssBaseScore_withValidVector(cveEvaluator):
    expected_base_score = 6
    actual_base_score = cveEvaluator.get_cvss_base_score()
    print(f"actual base score: {actual_base_score}")
    assert expected_base_score == actual_base_score


def test_CveEvaluator_getCvssBaseScore_withBadVectorType(cveEvaluatorWithBadVector):
    expected_base_score = 6
    actual_base_score = cveEvaluatorWithBadVector.get_cvss_base_score()
    print(f"actual base score: {actual_base_score}")
    assert expected_base_score == actual_base_score

def test_checkVectorScoreMappingValidity_withValidVector(cveEvaluator):
    vector_score_mapping = {
        "AV": {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2},
        "AC": {"L": 0.77, "H": 0.44},
        "PR": {"N": 0.85, "L": 0.62, "H": 0.27},
        "UI": {"N": 0.85, "R": 0.62},
        "S": {"U": 1.0, "C": 1.08},
        "C": {"H": 0.56, "L": 0.22, "N": 0.0},
        "I": {"H": 0.56, "L": 0.22, "N": 0.0},
        "A": {"H": 0.56, "L": 0.22, "N": 0.0},
    }
    resu,comments = check_vector_score_mapping_validity(vector_score_mapping)
    print(comments)
    assert resu == True

def test_checkVectorScoreMappingValidity_withMissVectorType(cveEvaluator):
    vector_score_mapping = {
        "AV": {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2},
        "AC": {"L": 0.77, "H": 0.44},
        "PR": {"N": 0.85, "L": 0.62, "H": 0.27},
        "C": {"H": 0.56, "L": 0.22, "N": 0.0},
        "I": {"H": 0.56, "L": 0.22, "N": 0.0},
    }
    resu, comments = check_vector_score_mapping_validity(vector_score_mapping)
    print(comments)
    assert resu == False

def test_checkVectorScoreMappingValidity_withMoreVectorType(cveEvaluator):
    vector_score_mapping = {
        "AV": {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2},
        "AC": {"L": 0.77, "H": 0.44},
        "PR": {"N": 0.85, "L": 0.62, "H": 0.27},
        "UI": {"N": 0.85, "R": 0.62},
        "S": {"U": 1.0, "C": 1.08},
        "C": {"H": 0.56, "L": 0.22, "N": 0.0},
        "I": {"H": 0.56, "L": 0.22, "N": 0.0},
        "A": {"H": 0.56, "L": 0.22, "N": 0.0},
        "ATEST": {"H": 0.56, "L": 0.22, "N": 0.0},
    }
    resu, comments = check_vector_score_mapping_validity(vector_score_mapping)
    print(comments)
    assert resu == True

def test_checkVectorScoreMappingValidity_withMissVectorVal(cveEvaluator):
    vector_score_mapping = {
        "AV": {"N": 0.85, "A": 0.62,},
        "AC": {"L": 0.77, "H": 0.44},
        "PR": {"N": 0.85, "L": 0.62, "H": 0.27},
        "UI": {"N": 0.85, "R": 0.62},
        "S": {"U": 1.0, "C": 1.08},
        "C": {"H": 0.56, "L": 0.22, "N": 0.0},
        "I": {"H": 0.56, "L": 0.22, "N": 0.0},
        "A": {"H": 0.56, "L": 0.22, "N": 0.0},
    }
    resu,comments = check_vector_score_mapping_validity(vector_score_mapping)
    print(comments)
    assert resu == False