import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
import base64

# Define the valid affiliations
valid_affiliations = ["Shivaji University", "Saveetha University"]

# Define the exclusion keywords
exclusion_keywords = ["College", "Affiliated to"]

# Streamlit UI
st.title("Research Author Affiliation Processor")
st.write("""
Upload a CSV file containing an **'Authors with affiliations'** column.
This will extract the corresponding author and affiliation  
for Shivaji University or Saveetha University entries.
""")

# File uploader
uploaded_file = st.file_uploader("📂 Upload CSV", type="csv")

def process_file(file) -> pd.DataFrame | None:
    try:
        df = pd.read_csv(file)

        # Ensure the column exists
        if 'Authors with affiliations' not in df.columns:
            st.error("❌ CSV is missing the `'Authors with affiliations'` column.")
            return None

        # Prep output columns
        df['Corresponding Author'] = ""
        df['Corresponding Affiliation'] = ""

        # Iterate rows
        for idx, row in df.iterrows():
            raw = row['Authors with affiliations']

            # Only split if it's a non-null string
            if isinstance(raw, str):
                pairs = raw.split(';')
            else:
                pairs = []

            valid_authors = []
            for token in pairs:
                name_aff = token.strip().split(',', 1)
                if len(name_aff) != 2:
                    continue
                name, aff = name_aff
                aff = aff.strip()

                # Saveetha University always allowed
                if "Saveetha University" in aff:
                    valid_authors.append((name.strip(), aff))
                # Other valid affiliations, excluding keywords
                elif any(v in aff for v in valid_affiliations):
                    if not any(ex in aff for ex in exclusion_keywords):
                        valid_authors.append((name.strip(), aff))

            # Last valid entry → corresponding author
            if valid_authors:
                ca, caf = valid_authors[-1]
                df.at[idx, 'Corresponding Author'] = ca
                df.at[idx, 'Corresponding Affiliation'] = caf

        return df

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
        return None

# Process & display
if uploaded_file:
    st.info("⏳ Processing...")
    result_df = process_file(uploaded_file)
    if result_df is not None:
        st.success("✅ Done!")
        st.dataframe(result_df)

        # Download button
        base = uploaded_file.name.rsplit('.', 1)[0]
        out_name = f"{base}_corresponding_updated.csv"
        csv_data = result_df.to_csv(index=False)
        st.download_button("📥 Download CSV", csv_data, file_name=out_name, mime="text/csv")
else:
    st.info("Please upload a CSV to begin.")

# Footer / support
st.markdown("---")
st.info("Created by Dr. Satyajeet Patil")
st.markdown("[Visit my Python apps](https://patilsatyajeet.wixsite.com/home/python)")

with st.expander("🤝 Support Our Research"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### UPI Payment")
        def make_qr(data):
            qr = qrcode.make(data)
            buf = BytesIO()
            qr.save(buf, format="PNG")
            buf.seek(0)
            return buf

        upi = "upi://pay?pa=satyajeet1396@oksbi&pn=Satyajeet Patil&cu=INR"
        buf = make_qr(upi)
        img_b64 = base64.b64encode(buf.getvalue()).decode()
        st.markdown("Scan to pay: **satyajeet1396@oksbi**")
        st.markdown(f'<img src="data:image/png;base64,{img_b64}" width="200"/>', unsafe_allow_html=True)

    with col2:
        st.markdown("#### Buy Me a Coffee")
        st.markdown(
            """
            <a href="https://www.buymeacoffee.com/researcher13" target="_blank">
              <img src="https://img.buymeacoffee.com/button-api/?text=Support our Research&emoji=&slug=researcher13" alt="Support our Research"/>
            </a>
            """, unsafe_allow_html=True
        )
