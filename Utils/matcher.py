import pandas as pd
import os
import math
from typing import List, Tuple

def match_individuals(scores : pd.DataFrame, num_flights : int = 2, algorithm : str = "berger", save_to : str = "Matchups"):
	"""
	Give everyone seeds, match top to bottom seeds, and create a fake 'Seed 0' Bye archer for odd numbers
	:param scores:
	:return:
	"""

	os.makedirs(save_to, exist_ok=True)

	divisions = scores["Division"].unique()
	for division in divisions:
		round_cols = [f"R{i}" for i in range(1, 11)]
		section = scores[scores["Division"] == division].copy()
		section["QualScore"] = section[round_cols].sum(axis=1)
		section = section.drop(columns=round_cols)
		section = section.sort_values(by=["QualScore"], ascending=False)

		people_per_flights = len(section) // num_flights

		flights = [section.iloc[i:i+people_per_flights] for i in range(0, len(section), people_per_flights)]

		for i, flight in enumerate(flights):

			output_path = os.path.join(save_to, f"{division}-Flight{i}.tsv")
			if len(flight) % 2 != 0:
				bye = pd.DataFrame([{
					"Name": "BYE",
					"Division": division,
					"QualScore": -math.inf
				}])
				flight = pd.concat([flight, bye], ignore_index=True)

			flight = flight.reset_index(drop=True)
			flight_names = flight["Name"].tolist()
			division_matchups = rr(flight_names, algorithm)
			division_matchups.to_csv(output_path, sep="\t", index=False)


def o_n_alternate(lower_bound : int = 0, upper_bound : int = 100):
	"""
	Create an alternating list of high low indices for matching
	There's an O(n) algorithm, that's pretty cool.
	:param lower_bound:
	:param upper_bound:
	:return:
	"""
	indices = list(range(lower_bound, upper_bound + 1))
	final = []
	for i, a in enumerate(indices):
		if i == 0 or (i%2 and i > final[-1]) or (not i%2 and i < final[-1]):
			final.append(a)
		else:
			final.insert(i - 1, a)

	return final

def step_list_circular(arr : List, steps : int = 0):
	"""
	Circular step in place
	:param arr:
	:param steps:
	:return:
	"""
	for step in range(steps):
		arr.append(arr.pop(0))
	return arr

def create_berger_matrix (number_of_competitors : int):
	"""
	Makes the n-1 n-1 table, matchups where i == j are against player n
	:param number_of_competitors:
	:return:
	"""
	return [step_list_circular(list(range(1, number_of_competitors)), i) for i in range(1, number_of_competitors)]

def rr_convolute(number_of_competitors : int, algorithm : str = "berger") -> List[List[Tuple[int,int]]]:
	"""
	produce an array of number_of_rounds arrays
	Going to use berger table algorithm
	:param number_of_competitors:
	:return:
	"""
	assert not number_of_competitors % 2, "The number of competitors in a flight should be even."
	number_of_rounds = int(number_of_competitors/2) * (number_of_competitors - 1)

	versus : List[List[Tuple[int,int]]] = [[] for _ in range(number_of_rounds)]

	match algorithm:
		case "berger":
			matchups = create_berger_matrix(number_of_competitors)
			for i in range(number_of_competitors - 1):
				for j in range(number_of_competitors - 1):
					pair = (i + 1, j + 1)
					if i == j:
						pair = (i + 1, number_of_competitors)
					versus[matchups[i][j] - 1].append(pair)
		case _ :
			assert False, f"{algorithm} has not been implemented."
	return versus

def build_matches(names : List[str], matchups : List[List[Tuple[int,int]]]) -> pd.DataFrame:
	"""
	Build matches from a list of names, assumed sorted by scores, and matchup info from rr_convolute. Returns a dataframe with the rounds.
	:param names:
	:param matchups:
	:return:
	"""
	final_lineup = pd.DataFrame(columns = ["Bale"]).set_index("Bale")
	for round_number, round_info in enumerate(matchups):
		round_names = []
		for pair in round_info:
			round_name = f"{names[pair[0] - 1]} vs {names[pair[1] - 1]}"
			round_names.append(round_name)
		if len(final_lineup) < len(round_names):
			final_lineup = final_lineup.reindex(range(len(round_names)))
		elif len(round_names) < len(final_lineup):
			round_names += [None] * (len(final_lineup) - len(round_names))
		final_lineup[f"Round {round_number + 1}"] = round_names
	return final_lineup

def rr(names : List[str], algorithm : str = "berger") -> pd.DataFrame:
	matchups = rr_convolute(number_of_competitors = len(names), algorithm = algorithm)
	final_lineup = build_matches(names, matchups)
	return final_lineup