import streamlit as st
from sqlalchemy.orm import sessionmaker
import sqlalchemy as db
import alchemy_models
from sqlalchemy import func
import altair as alt
from alchemy_models import Baker, Recipe, Series, Ingredient, IngredientType, UnitType
import pandas as pd
import numpy as np
import altair as alt
import random

engine = alchemy_models.db_connect()
Session = sessionmaker(bind=engine)


def make_plot(data):
    pts = alt.selection(type="multi", encodings=['x'])

    rect = alt.Chart(data).mark_rect().encode(
        alt.X('series number:N'),
        alt.Y('grams of sugar', bin=True),
        alt.Color('count()',
            scale=alt.Scale(scheme='greenblue'),
            legend=alt.Legend(title='Recipes')
            ),
        tooltip='ingredient'
    )

    bar = alt.Chart(data).mark_bar().encode(
        x='baker',
        y='count(recipe)',
        color=alt.condition(pts, alt.ColorValue("steelblue"), alt.ColorValue("grey"))
    ).properties(
        width=550,
        height=200
    ).add_selection(pts)

    st.altair_chart(rect)
    st.altair_chart(bar)


def main():

    session = Session()

    st.sidebar.markdown("## [Home](http://knowlexchange.net)")
    st.sidebar.markdown("\n\n\n")

    bakers_pd = pd.read_sql(session.query(Baker).filter(Baker.site_id > 0).statement,session.bind)
    baker_names = bakers_pd['name'].values.tolist()

    baker_selection = st.sidebar.multiselect(label='Select bakers to analyse', options=baker_names, default=random.choices(baker_names, k=10))

    if len(baker_selection) > 0:
        baker_recipes = pd.read_sql(session.query(
            Recipe.id.label('recipe'),
            Baker.name.label('baker'),
            Baker.role, 
            Series.series_number.label('series number'),
            IngredientType.name.label('ingredient'),
            func.sum(Ingredient.amount).label('grams of sugar'),
            UnitType.name.label('unit')
            )
                .join(Baker, Baker.id == Recipe.baker_id)
                .join(Series, Series.id == Recipe.series_id)
                .join(Ingredient, Ingredient.recipe_id == Recipe.id)
                .join(IngredientType, IngredientType.id == Ingredient.ingredient_type)
                .join(UnitType, UnitType.id == Ingredient.unit_type)
                .filter(Baker.name.in_(baker_selection))
                .filter(IngredientType.name.like("%{}%".format("sugar")))
                .filter(UnitType.name == "g")
                .group_by(Baker.id, Recipe.id, Ingredient.id, IngredientType.id)
                .statement, session.bind)

        make_plot(baker_recipes)
        st.write(baker_recipes)


    st.write(", ".join(baker_selection))




if __name__ == "__main__":
    main()
