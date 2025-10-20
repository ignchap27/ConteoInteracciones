import streamlit as st # type: ignore

pages = {
    "IAU": [
        st.Page("pages/home_page.py", title="Home"),
        st.Page("pages/model_page.py", title="Modelos"),
    ]
}

pg = st.navigation(pages, position="top")
pg.run()