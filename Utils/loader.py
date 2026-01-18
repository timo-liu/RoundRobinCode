import pandas as pd

def load_scores(path: str = "Data/scores.tsv", remove_errors : bool = False) -> pd.DataFrame:
	"""
	Loads and validates scores for round robin
	:param path:
	:return:
	"""
	scores = pd.read_csv(path, sep="\t")
	if remove_errors:
		scores = validate(scores, remove_errors=remove_errors)
	return scores

def validate(scores : pd.DataFrame, remove_errors: bool = False):
	"""
	Validates scores for round robin
	:param scores:
	:param remove_errors:
	:return:
	"""
	remove_indices = []

	for index, row in scores.iterrows():
		if any(pd.isna(row[f"R{i}"]) for i in range(1, 11)):
			print(f"{row["Name"]} appears to be missing scores. You should check that.")
			if remove_errors:
				remove_indices.append(index)
	return scores.drop(index=remove_indices)