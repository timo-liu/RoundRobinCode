from Utils import *
import argparse
import os

if __name__ == "__main__":
	argparser = argparse.ArgumentParser()
	argparser.add_argument("-s", "--score_file", default="Data/scores.tsv")
	argparser.add_argument("-r", "--remove_errors", action="store_true")
	argparser.add_argument("-f", "--format", type=str, help="individual, 2team, or 3team", default="individual", choices=["individual", "2team", "3team"])
	argparser.add_argument("-o", "--output_dir", default="Matchups")
	args = argparser.parse_args()

	os.makedirs(args.output_dir, exist_ok=True)