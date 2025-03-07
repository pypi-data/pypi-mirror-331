import pytest

from iv_sherlock.cve_evaluator import parse_cvss_vector, vector_str_to_value, \
    check_vector_score_mapping_validity, get_cvss_score, get_exploit_score_from_vector, get_impact_score_from_vector, \
    get_cvss_base_score


@pytest.fixture(scope='module')
def cveVector():
    return "AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:H"


@pytest.fixture(scope='module')
def cveWithBadVector():
    return "AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/AO:H"

@pytest.fixture(scope='module')
def cvss_vector_score_mapping():
    return {
  "AV": {
    "N": 0.85,
    "A": 0.62,
    "L": 0.55,
    "P": 0.2
  },
  "AC": {
    "L": 0.77,
    "H": 0.44
  },
  "PR": {
    "N": 0.85,
    "L": 0.62,
    "H": 0.27
  },
  "UI": {
    "N": 0.85,
    "R": 0.62
  },
  "S": {
    "U": 1.0,
    "C": 1.08
  },
  "C": {
    "H": 0.56,
    "L": 0.22,
    "N": 0.0
  },
  "I": {
    "H": 0.56,
    "L": 0.22,
    "N": 0.0
  },
  "A": {
    "H": 0.56,
    "L": 0.22,
    "N": 0.0
  }
}


def test_parseCvssVector():
    expected_vector = {'AV': 'N', 'AC': 'L', 'PR': 'N', 'UI': 'R', 'S': 'U', 'C': 'H', 'I': 'H', 'A': 'H'}
    vector = "AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H"
    resu = parse_cvss_vector(vector)
    print(resu)
    assert resu == expected_vector


def test_vectorStrToValue(cvss_vector_score_mapping):
    expected_score = {'AV': 0.85, 'AC': 0.77, 'PR': 0.85, 'UI': 0.62, 'S': 1.0, 'C': 0.56, 'I': 0.56, 'A': 0.56}
    cvss_score = {}
    vector = {'AV': 'N', 'AC': 'L', 'PR': 'N', 'UI': 'R', 'S': 'U', 'C': 'H', 'I': 'H', 'A': 'H'}
    for vec_type, vec_val in vector.items():
        print(f"type: {vec_type}, val: {vec_val}")
        vec_score = vector_str_to_value(cvss_vector_score_mapping,vec_val,vec_type)
        print(f"type: {vec_type}, val: {vec_score}")
        cvss_score[vec_type] = vec_score
    print(cvss_score)
    assert cvss_score == expected_score

def test_CveEvaluator_getCvssScore(cvss_vector_score_mapping):
    cvss_vector_str = "AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:H"
    expected_score = {'AV': 0.85, 'AC': 0.77, 'PR': 0.85, 'UI': 0.62, 'S': 1.0, 'C': 0.56, 'I': 0.22, 'A': 0.56}
    cvss_score = get_cvss_score(cvss_vector_score_mapping, cvss_vector_str)
    print(cvss_score)
    assert cvss_score == expected_score

def test_CveEvaluator_getExploitScore(cvss_vector_score_mapping):
    cvss_vector_str = "AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:H"
    expected_score = 2.835
    exploit_score = get_exploit_score_from_vector(cvss_vector_score_mapping, cvss_vector_str)
    resu = round(exploit_score, 3)
    print(exploit_score)
    assert resu == expected_score

def test_CveEvaluator_getImpactScore(cvss_vector_score_mapping):
    cvss_vector_str = "AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:H"
    expected_score = 3.134
    impact_score = get_impact_score_from_vector(cvss_vector_score_mapping,cvss_vector_str)
    print(impact_score)
    resu = round(impact_score, 3)
    assert resu == expected_score

def test_CveEvaluator_getCvssBaseScore_withValidVector(cvss_vector_score_mapping):
    cvss_vector_str = "AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:H"
    expected_base_score = 6
    actual_base_score = get_cvss_base_score(cvss_vector_score_mapping,cvss_vector_str)
    print(f"actual base score: {actual_base_score}")
    assert expected_base_score == actual_base_score


def test_CveEvaluator_getCvssBaseScore_withBadVectorType(cvss_vector_score_mapping):
    bad_cvss_vector = "AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/AO:H"
    expected_base_score = 6
    actual_base_score = get_cvss_base_score(cvss_vector_score_mapping,bad_cvss_vector)
    print(f"actual base score: {actual_base_score}")
    assert expected_base_score == actual_base_score

def test_checkVectorScoreMappingValidity_withValidVector():
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

def test_checkVectorScoreMappingValidity_withMissVectorType():
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

def test_checkVectorScoreMappingValidity_withMoreVectorType():
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

def test_checkVectorScoreMappingValidity_withMissVectorVal():
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