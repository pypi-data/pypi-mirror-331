import argparse
import sys

from simplelabel import __appname__
from simplelabel import __version__
from simplelabel.core import DEFAULT_FIELD_MAP
from simplelabel.utils import DataLabelEngine
from simplelabel.utils import SQLGenerator


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--version", "-V",
        action="store_true",
        help="show version"
    )
    parser.add_argument(
        "--label", "-L",
        nargs=2,
        metavar=('rule', 'data'),
        help="Quickly complete data labeling with rules"
    )
    parser.add_argument(
        "--generate", "-G",
        nargs=1,
        metavar='rule',
        help="Quickly complete SQL generation with rules"
    )
    parser.add_argument(
        "--output", "-o", "-O",
        help="output file path"
    )

    args = parser.parse_args()

    try:
        # 版本信息 --version
        if args.version:
            print("{0} {1}".format(__appname__, __version__))
            sys.exit(0)

        if args.label:
            if args.output is None:
                print("Output file path (-o) is required when using --label.")
                return

            rule_file, data_file = args.label
            output_labeled_file = args.output

            # 快速完成数据标注
            label_engine = DataLabelEngine.init(rule_file, field_map=DEFAULT_FIELD_MAP)
            label_engine.label(data_file, output_labeled_file)

            print(f"Labeled data already saved to {output_labeled_file}.")

        if args.generate:
            if args.output is None:
                print("Output file path (-o) is required when using --generate.")
                return

            rule_file = args.generate[0]
            output_sql_file = args.output

            # 快速完成SQL语句生成
            sql_generator = SQLGenerator.init(rule_file, field_map=DEFAULT_FIELD_MAP)
            sql_generator.generate(output_sql_file)

            print(f"Generated SQL statement already saved to {output_sql_file}.")

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(0)

    finally:
        sys.exit(0)


if __name__ == "__main__":
    main()
