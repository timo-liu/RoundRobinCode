import pandas as pd
from typing import List
import random


def o_n_alternate2(lower_bound : int = 0, upper_bound : int = 100):
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

def o_n_alternate3(lower_bound : int = 0, upper_bound : int = 100):
	indices = list(range(lower_bound, upper_bound + 1))
	seeds = range(len(indices), 0, -1)
	lseeds, mseeds, hseeds = seeds[:upper_bound//3], seeds[upper_bound//3 : (2 * upper_bound)//3], seeds[(2 * upper_bound)//3 :]
	low, mid, high = indices[:upper_bound//3], indices[upper_bound//3 : (2 * upper_bound)//3], indices[(2 * upper_bound)//3 :]

	# keeping low the same, lowest to highest
	combined = list(zip(mid, mseeds))
	random.shuffle(combined)
	mid, mseeds = map(list, zip(*combined))
	# sorting the highs in descending order (best first)
	high = reversed(high)

	final_indices = []
	final_seeds = []

	for i in range(max(len(low), len(mid), len(high))):
		for l in [(low, lseeds), (high,hseeds), (mid, mseeds)]:
			if i < len(l):
				final_indices.append(l[0][i])
				final_seeds.append(l[1][i])
	return final_indices, final_seeds

def create_teams(names: List[str], matching_indices : List[int], seeds : List[int], team_size : int = 2):

	final_teams = []

	match team_size:
		case 2:
			assert len(matching_indices) % 2 == 0, "Do something to make sure the matching indices are even."
			if len(names) % 2 != 0:
				names.insert(0, "Gunrock")
				seeds.insert(0, "−∞")
			for i in range(1, len(matching_indices), 2):
				pair = f"{names[matching_indices[i]]} ({seeds[matching_indices[i]]} and {seeds[matching_indices[i+1]]} ({seeds[matching_indices[i+1]]}))"
				final_teams.append(pair)

		case 3:
			if len(names) % 3 != 0:
				if len(names) % 3 == 1:
					# last two teams will be 2 person teams
					for i in range(1, len(matching_indices) - 4, 3):
						triplet = f"{names[matching_indices[i]]} ({seeds[matching_indices[i]]}), {names[matching_indices[i + 1]]} ({seeds[matching_indices[i + 1]]}), {names[matching_indices[i + 2]]} ({seeds[matching_indices[i + 2]]})"
						final_teams.append(triplet)
					last_four = matching_indices[-4:]
					final_teams.append(
						f"{names[last_four[0]]} ({seeds[last_four[0]]}) and {names[last_four[1]]} ({seeds[last_four[1]]})")
					final_teams.append(
						f"{names[last_four[2]]} ({seeds[last_four[2]]}) and {names[last_four[3]]} ({seeds[last_four[3]]})")
				elif len(names) % 3 == 2:
					# last 2 people are in their own team
					for i in range(1, len(matching_indices) - 2, 3):
						triplet = f"{names[matching_indices[i]]} ({seeds[matching_indices[i]]}), {names[matching_indices[i + 1]]} ({seeds[matching_indices[i + 1]]}), {names[matching_indices[i + 2]]} ({seeds[matching_indices[i + 2]]})"
						final_teams.append(triplet)
					last_two = matching_indices[-2:]
					final_teams.append(
						f"{names[last_two[0]]} ({seeds[last_two[0]]}) and {names[last_two[1]]} ({seeds[last_two[1]]})")
	return final_teams

def match_teams(scores: pd.DataFrame, people_per_team : int = 2) -> pd.DataFrame:
	divisions = scores["Division"].unique()
	flight_dict = {}
	for division in divisions:
		flight_dict[division] = {}
		if "QualScore" not in scores.columns:
			round_cols = [f"R{i}" for i in range(1, 11)]
			section = scores[scores["Division"] == division].copy()
			section["QualScore"] = section[round_cols].sum(axis=1)
			section = section.drop(columns=round_cols)
		section = scores[scores["Division"] == division].copy()
		section = section.sort_values(by=["QualScore"], ascending=True)
