import argparse
import os
from Utils import load_scores
from Utils import *

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-s", "--score_file", default="Data/quals_scores.tsv")
    argparser.add_argument("-r", "--remove_errors", action="store_true")
    argparser.add_argument("-f", "--format", type=str, default="2team", choices=["2team", "3team"])
    argparser.add_argument("-o", "--output_dir", default="Matchups")
    args = argparser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    scores = load_scores(args.score_file, args.remove_errors)

    people_per_team = 2 if args.format == "2team" else 3

    # Run team matching
    final_teams_dict = match_teams(scores, people_per_team=people_per_team)

    for division, flights in final_teams_dict.items():
        print(flights)
        output_file = os.path.join(args.output_dir, f"{division}_{people_per_team}-person_teams.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            for flight_num, teams in enumerate(flights, start=1):
                    f.write(teams + "\n")

    print(f"Team matchups saved to {args.output_dir}")
