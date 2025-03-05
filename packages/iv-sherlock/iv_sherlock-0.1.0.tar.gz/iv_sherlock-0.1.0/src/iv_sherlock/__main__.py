# Standard library imports
import argparse
import glob
from pathlib import Path

# sherlock imports

from iv_sherlock.config_manager import Config
from iv_sherlock.image_vul_parser import ImageVulParser
from iv_sherlock.report_generator import ReportGenerator


def main():


    # create an arg parse for cli
    parser = argparse.ArgumentParser(description="Parse raw vulnerabilities reports and generate human readable report.")
    parser.add_argument("-c","--conf",  type=str, help="The custom configuration file path. The configuration file must be in .toml format.")
    args = parser.parse_args()
    # create a config manager
    config = Config(args.conf)
    # get values from config manager
    raw_data_root_dir = config.get_input_report_path()

    export_pdf = config.get_export_pdf()
    # store results
    results = []
    for image_path in glob.glob(f"{raw_data_root_dir}/*.json"):
        raw_data_path = Path(image_path)
        # create image vul parser
        img_vul_parser = ImageVulParser(raw_data_path.as_posix())
        results.append(img_vul_parser.build_image_vul_report())
    if len(results) == 0:
        print(f"Can't find any vulnerabilities report. Make sure the report source directory {config.get_input_report_path()} is correct.")
    # create report generator
    rg = ReportGenerator(config)
    rg.initiate_general_report(results)
    for base_info, cve_list in results:
        rg.generate_report(base_info, cve_list)
        rg.append_general_report(image_info=base_info, cve_list=cve_list)

    rg.close_general_report()
    if export_pdf:
        rg.render_template_to_pdf()


if __name__ == "__main__":
    main()
