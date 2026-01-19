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

def create_teams(
    names: List[str],
    matching_indices: List[int],
    seeds: List[int],  # seeds here unused for team seeds; kept for compatibility
    qual_scores: List[float],
    team_size: int = 2
) -> List[str]:

    teams_with_scores = []

    match team_size:
        case 2:
            if len(names) % 2 != 0:
                names.insert(0, "Gunrock")
                seeds.insert(0, "−∞")
                qual_scores.insert(0, 0)

            assert len(matching_indices) % 2 == 0, "Number of matching indices must be even."

            for i in range(0, len(matching_indices), 2):
                p1 = matching_indices[i]
                p2 = matching_indices[i + 1]

                team_qual_sum = qual_scores[p1] + qual_scores[p2]
                team_str = (
                    f"{names[p1]} ({seeds[p1]}) and {names[p2]} ({seeds[p2]})"
                )
                teams_with_scores.append((team_str, team_qual_sum))

        case 3:
            if len(names) % 3 != 0:
                if len(names) % 3 == 1:
                    for i in range(0, len(matching_indices) - 4, 3):
                        p1, p2, p3 = matching_indices[i], matching_indices[i + 1], matching_indices[i + 2]
                        team_qual_sum = qual_scores[p1] + qual_scores[p2] + qual_scores[p3]
                        team_str = (
                            f"{names[p1]} ({seeds[p1]}), {names[p2]} ({seeds[p2]}), {names[p3]} ({seeds[p3]})"
                        )
                        teams_with_scores.append((team_str, team_qual_sum))

                    last_four = matching_indices[-4:]
                    for i in range(0, 4, 2):
                        p1, p2 = last_four[i], last_four[i + 1]
                        team_qual_sum = qual_scores[p1] + qual_scores[p2]
                        team_str = f"{names[p1]} ({seeds[p1]}) and {names[p2]} ({seeds[p2]})"
                        teams_with_scores.append((team_str, team_qual_sum))

                elif len(names) % 3 == 2:
                    for i in range(0, len(matching_indices) - 2, 3):
                        p1, p2, p3 = matching_indices[i], matching_indices[i + 1], matching_indices[i + 2]
                        team_qual_sum = qual_scores[p1] + qual_scores[p2] + qual_scores[p3]
                        team_str = (
                            f"{names[p1]} ({seeds[p1]}), {names[p2]} ({seeds[p2]}), {names[p3]} ({seeds[p3]})"
                        )
                        teams_with_scores.append((team_str, team_qual_sum))

                    last_two = matching_indices[-2:]
                    p1, p2 = last_two[0], last_two[1]
                    team_qual_sum = qual_scores[p1] + qual_scores[p2]
                    team_str = f"{names[p1]} ({seeds[p1]}) and {names[p2]} ({seeds[p2]})"
                    teams_with_scores.append((team_str, team_qual_sum))

            else:
                for i in range(0, len(matching_indices), 3):
                    p1, p2, p3 = matching_indices[i], matching_indices[i + 1], matching_indices[i + 2]
                    team_qual_sum = qual_scores[p1] + qual_scores[p2] + qual_scores[p3]
                    team_str = (
                        f"{names[p1]} ({seeds[p1]}), {names[p2]} ({seeds[p2]}), {names[p3]} ({seeds[p3]})"
                    )
                    teams_with_scores.append((team_str, team_qual_sum))

    # Sort teams by total QualScore ascending (lowest total = seed 1)
    teams_with_scores.sort(key=lambda x: x[1], reverse=True)

    # Assign seeds and format output strings with seed info
    final_teams = []
    for seed, (team_str, total_points) in enumerate(teams_with_scores, start=1):
        final_teams.append(f"{team_str} [Total Points: {total_points} (Seed {seed})]")

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
        qual_scores = section["QualScore"].copy().tolist()

        if people_per_team == 2 and len(names) % 2 != 0:
            names.insert(0, "Gunrock")
            qual_scores.insert(0, 0)

        num_players = len(names)

        if people_per_team == 2:
            matching_indices, matching_seeds = o_n_alternate2_zero_based(num_players)
        elif people_per_team == 3:
            matching_indices, matching_seeds = o_n_alternate3(0, num_players - 1)
        else:
            raise NotImplementedError("Only 2 and 3 person teams are supported.")
        matching_seeds = [seed if seed != 1 or names[idx] != "Gunrock" else 0 for idx, seed in enumerate(matching_seeds)]
        if "Gunrock" in names and "−∞" not in matching_seeds:
            idx_gunrock = names.index("Gunrock")
            matching_seeds[idx_gunrock] = "−∞"

        final_teams = create_teams(names, matching_indices, matching_seeds, qual_scores, people_per_team)
        flight_dict[division] = final_teams

    return flight_dict
