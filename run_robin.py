from Utils import *
import argparse

from Utils import load_scores
from Utils.matcher import match_individuals

if __name__ == "__main__":
	argparser = argparse.ArgumentParser()
	argparser.add_argument("-s", "--score_file", default="Data/scores.tsv")
	argparser.add_argument("-r", "--remove_errors", action="store_true")
	argparser.add_argument("-f", "--format", type=str, help="individual, 2team, or 3team", default="individual", choices=["individual", "2team", "3team"])
	args = argparser.parse_args()

	# get the scores
	scores = load_scores(args.score_file, args.remove_errors)

	match args.format:
		case "individual":
			match_individuals(scores)