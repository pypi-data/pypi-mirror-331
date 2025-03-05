import pandas as pd
import pytest
from importlib import resources
from iv_sherlock.conf.constant import OS_FAMILY, REPO_TAGS, IMG_ID, OS_NAME, OS_ARCHI, IMG_NAME, IMG_CREATION_TIME
from iv_sherlock.image_vul_parser import ImageVulParser


@pytest.fixture
def redis_img_vul_parser():
    report_path = str(resources.files("iv_sherlock.data") / "redis.json")
    return ImageVulParser(raw_report_path=report_path)


def test_getRawData(redis_img_vul_parser):
    raw_data = redis_img_vul_parser.get_raw_data()
    print(raw_data)

def test_parseImageMetadata(redis_img_vul_parser):
    expected_os_family = "debian"
    expected_os_name = "12.7"
    expected_os_archi = "amd64"
    expected_repo_tags = ['redis:latest']
    expected_image_id = "sha256:590b81f2fea1af9798db4580a6299dafba020c2f5dc7d8d734663e7fa5299ca0"
    res = redis_img_vul_parser.parse_image_metadata()
    os_family = res[OS_FAMILY]
    os_name = res[OS_NAME]
    os_archi = res[OS_ARCHI]
    repo_tags = res[REPO_TAGS]
    image_id = res[IMG_ID]
    print(f"os_family: {os_family}")
    print(f"os_name: {os_name}")
    print(f"os_archi: {os_archi}")
    print(f"repo_tags: {repo_tags}")
    print(f"image_id: {image_id}")
    assert os_family == expected_os_family
    assert os_name == expected_os_name
    assert os_archi == expected_os_archi
    assert repo_tags == expected_repo_tags
    assert image_id == expected_image_id

def test_getImageBasicInfo(redis_img_vul_parser):
    expected_os_family = "debian"
    expected_os_name = "12.7"
    expected_os_archi = "amd64"
    expected_repo_tags = ['redis:latest']
    expected_image_id = "sha256:590b81f2fea1af9798db4580a6299dafba020c2f5dc7d8d734663e7fa5299ca0"
    expected_image_name = "redis"
    expected_image_creation_time = "2024-09-13T09:13:14.153929471+02:00"
    res = redis_img_vul_parser.get_image_basic_info()
    os_family = res[OS_FAMILY]
    os_name = res[OS_NAME]
    os_archi = res[OS_ARCHI]
    repo_tags = res[REPO_TAGS]
    image_id = res[IMG_ID]
    image_name = res[IMG_NAME]
    image_creation_time = res[IMG_CREATION_TIME]
    print(res)
    assert os_family == expected_os_family
    assert os_name == expected_os_name
    assert os_archi == expected_os_archi
    assert repo_tags == expected_repo_tags
    assert image_id == expected_image_id
    assert image_creation_time == expected_image_creation_time
    assert image_name == expected_image_name



def test_buildImageVulReport(redis_img_vul_parser):
    img_info, cve_list = redis_img_vul_parser.build_image_vul_report()
    for cve in cve_list:
        print(cve)

def test_parserTargetVulnerabilities(redis_img_vul_parser):
    vuls = redis_img_vul_parser.raw_data.get("Results")[0].get("Vulnerabilities")

    pdf = redis_img_vul_parser.parser_target_vulnerabilities(vuls)
    for column in pdf.columns:
        print(f"Column: {column}, Type: {pdf[column].dtype}")
    pd.set_option('display.max_columns', None)  # Show all columns
    pd.set_option('display.max_colwidth', None)  # Show full content in each column
    print(pdf.head())

def test_parserCvss_withValidCvssValue(redis_img_vul_parser):
    expected_v3_score = 3.7
    expected_v3_vector = "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N"
    cvss = redis_img_vul_parser.raw_data.get("Results")[0].get("Vulnerabilities")[0].get("CVSS")
    v3_score,v3_vector = redis_img_vul_parser.parse_cvss(cvss)
    print(v3_score)
    print(v3_vector)
    assert v3_score == expected_v3_score
    assert v3_vector == expected_v3_vector


def test_parserCvss_withBadCvssValue(redis_img_vul_parser):
    cvss = {}
    v3_score,v3_vector = redis_img_vul_parser.parse_cvss(cvss)
    print(v3_score)
    print(v3_vector)
    assert v3_score is None
    assert v3_vector is None

def test_getAvailableAttributes(redis_img_vul_parser):
    expected_attributes = ['SchemaVersion', 'CreatedAt', 'ArtifactName', 'ArtifactType', 'Metadata', 'Results']
    actual_attributes = redis_img_vul_parser.get_available_attributes()
    print(actual_attributes)
    assert expected_attributes == actual_attributes

