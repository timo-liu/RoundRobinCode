import streamlit as st
import pandas as pd
from Utils import *
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from io import BytesIO

# region Utils
def matchups_to_pdf(df: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    story = []

    grouped = df.groupby(["Division", "Flight Number"])

    for (division, flight), table_df in grouped:
        title = Paragraph(
            f"<b>Division:</b> {division} &nbsp;&nbsp; <b>Flight:</b> {flight}",
            styles["Heading2"]
        )
        story.append(title)
        story.append(Spacer(1, 12))

        table_data = [table_df.columns.tolist()] + table_df.values.tolist()

        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("TOPPADDING", (0, 0), (-1, 0), 8),
        ]))

        story.append(table)
        story.append(PageBreak())

    doc.build(story)
    buffer.seek(0)
    return buffer.read()

# endregion Utils


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

# Variables to hold state
df = None
division_sizes = {}

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file, sep="\t")
    except Exception as e:
        st.error(f"Failed to read the file: {e}")
        df = None

if df is not None:
    st.success("File loaded successfully!")
    st.dataframe(df.head())

    # Division inputs immediately after upload
    if "Division" in df.columns:
        st.markdown("### Division Settings")

        # We need to retain division_sizes across reruns, so use st.session_state
        if "division_sizes" not in st.session_state:
            st.session_state.division_sizes = {
                division: 4 for division in sorted(df["Division"].dropna().unique())
            }

        # Display inputs and update session_state
        for division in sorted(df["Division"].dropna().unique()):
            val = st.number_input(
                label=f"People per Flight for Division {division}",
                min_value=1,
                max_value=16,
                value=st.session_state.division_sizes.get(division, 4),
                step=1,
                key=f"division_{division}_size"
            )
            st.session_state.division_sizes[division] = val

        division_sizes = st.session_state.division_sizes
        st.write("Division configuration:", division_sizes)
    else:
        st.warning("No 'Division' column found in the uploaded file.")

process_clicked = st.button("Process Matchups")

if process_clicked:
    if df is None:
        st.error("Please upload a scores file first!")
    else:
        st.info(
            f"Processing {format_type} | "
            f"Flights: {num_flights} | "
            f"Algorithm: {algorithm} | "
            f"Team Size: {team_size}"
        )

        if format_type == "Round Robin":
            # Pass a list of people per flight per division:
            # If you want to pass a dict or list depends on match_individuals API.
            # Here we pass the division_sizes.values() as before.
            final_matchups = match_individuals(
                df,
                people_per_flight=division_sizes.values() if division_sizes else [num_flights],
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

                # CSV download
                csv = combined_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download CSV",
                    csv,
                    "matchups.csv",
                    "text/csv"
                )

                # PDF download
                pdf_bytes = matchups_to_pdf(combined_df)
                st.download_button(
                    "Download PDF",
                    pdf_bytes,
                    "matchups.pdf",
                    "application/pdf"
                )
            else:
                st.warning("No matchup data to download.")

        else:
            st.warning("Eliminations are not implemented yet.")
