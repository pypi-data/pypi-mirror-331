"""
report_generator
===============

This module provides a class to generate html and pdf reports based on the results of image_vul_parser.

Author:
    Pengfei liu

Date:
    2025-02-25
"""

# Standard library imports
import sys
from pathlib import Path
from typing import List
import glob
from pathlib import Path

# Third party imports
import pandas as pd
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

# sherlock imports
from iv_sherlock.conf.constant import (
    IMG_NAME,
    TARGET_VULNERABILITY_DF,
)
from iv_sherlock.config_manager import Config
from iv_sherlock.image_vul_parser import ImageVulParser


class ReportGenerator:
    """
    Represents a report generator. It can generate a vulnerability report for each image, and a general
    report which summery the vulnerability of all existing images.

    :param config: The config object which contains the configuration of the report.
    :type config: iv_sherlock.config_manager.Config

    :ivar output_path: The directory path which hosts the generated reports.
    :vartype output_path: str

    """

    def __init__(self, config: Config):
        template_dir_path = Config.get_report_template_dir_path()
        if self._is_path_valid(template_dir_path):
            environment = Environment(loader=FileSystemLoader(template_dir_path))
            self.template = environment.get_template("vul_report.html")
            self.general_template = environment.get_template("gen_report.html")
            self.vul_simple_template = environment.get_template("vul_simple.html")
            self.end_general_template = environment.get_template("end_template.html")
        else:
            raise ValueError("The provided template dir path is not valid.")
        self.output_path = config.get_output_report_path()
        self.encoding = config.get_default_encoding()
        self.raw_data_root_dir = config.get_input_report_path()
        self.export_pdf = config.get_export_pdf()
        self.cvss_vector_score_mapping = config.get_cvss_vector_value_mapping()

    @staticmethod
    def _is_path_valid(dir_path: str):
        return Path(dir_path).is_dir()

    def generate_reports_from_source_dir(self):
        """
        This function takes the directory define in config which contains the raw vulnerability reports, then generates
        a vulnerability report for each raw report and a summery report.
        :return:
        """

        # store results
        results = []
        for image_path in glob.glob(f"{self.raw_data_root_dir}/*.json"):
            raw_data_path = Path(image_path)
            # create image vul parser
            img_vul_parser = ImageVulParser(raw_data_path.as_posix(), self.cvss_vector_score_mapping)
            results.append(img_vul_parser.build_image_vul_report())
        if len(results) == 0:
            error_msg = (f"Can't find any vulnerabilities report. Make sure the report "
                         f"source directory {self.raw_data_root_dir} is correct.")
            print(error_msg)
            exit(1)
        # create report generator
        self.initiate_general_report(results)
        for base_info, cve_list in results:
            self.generate_report(base_info, cve_list)
            self.append_general_report(image_info=base_info, cve_list=cve_list)

        self.close_general_report()
        if self.export_pdf:
            self.render_template_to_pdf()

    def generate_report(self, image_info: dict, cve_list: List[dict]):
        for cve in cve_list:
            vul_df: pd.DataFrame = pd.DataFrame(cve[TARGET_VULNERABILITY_DF])
            vul_html = vul_df.to_html(index=False)
            cve["target_vul_html"] = vul_html
        content = self.template.render(image_info=image_info, cve_list=cve_list)
        raw_image_name = image_info[IMG_NAME]
        image_name = self._normalize_image_name(raw_image_name)
        report_path = Path(self.output_path) / f"{image_name}_report.html"
        try:
            with open(report_path.as_posix(), "w+", encoding=self.encoding) as f:
                f.write(content)
        except FileNotFoundError:
            print(f"Can't create report file {report_path}, make sure the {self.output_path} directory exists.")
            sys.exit(1)

    def initiate_general_report(self, image_list):
        image_infos = []
        targets = 0
        cve_count_by_status_list = []
        for base_info, cve_list in image_list:
            targets = 0
            for cve in cve_list:
                targets = targets + 1
                vul_df: pd.DataFrame = pd.DataFrame(cve[TARGET_VULNERABILITY_DF])
                if len(vul_df) != 0:
                    cve_count_by_status = (
                        vul_df.groupby("severity").size().reset_index(name="CVE_Count")
                    )
                    cve_count_by_status_list.append(cve_count_by_status)

            combined_df = pd.concat(cve_count_by_status_list)
            cve_count_by_status = combined_df.groupby("severity", as_index=False).sum()
            result: dict = {}
            result[IMG_NAME] = self._normalize_image_name(base_info[IMG_NAME])
            result["targets"] = targets
            result["critical"] = cve_count_by_status[
                cve_count_by_status.severity == "CRITICAL"
                ].values[0][1]
            result["high"] = cve_count_by_status[
                cve_count_by_status.severity == "HIGH"
                ].values[0][1]
            result["medium"] = cve_count_by_status[
                cve_count_by_status.severity == "MEDIUM"
                ].values[0][1]
            result["low"] = cve_count_by_status[
                cve_count_by_status.severity == "LOW"
                ].values[0][1]
            result["image_link"] = f"../tmp/{result[IMG_NAME]}_report.html"

            image_infos.append(result)
        content = self.general_template.render(imageinfos=image_infos)
        report_path = Path(self.output_path) / f"general_report.html"
        try:
            with open(report_path.as_posix(), "w") as f:
                f.write(content)
        except FileNotFoundError:
            print(f"Can't create report file {report_path}, make sure the {self.output_path} directory exists.")
            sys.exit(1)

    def append_general_report(self, image_info: dict, cve_list: List[dict]):
        for cve in cve_list:
            vul_df: pd.DataFrame = pd.DataFrame(cve[TARGET_VULNERABILITY_DF])
            if len(vul_df) != 0:
                cve_count_by_status = (
                    vul_df.groupby(["severity", "status"])
                    .size()
                    .reset_index(name="CVE_Count")
                )
                vul_count_html = cve_count_by_status.to_html(index=False)
                cve["target_vul_html"] = vul_count_html
        content = self.vul_simple_template.render(
            image_info=image_info,
            cve_list=cve_list,
            image_link=f"../tmp/{image_info[IMG_NAME]}_report.html",
        )
        report_path = Path(self.output_path) / f"general_report.html"
        with open(report_path.as_posix(), "a") as f:
            f.write(content)

    def close_general_report(self):
        content = self.end_general_template.render()
        report_path = Path(self.output_path) / f"general_report.html"
        with open(report_path.as_posix(), "a") as f:
            f.write(content)

    def render_template_to_pdf(self):
        # allows to run without platwright installed if export_pdf = False
        try:
            # Third party imports
            from playwright.sync_api import sync_playwright
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "Playwright needs to be installed to export to PDF, run : pip install playwright & playwright install"
            )
        with sync_playwright() as p:
            selectors_to_click = ["button"]
            browser = p.chromium.launch()
            page = browser.new_page()
            html_path = Path(self.output_path) / f"general_report.html"
            page.goto(f"file://{html_path.resolve()}")

            page.wait_for_load_state("networkidle")

            # Simule des clics sur les éléments des sections à dérouler (via leurs sélecteurs CSS)
            for selector in selectors_to_click:
                page.click(selector)

            pdf_path = Path(self.output_path) / f"general_report.pdf"
            page.pdf(path=pdf_path, format="A4", print_background=True)

            browser.close()

    @staticmethod
    def _normalize_image_name(image_name: str) -> str:
        """
        This function normalize the image name repo_name/image_name to repo_name-image_name
        :param image_name:
        :return:
        """
        return image_name.replace("/", "-")
