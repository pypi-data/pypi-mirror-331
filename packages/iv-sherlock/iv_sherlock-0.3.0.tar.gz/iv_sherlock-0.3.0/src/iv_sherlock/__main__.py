# Standard library imports
import argparse


# sherlock imports

from iv_sherlock.config_manager import Config

from iv_sherlock.report_generator import ReportGenerator




def main():
    print("Generating report...")

    # create an arg parse for cli
    parser = argparse.ArgumentParser(description="Parse raw vulnerabilities reports and generate human readable report.")
    parser.add_argument("-c","--conf",  type=str, help="The custom configuration file path. The configuration file must be in .toml format.")
    args = parser.parse_args()
    # create a config manager
    config = Config(args.conf)

    # generate vul report
    rg = ReportGenerator(config)
    rg.generate_reports_from_source_dir()
    print("Done.")



if __name__ == "__main__":
    main()
