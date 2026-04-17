import streamlit as st
from fpdf import FPDF
from io import BytesIO
from datetime import date

# --- PDF GENERATION CLASS ---
class SpecialNotePDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 16)
        self.cell(0, 10, 'PROCUREMENT SPECIAL NOTE - AUDIT READY', 0, 1, 'C')
        self.set_draw_color(0, 87, 155)
        self.line(10, 22, 200, 22)
        self.ln(10)

    def section_header(self, label):
        self.set_font('Helvetica', 'B', 12)
        self.set_fill_color(230, 240, 255)
        self.cell(0, 8, f" {label}", 0, 1, 'L', fill=True)
        self.ln(2)

    def write_field(self, label, value):
        self.set_font('Helvetica', 'B', 10)
        self.write(7, f"{label}: ")
        self.set_font('Helvetica', '', 10)
        self.write(7, f"{value}\n")
        self.ln(2)

# --- UI CONFIGURATION ---
st.set_page_config(page_title="Special Note Builder", page_icon="📝")

st.title("🛡️ Procurement Special Note")
st.info("Complete this form to generate the audit document for AI validation.")

# --- FORM ---
with st.form("special_note_form"):
    # 1. Price Analysis & Currency
    st.subheader("1. Price Analysis")
    
    currency = st.selectbox("Select Currency", ["INR", "USD", "GBP", "EUR", "CNY"])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        # 'label_visibility' hidden removes the label but keeps accessibility
        # 'step=None' or leaving it out removes the +/- buttons in some browsers
        lpp = st.number_input(f"Last Purchase Price ({currency})", min_value=0.0, format="%.2f")
    with col2:
        lpp_date = st.date_input("LPP Date", value=date.today())
    with col3:
        curr_price = st.number_input(f"Current Price ({currency})", min_value=0.0, format="%.2f")

    # Auto-calculate variance
    variance = 0.0
    if lpp > 0:
        variance = ((curr_price - lpp) / lpp) * 100
    
    st.write(f"**Calculated Variance:** {variance:.2f}%")
    if variance > 10:
        st.error(f"⚠️ High Variance detected: {variance:.2f}%")
    elif variance > 0:
        st.warning(f"Price Increase: {variance:.2f}%")

    # 2. Justifications
    st.subheader("2. Justifications & Recommendations")
    l1_just = st.text_area("Justification for selecting other than L1 (If applicable)")
    
    col_a, col_b = st.columns(2)
    with col_a:
        end_user_rec = st.checkbox("End User Recommendation Received?")
    with col_b:
        repeat_order = st.radio("Is this a Repeat Order?", ["No", "Yes"])

    single_quote = st.text_area("Single Quote Justification (If < 3 quotes)")
    oem_rec = st.text_area("Brand Specific & OEM Recommendation")
    urgency = st.text_area("Urgency Justification (Time constraints)")

    # 3. Final Note
    st.subheader("3. Detailed Special Note")
    special_note_text = st.text_area("Final Summary (Max 500 Words)", height=200)

    submitted = st.form_submit_button("Generate & Audit PDF")

# --- POST-SUBMISSION LOGIC ---
if submitted:
    pdf = SpecialNotePDF()
    pdf.add_page()
    
    pdf.section_header("I. Price & LPP Data")
    pdf.write_field("Currency", currency)
    pdf.write_field("Last Purchase Price", f"{lpp:,.2f}")
    pdf.write_field("LPP Date", f"{lpp_date}")
    pdf.write_field("Current Price", f"{curr_price:,.2f}")
    pdf.write_field("Price Variance", f"{variance:.2f}%")
    
    pdf.section_header("II. Selection Justifications")
    pdf.write_field("Selecting other than L1", l1_just if l1_just else "N/A")
    pdf.write_field("End User Recommended", "Yes" if end_user_rec else "No")
    pdf.write_field("Repeat Order", repeat_order)
    pdf.write_field("Single Quote Reason", single_quote if single_quote else "N/A")
    
    pdf.section_header("III. Technical & OEM")
    pdf.write_field("OEM/Brand Rec", oem_rec if oem_rec else "N/A")
    pdf.write_field("Urgency Reason", urgency if urgency else "Normal Proc. Cycle")
    
    pdf.section_header("IV. Buyer's Special Note")
    pdf.set_font('Helvetica', '', 10)
    pdf.multi_cell(0, 7, special_note_text)

    pdf_output = pdf.output(dest='S').encode('latin-1')
    
    st.success("✅ Form validated. Ready for Audit.")
    st.download_button(
        label="📥 Download Special Note PDF",
        data=pdf_output,
        file_name=f"Audit_Note_{date.today()}.pdf",
        mime="application/pdf"
    )