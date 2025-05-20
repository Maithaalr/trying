import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

st.set_page_config(page_title="لوحة معلومات الموارد البشرية", layout="wide")

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Cairo&display=swap" rel="stylesheet">
    <style>
    html, body, [class*="css"]  {
        font-family: 'Cairo', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)


# ---------- إعداد الصفحة العامة ---------- #
st.set_page_config(page_title="لوحة معلومات الموارد البشرية", layout="wide")

# ---------- عرض اللوقو ---------- #
logo = Image.open("logo.png")  # تأكدي أن الصورة موجودة بنفس المجلد
st.image(logo, width=250)

st.markdown("""
    <h2 style='text-align: right; color: #1e3d59;'>لوحة معلومات الموارد البشرية</h2>
    <hr style='border: 1px solid #ccc;'>
""", unsafe_allow_html=True)

# ---------- رفع ملف Excel ---------- #
uploaded_file = st.file_uploader("ارفع ملف الموظفين", type=["xlsx"])

if uploaded_file:
    all_sheets = pd.read_excel(uploaded_file, sheet_name=None, header=4)
    selected_sheet = st.selectbox("اختر الجهة", list(all_sheets.keys()))
    df = all_sheets[selected_sheet]

    df.columns = df.columns.str.strip()

    # تنظيف الأعمدة المكررة أو الفارغة
    df = df.loc[:, ~df.columns.duplicated()]
    df = df.loc[:, df.columns.notna()]

    st.markdown(f"### 👥 بيانات الموظفين - {selected_sheet}")
    st.dataframe(df.head())

    # ---------- KPIs ---------- #
    st.markdown("""
        <div style='background-color: #1e3d59; padding: 20px; border-radius: 12px; color: white; text-align: center; font-size: 18px;'>
            <b>📊 عدد الموظفين الكلي:</b> <span style='font-size: 22px;'>{}</span><br>
            <b>✅ عدد السجلات المكتملة:</b> <span style='font-size: 22px;'>{}</span>
        </div>
        <br>
    """.format(
        df.shape[0],
        df.dropna().shape[0]
    ), unsafe_allow_html=True)

    # ---------- تحليل Missing Values ---------- #
    st.markdown("### 🔍 نسبة البيانات المفقودة")
    missing_percent = df.isnull().mean() * 100
    missing_df = missing_percent.reset_index()
    missing_df.columns = ['العمود', 'نسبة القيم المفقودة']
    fig_missing = px.bar(missing_df, x='العمود', y='نسبة القيم المفقودة',
                         title="نسبة البيانات المفقودة حسب العمود",
                         color_discrete_sequence=['#1e3d59'])
    st.plotly_chart(fig_missing, use_container_width=True)

    # ---------- تحليل التواريخ (خط زمني) ---------- #
    if 'تاريخ التعيين' in df.columns:
        df['تاريخ التعيين'] = pd.to_datetime(df['تاريخ التعيين'], errors='coerce')
        if df['تاريخ التعيين'].notna().sum() > 0:
            df['سنة التعيين'] = df['تاريخ التعيين'].dt.year
            st.markdown("### 📆 تحليل سنة التعيين")
            timeline = df['سنة التعيين'].value_counts().sort_index()
            fig_timeline = px.bar(x=timeline.index, y=timeline.values,
                                  labels={'x': 'سنة التعيين', 'y': 'عدد الموظفين'},
                                  title="عدد الموظفين حسب سنة التعيين",
                                  color_discrete_sequence=['#1e3d59'])
            st.plotly_chart(fig_timeline, use_container_width=True)
        else:
            st.warning("لا توجد تواريخ صالحة في عمود 'تاريخ التعيين'.")

    # ---------- تحليل الديانة ---------- #
    if 'الديانة' in df.columns:
        st.markdown("### ☪️ تحليل توزيع الديانات")
        religion_counts = df['الديانة'].value_counts()
        fig_religion = px.pie(values=religion_counts.values,
                              names=religion_counts.index,
                              title="نسبة توزيع الديانات",
                              color_discrete_sequence=['#1e3d59', '#6699cc'])
        st.plotly_chart(fig_religion, use_container_width=True)

    # ---------- نموذج تقديم طلب إجازة ---------- #
    st.markdown("### 📝 نموذج تقديم إجازة")
    emp_id = st.text_input("أدخل الرقم الوظيفي")
    if st.button("تقديم الطلب"):
        if emp_id in df['الرقم الوظيفي'].astype(str).values:
            emp_row = df[df['الرقم الوظيفي'].astype(str) == emp_id]
            missing_cols = emp_row.columns[emp_row.isnull().any()].tolist()
            if missing_cols:
                st.error("❌ تم رفض الطلب. البيانات التالية ناقصة:")
                for col in missing_cols:
                    st.write(f"- {col}")
                st.info("يرجى إكمال البيانات قبل تقديم الإجازة.")
            else:
                st.success("✅ تم قبول طلب الإجازة بنجاح!")
        else:
            st.warning("الرقم الوظيفي غير موجود.")

else:
    st.info("يرجى رفع ملف Excel يحتوي على بيانات الموظفين.")
