import pandas as pd

def match_teams(scores: pd.DataFrame, number_of_flight : int = 2, people_per_team : int = 2) -> pd.DataFrame:
	divisions = scores["Division"].unique()
	flight_dict = {}
	for division in divisions:
		flight_dict[division] = {}
		if "QualScore" not in scores.columns:
			round_cols = [f"R{i}" for i in range(1, 11)]
			section = scores[scores["Division"] == division].copy()
			section["QualScore"] = section[round_cols].sum(axis=1)
			section = section.drop(columns=round_cols)
		else:
			section = scores[scores["Division"] == division].copy()
		section = section.sort_values(by=["QualScore"], ascending=False)
	# TODO Figure out what to do when the number of archers % people_per_team != 0