import streamlit as st
from sqlalchemy.orm import sessionmaker
import sqlalchemy as db
import alchemy_models
from alchemy_models import Baker
import pandas as pd

engine = alchemy_models.db_connect()
Session = sessionmaker(bind=engine)
def main():

    session = Session()

    st.sidebar.markdown("## [Home](http://knowlexchange.net)")
    st.sidebar.markdown("\n\n\n")

    baker_names = pd.read_sql(session.query(Baker).filter(Baker.site_id > 0).statement,session.bind)

    baker_selection = st.sidebar.multiselect('Select bakers to analyse', baker_names['name'])

    bakers_to_show = ""
    if len(baker_selection) > 0:
        bakers_to_show = pd.read_sql(session.query(Baker).filter(Baker.name.in_(baker_selection)).statement, session.bind)
    st.write(", ".join(baker_selection))
    st.write(bakers_to_show)


if __name__ == "__main__":
    main()
