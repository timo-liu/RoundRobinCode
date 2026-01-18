from Utils import *
import argparse

from Utils import load_scores
from Utils.rr_matcher import match_individuals
import os

if __name__ == "__main__":
	argparser = argparse.ArgumentParser()
	argparser.add_argument("-s", "--score_file", default="Data/scores.tsv")
	argparser.add_argument("-r", "--remove_errors", action="store_true")
	argparser.add_argument("-f", "--format", type=str, help="individual, 2team, or 3team", default="individual", choices=["individual", "2team", "3team"])
	argparser.add_argument("-o", "--output_dir", default="Matchups")
	args = argparser.parse_args()

	os.makedirs(args.output_dir, exist_ok=True)

	# get the scores
	scores = load_scores(args.score_file, args.remove_errors)

	match args.format:
		case "individual":
			final_matchups = match_individuals(scores, people_per_flight=4)
			for division, flight_info in final_matchups.items():
				for flight, matchups in flight_info.items():
					out = os.path.join(args.output_dir, f"{division}_flight-{flight}.tsv")
					matchups.to_csv(out, sep="\t", index=True)