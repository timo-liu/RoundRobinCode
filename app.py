import streamlit as st
import pandas as pd
from Utils import *

st.title("Round Robin Matcher")

# =========================
# Examples
# =========================
example_csv = """\
Name\tDivision\tR1\tR2\tR3\tR4\tR5\tR6\tR7\tR8\tR9\tR10
Archer1\tBB\t1\t1\t1\t1\t1\t1\t1\t1\t1\t1
Archer2\tBB\t1\t1\t1\t1\t1\t1\t1\t1\t1\t1
Archer3\tFP\t1\t1\t1\t1\t1\t1\t1\t1\t1\t1
"""

quals_example = """\
Name\tDivision\tQualScore
Archer1\tBB\t1
Archer2\tBB\t1
Archer3\tFP\t1
"""

st.markdown("### Expected CSV/TSV file structure:")
st.code(example_csv, language="tsv")
st.markdown("### Alternative CSV/TSV file structure:")
st.code(quals_example, language="tsv")

# =========================
# Parameters Info
# =========================
with st.expander("Parameter Descriptions (click to expand)"):
    st.markdown("""
    - **Format:** Competition structure (Round Robin or Eliminations).
    - **Number of Flights:** Number of groups for Round Robin.
    - **Matching Algorithm:** Method used to generate matchups.
    - **People per Team:** Team size for eliminations.
    - **Remove Errors:** Drop invalid rows before processing.
    """)

# =========================
# Upload
# =========================
uploaded_file = st.file_uploader(
    "Upload your TSV or CSV scores file",
    type=["csv", "tsv", "txt"]
)

# =========================
# TOP-LEVEL FORMAT SELECTOR (CENTERED)
# =========================
st.markdown("---")
format_col = st.columns([1, 2, 1])[1]
with format_col:
    format_type = st.selectbox(
        "Competition Format",
        options=["Round Robin", "Eliminations"],
        index=0
    )
st.markdown("---")

# =========================
# OPTIONS
# =========================
with st.container():
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        num_flights = st.number_input(
            "People per Flight",
            min_value=1,
            max_value=4,
            value=2,
            step=1,
            disabled=(format_type != "Round Robin")
        )

    with col2:
        algorithm = st.selectbox(
            "Matching Algorithm",
            options=["berger"],
            index=0,
            disabled=(format_type != "Round Robin")
        )

    with col3:
        remove_errors = st.checkbox("Remove Errors", value=False)

    with col4:
        if format_type == "Eliminations":
            team_size = st.selectbox(
                "People per Team",
                options=[1, 2, 3, 4],
                index=1
            )
        else:
            team_size = None
            st.markdown("")

process_clicked = st.button("Process Matchups")

# =========================
# PROCESSING
# =========================
if process_clicked:
    if uploaded_file is None:
        st.error("Please upload a scores file first!")
    else:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_csv(uploaded_file, sep="\t")
        except Exception as e:
            st.error(f"Failed to read the file: {e}")
        else:
            st.success("File loaded successfully!")
            st.dataframe(df.head())

            st.info(
                f"Processing {format_type} | "
                f"Flights: {num_flights} | "
                f"Algorithm: {algorithm} | "
                f"Team Size: {team_size}"
            )

            if format_type == "Round Robin":
                final_matchups = match_individuals(
                    df,
                    people_per_flight=num_flights,
                    algorithm=algorithm
                )

                all_flights_list = []

                for division, flight_info in final_matchups.items():
                    for flight_number, flights in flight_info.items():
                        st.markdown(
                            f"### Division: {division} | Flight: {flight_number}"
                        )
                        st.dataframe(flights)

                        flights_copy = flights.copy()
                        flights_copy["Division"] = division
                        flights_copy["Flight Number"] = flight_number
                        all_flights_list.append(flights_copy)

                if all_flights_list:
                    combined_df = pd.concat(all_flights_list, ignore_index=True)
                    csv = combined_df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "Download CSV",
                        csv,
                        "matchups.csv",
                        "text/csv"
                    )
                else:
                    st.warning("No matchup data to download.")

            else:
                st.warning("Eliminations are not implemented yet.")
