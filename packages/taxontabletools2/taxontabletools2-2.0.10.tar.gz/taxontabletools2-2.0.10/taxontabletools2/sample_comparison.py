import pandas as pd
import numpy as np
from pathlib import Path
from taxontabletools2.utilities import simple_taxontable
from taxontabletools2.utilities import filter_taxontable
import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn3
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn3
from io import BytesIO

def venn(path_to_outdirs, taxon_table_xlsx, taxon_table_df, samples, metadata_df, selected_metadata, traits_df, selected_traits, users_settings, tool_settings):
    ## create copies of the dataframes
    taxon_table_df = taxon_table_df.copy()
    metadata_df = metadata_df.copy()
    traits_df = traits_df.copy()

    ## collect tool-specific settings
    selected_metadata = tool_settings['selected_metadata']
    taxonomic_level = tool_settings['taxonomic_level']

    ## collect the number of categories
    metadata_df = metadata_df[['Sample', selected_metadata]]
    categories = [i for i in metadata_df[selected_metadata].drop_duplicates().values.tolist() if i != '']
    n_categories = len(categories)

    if n_categories == 2:
        samples_a = metadata_df.loc[metadata_df[selected_metadata] == categories[0]]['Sample'].values.tolist()
        df_a = filter_taxontable(taxon_table_df, samples_a, taxonomic_level)
        species_a = set(df_a[taxonomic_level].values.tolist())
        samples_b = metadata_df.loc[metadata_df[selected_metadata] == categories[1]]['Sample'].values.tolist()
        df_b = filter_taxontable(taxon_table_df, samples_b, taxonomic_level)
        species_b = set(df_b[taxonomic_level].values.tolist())

        a_only = species_a - species_b
        print(a_only)
        n_a_only = len(a_only)
        shared = species_a & species_b
        print(shared)
        n_shared = len(shared)
        b_only = species_b - species_a
        print(b_only)
        n_b_only = len(b_only)

        # Create the Venn diagram
        plt.figure(figsize=(8, 8))
        venn = venn2(subsets=(n_a_only, n_b_only, n_shared), set_labels=(categories[0], categories[1]))

        # Adjust the font size of set labels
        venn.get_label_by_id('A').set_fontsize(12)  # Font size for "Category A"
        venn.get_label_by_id('B').set_fontsize(12)  # Font size for "Category B"
        # Adjust the font size of subset labels (the numbers inside the circles)
        for text in venn.subset_labels:
            if text:  # Check if the label exists (some subsets might be None)
                text.set_fontsize(users_settings['font_size'])

        return plt

    elif n_categories == 3:
        samples_a = metadata_df.loc[metadata_df[selected_metadata] == categories[0]]['Sample'].values.tolist()
        df_a = filter_taxontable(taxon_table_df, samples_a, taxonomic_level)
        species_a = set(df_a[taxonomic_level].values.tolist())

        samples_b = metadata_df.loc[metadata_df[selected_metadata] == categories[1]]['Sample'].values.tolist()
        df_b = filter_taxontable(taxon_table_df, samples_b, taxonomic_level)
        species_b = set(df_b[taxonomic_level].values.tolist())

        samples_c = metadata_df.loc[metadata_df[selected_metadata] == categories[2]]['Sample'].values.tolist()
        df_c = filter_taxontable(taxon_table_df, samples_c, taxonomic_level)
        species_c = set(df_c[taxonomic_level].values.tolist())

        # Calculate the different subsets
        a_only = species_a - (species_b | species_c)
        b_only = species_b - (species_a | species_c)
        c_only = species_c - (species_a | species_b)
        ab_shared = (species_a & species_b) - species_c
        ac_shared = (species_a & species_c) - species_b
        bc_shared = (species_b & species_c) - species_a
        abc_shared = species_a & species_b & species_c

        # Create the Venn diagram
        plt.figure(figsize=(8, 8))
        venn = venn3(subsets=(
        len(a_only), len(b_only), len(ab_shared), len(c_only), len(ac_shared), len(bc_shared), len(abc_shared)),
                     set_labels=(categories[0], categories[1], categories[2]))

        # Adjust the font size of set labels
        venn.get_label_by_id('A').set_fontsize(12)  # Font size for "Category A"
        venn.get_label_by_id('B').set_fontsize(12)  # Font size for "Category B"
        venn.get_label_by_id('C').set_fontsize(12)  # Font size for "Category C"

        # Adjust the font size of subset labels (the numbers inside the circles)
        for text in venn.subset_labels:
            if text:  # Check if the label exists (some subsets might be None)
                text.set_fontsize(users_settings['font_size'])

        return plt

    elif n_categories == 1:
        st.error(f'Venn diagrams only work with 2-3 categories. The metadata {selected_metadata} has one category.')
    else:
        st.error(
            f'Venn diagrams only work with 2-3 categories. The metadata {selected_metadata} has {n_categories} categories.')



