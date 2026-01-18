import streamlit as st
import pandas as pd
from Utils import *

st.title("Round Robin Matcher")

example_csv = """\
Name\tDivision\tR1\tR2\tR3\tR4\tR5\tR6\tR7\tR8\tR9\tR10
Archer1\tBB\t1\t1\t1\t1\t1\t1\t1\t1\t1\t1
Archer2\tBB\t1\t1\t1\t1\t1\t1\t1\t1\t1\t1
Archer3\tFP\t1\t1\t1\t1\t1\t1\t1\t1\t1\t1
"""

st.markdown("### Expected CSV/TSV file structure:")
st.code(example_csv, language="tsv")

with st.expander("Parameter Descriptions (click to expand)"):
    st.markdown("""
    - **Number of Flights:** How many groups to split the competitors into for separate round robins.
    - **Matching Algorithm:** The method used to generate matchups (currently only 'berger' round robin).
    - **Remove Errors:** If enabled, rows with missing or invalid data will be excluded before processing.
    - **Condition:** The competition format — currently only 'Individual RR' is implemented.
    """)

# Upload file section
uploaded_file = st.file_uploader("Upload your TSV or CSV scores file", type=["csv", "tsv", "txt"])

with st.container():
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        num_flights = st.selectbox("Number of Flights", options=[1, 2, 3, 4], index=1)
    with col2:
        algorithm = st.selectbox("Matching Algorithm", options=["berger"], index=0)
    with col3:
        remove_errors = st.checkbox("Remove Errors", value=False)
    with col4:
        condition = st.selectbox("Condition", options=["Individual RR", "2 Person Teams", "3 Person Teams"], index=0)

process_clicked = st.button("Process Matchups")

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

            st.info(f"Processing with {num_flights} flights, algorithm '{algorithm}', condition '{condition}'...")

            match condition:
                case "Individual RR":
                    final_matchups = match_individuals(df, num_flights=num_flights, algorithm=algorithm)
                    final_matchups = match_individuals(df, num_flights=num_flights, algorithm=algorithm)

                    # To gather all flights into one DataFrame for download
                    all_flights_list = []

                    for division, flight_info in final_matchups.items():
                        for flight_number, flights in flight_info.items():
                            st.markdown(f"### Division: {division} | Flight Number: {flight_number}")
                            st.dataframe(flights)
                            # Add metadata columns for CSV output (optional)
                            flights_copy = flights.copy()
                            flights_copy['Division'] = division
                            flights_copy['Flight Number'] = flight_number
                            all_flights_list.append(flights_copy)

                    # Combine all flights for CSV download
                    if all_flights_list:
                        combined_df = pd.concat(all_flights_list, ignore_index=True)
                        csv = combined_df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name='matchups.csv',
                            mime='text/csv',
                        )
                    else:
                        st.warning("No matchup data to download.")
                case "2 Person Teams":
                    st.warning("2 Person Teams is not implemented yet.")
                case "3 Person Teams":
                    st.warning("3 Person Teams is not implemented yet.")
