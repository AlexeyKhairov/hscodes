import streamlit as st
import pandas as pd

# Load the HS code database from the CSV file
@st.cache_data  # Cache the database for faster access
def load_hs_database(csv_file):
    try:
        df = pd.read_csv(csv_file)
        if not {'HS2', 'HS4', 'HS6'}.issubset(df.columns):
            raise ValueError("CSV file must contain 'HS2', 'HS4', and 'HS6' columns.")
        return df
    except Exception as e:
        st.error(f"Error loading database: {e}")
        return None

# Function to transfigure HS codes
def transfigure_hs_codes(input_codes, hs_db):
    results = []
    input_codes = [code.strip() for code in input_codes.split()]  # Split input by spaces
    for code in input_codes:
        if len(code) == 2:
            matches = hs_db[hs_db['HS2'] == code]
        elif len(code) == 4:
            matches = hs_db[hs_db['HS4'] == code]
        else:
            st.warning(f"Invalid code length: {code}. Skipping...")
            continue
        if not matches.empty:
            results.extend(matches['HS6'].tolist())
        else:
            st.warning(f"No matching 6-digit HS codes found for {code}.")
    return results

# Main function to create the Streamlit app
def main():
    st.title("HS Code Transfiguration Tool")

    # Load the HS code database
    csv_file = "hs_code_database.csv"
    hs_db = load_hs_database(csv_file)
    if hs_db is None:
        st.stop()

    # Input text field
    input_codes = st.text_input("Enter 2 or 4-digit HS codes (separated by spaces):", "")

    # Button to trigger transfiguration
    if st.button("Расхлопнуть"):
        if not input_codes.strip():
            st.warning("Please enter at least one HS code.")
        else:
            results = transfigure_hs_codes(input_codes, hs_db)
            if results:
                st.subheader("Expanded 6-digit HS Codes:")
                result_text = "\n".join(results)
                st.text_area("Output:", value=result_text, height=300)
            else:
                st.info("No matching 6-digit HS codes found.")

if __name__ == "__main__":
    main()