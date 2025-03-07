# define basic image info dict keys
OS_FAMILY = "os_family"
OS_NAME = "os_name"
OS_ARCHI = "os_archi"
REPO_TAGS = "repo_tags"
IMG_ID = "image_id"
IMG_NAME = "image_name"
IMG_CREATION_TIME = "creation_time"

# define results parsed dict keys
TARGET_NAME = "target_name"
TARGET_CLASS = "target_class"
TARGET_TYPE = "target_type"
TARGET_VULNERABILITY_DF = "target_vul_df"

# define vulnerability dataframe column name
LIBRARY = "library"
VULNERABILITY_ID = "vulnerability_id"
VULNERABILITY_URL = "vulnerability_url"
SEVERITY = "severity"
CASD_SEVERITY = "casd_severity"
CASD_CVSS_SCORE = "casd_cvss_score"
STATUS = "status"
INSTALLED_VER = "installed_version"
FIXED_VER = "fixed_version"
DESCRIPTION = "description"
CVSS_V3_SCORE = "cvss_v3_score"
CVSS_V3_VECTOR = "cvss_v3_vector"


from enum import Enum

class Severity(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

class CvssScoreSeverityMapper:
    @staticmethod
    def get_cve_severity(cvss_score:float)->Severity:
        """
        This method takes a CVSS score value and returns a Severity. Below is the general cvss score system
        Low: 0.1-3.9
        Medium: 4.0-6.9
        High: 7.0-8.9
        Critical: 9.0-10.0
        :param cvss_score:
        :return:
        """
        if 0 <= cvss_score <= 3.9 :
            return Severity.LOW
        elif 4.0 <= cvss_score <= 6.9 :
            return Severity.MEDIUM
        elif 7.0 <= cvss_score <= 8.9 :
            return Severity.HIGH
        elif 9.0 <= cvss_score <= 10.0 :
            return Severity.CRITICAL
        else:
            error_msg = f'Invalid cvss score {cvss_score}. CVSS score must be between 0 and 10.0. Use default value'
            print(error_msg)
            return Severity.CRITICAL
