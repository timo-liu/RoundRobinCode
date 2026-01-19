import pandas as pd
from typing import List, Dict
import random

def o_n_alternate2_zero_based(num_players: int):
    """
    Returns a 0-based alternating list of indices for pairing high and low seeds.
    E.g. for num_players=6: [0, 5, 1, 4, 2, 3]
    Seeds are 1-based ranks: seed 1 is best player (index 1 if Gunrock inserted at 0).
    """
    indices = []
    low, high = 0, num_players - 1
    while low <= high:
        indices.append(low)
        if low != high:
            indices.append(high)
        low += 1
        high -= 1

    seeds = reversed([i + 1 for i in range(num_players)])  # Seeds from 1 to num_players

    return indices, seeds

def o_n_alternate3(lower_bound: int = 0, upper_bound: int = 100):
    indices = list(range(lower_bound, upper_bound + 1))
    seeds = list(range(len(indices), 0, -1))
    lseeds = seeds[:upper_bound // 3]
    mseeds = seeds[upper_bound // 3 : (2 * upper_bound) // 3]
    hseeds = seeds[(2 * upper_bound) // 3 :]

    low = indices[:upper_bound // 3]
    mid = indices[upper_bound // 3 : (2 * upper_bound) // 3]
    high = indices[(2 * upper_bound) // 3 :]

    # Shuffle mid seeds with mid indices
    combined = list(zip(mid, mseeds))
    random.shuffle(combined)
    mid, mseeds = map(list, zip(*combined))

    # Reverse high to get descending order (best first)
    high = list(reversed(high))

    final_indices = []
    final_seeds = []

    for i in range(max(len(low), len(mid), len(high))):
        for l_indices, l_seeds in [(low, lseeds), (high, hseeds), (mid, mseeds)]:
            if i < len(l_indices):
                final_indices.append(l_indices[i])
                final_seeds.append(l_seeds[i])
    return final_indices, final_seeds

def create_teams(names: List[str], matching_indices: List[int], seeds: List[int], team_size: int = 2):

    final_teams = []

    match team_size:
        case 2:
            # If odd number of players, insert Gunrock placeholder at front (index 0)
            if len(names) % 2 != 0:
                names.insert(0, "Gunrock")
                seeds.insert(0, "−∞")  # You can use 0 or -inf as placeholder seed

            assert len(matching_indices) % 2 == 0, "Number of matching indices must be even."

            for i in range(0, len(matching_indices), 2):
                p1 = matching_indices[i]
                p2 = matching_indices[i + 1]
                pair = f"{names[p1]} ({seeds[p1]}) and {names[p2]} ({seeds[p2]})"
                print(pair)
                final_teams.append(pair)

        case 3:
            # You can apply similar zero-based logic here if needed
            if len(names) % 3 != 0:
                if len(names) % 3 == 1:
                    for i in range(0, len(matching_indices) - 4, 3):
                        triplet = (
                            f"{names[matching_indices[i]]} ({seeds[matching_indices[i]]}), "
                            f"{names[matching_indices[i + 1]]} ({seeds[matching_indices[i + 1]]}), "
                            f"{names[matching_indices[i + 2]]} ({seeds[matching_indices[i + 2]]})"
                        )
                        final_teams.append(triplet)
                    last_four = matching_indices[-4:]
                    final_teams.append(
                        f"{names[last_four[0]]} ({seeds[last_four[0]]}) and {names[last_four[1]]} ({seeds[last_four[1]]})"
                    )
                    final_teams.append(
                        f"{names[last_four[2]]} ({seeds[last_four[2]]}) and {names[last_four[3]]} ({seeds[last_four[3]]})"
                    )
                elif len(names) % 3 == 2:
                    for i in range(0, len(matching_indices) - 2, 3):
                        triplet = (
                            f"{names[matching_indices[i]]} ({seeds[matching_indices[i]]}), "
                            f"{names[matching_indices[i + 1]]} ({seeds[matching_indices[i + 1]]}), "
                            f"{names[matching_indices[i + 2]]} ({seeds[matching_indices[i + 2]]})"
                        )
                        final_teams.append(triplet)
                    last_two = matching_indices[-2:]
                    final_teams.append(
                        f"{names[last_two[0]]} ({seeds[last_two[0]]}) and {names[last_two[1]]} ({seeds[last_two[1]]})"
                    )
            else:
                # If multiple of 3, group in triplets normally
                for i in range(0, len(matching_indices), 3):
                    triplet = (
                        f"{names[matching_indices[i]]} ({seeds[matching_indices[i]]}), "
                        f"{names[matching_indices[i + 1]]} ({seeds[matching_indices[i + 1]]}), "
                        f"{names[matching_indices[i + 2]]} ({seeds[matching_indices[i + 2]]})"
                    )
                    final_teams.append(triplet)

    return final_teams

def match_teams(scores: pd.DataFrame, people_per_team: int = 2) -> Dict[str, List[str]]:
    divisions = scores["Division"].unique()
    flight_dict = {}
    for division in divisions:
        if "QualScore" not in scores.columns:
            round_cols = [f"R{i}" for i in range(1, 11)]
            section = scores[scores["Division"] == division].copy()
            section["QualScore"] = section[round_cols].sum(axis=1)
            section = section.drop(columns=round_cols)
        else:
            section = scores[scores["Division"] == division].copy()

        section = section.sort_values(by=["QualScore"], ascending=True)
        names = section["Name"].copy().tolist()

        # Insert Gunrock if odd and 2 person teams
        if people_per_team == 2 and len(names) % 2 != 0:
            names.insert(0, "Gunrock")

        num_players = len(names)

        if people_per_team == 2:
            matching_indices, matching_seeds = o_n_alternate2_zero_based(num_players)
        elif people_per_team == 3:
            matching_indices, matching_seeds = o_n_alternate3(0, num_players - 1)
        else:
            raise NotImplementedError("Only 2 and 3 person teams are supported.")

        # For 2 teams, insert seed 0 or -inf for Gunrock
        matching_seeds = [seed if seed != 1 or names[idx] != "Gunrock" else 0 for idx, seed in enumerate(matching_seeds)]

        # Insert seed for Gunrock if not already (handle in create_teams)
        if "Gunrock" in names and "−∞" not in matching_seeds:
            idx_gunrock = names.index("Gunrock")
            matching_seeds[idx_gunrock] = "−∞"

        final_teams = create_teams(names, matching_indices, matching_seeds, people_per_team)
        flight_dict[division] = final_teams
    return flight_dict
