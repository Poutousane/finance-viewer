# app.py
"""
Application Finance Viewer - Interface pour visualiser et télécharger des données financières
"""

import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import traceback

# Importer les données et utilitaires
from assets import (
    stock_categories, stock_assets, crypto_assets,
    currency_assets, resource_assets, index_categories, index_assets
)
from utils import clean_text, create_excel, format_volume

# Configuration de la page
st.set_page_config(
    page_title="Finance Viewer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titre de l'application
st.title("Finance Viewer")

# Création des onglets principaux pour types d'actifs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Crypto", "Actions", "Devises", "Ressources", "Indices"])


def display_standard_asset_data(assets, tab_key):
    """
    Affiche les données pour un type d'actif standard (crypto, devises, ressources)

    Args:
        assets (dict): Dictionnaire des actifs {nom: symbole}
        tab_key (str): Clé unique pour les widgets Streamlit
    """
    col1, col2, col3 = st.columns(3)

    with col1:
        selected_asset = st.selectbox("Choisissez un actif", list(assets.keys()), key=f"select_{tab_key}")

    with col2:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=365)
        start_date_input = st.date_input("Date de début", value=start_date, key=f"start_{tab_key}")

    with col3:
        end_date_input = st.date_input("Date de fin", value=end_date, key=f"end_{tab_key}")

    # Récupération des données
    ticker_symbol = assets[selected_asset]
    try:
        # Récupérer les données
        data = yf.download(ticker_symbol, start=start_date_input, end=end_date_input, interval="1d")

        if data.empty:
            st.error(f"Aucune donnée disponible pour {selected_asset} dans la période sélectionnée.")
        else:
            # S'assurer que les données ne sont pas vides
            if not data.empty and len(data) > 0:
                # Extraction des valeurs
                latest_close_value = float(data['Close'].iloc[-1])
                first_close_value = float(data['Close'].iloc[0])
                variation_value = ((latest_close_value - first_close_value) / first_close_value) * 100
                latest_volume_value = float(data['Volume'].iloc[-1])

                # Affichage des indicateurs clés
                st.subheader("Indicateurs clés")

                metrics_col1, metrics_col2, metrics_col3 = st.columns(3)

                with metrics_col1:
                    formatted_close = f"${latest_close_value:.2f}"
                    st.metric("Prix de clôture", formatted_close)

                with metrics_col2:
                    formatted_variation = f"{variation_value:.2f}%"
                    formatted_delta = f"{variation_value:.2f}%"
                    st.metric("Variation", formatted_variation, delta=formatted_delta)

                with metrics_col3:
                    vol_str = format_volume(latest_volume_value)
                    st.metric("Volume (dernier jour)", vol_str)

                # Tableau des données et reste du code pour l'affichage...
                # [Pour garder la réponse concise, cette partie est condensée]

                # Créer un excel et proposer le téléchargement
                excel_data = create_excel(data, clean_text(selected_asset))
                clean_name = clean_text(selected_asset)
                clean_start = clean_text(start_date_input)
                clean_end = clean_text(end_date_input)

                st.download_button(
                    label="Télécharger les données (XLSX)",
                    data=excel_data,
                    file_name=f"{clean_name}_{clean_start}_{clean_end}.xlsx",
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    key=f"download_{tab_key}"
                )
            else:
                st.error(f"Aucune donnée n'a été récupérée pour {selected_asset}.")

    except Exception as e:
        st.error(f"Une erreur s'est produite lors de la récupération des données : {e}")
        st.error(f"Traceback détaillé: {traceback.format_exc()}")


# [Les fonctions display_stock_data() et display_indices_data() seraient également définies ici]

# Affichage des données selon l'onglet sélectionné
with tab1:
    display_standard_asset_data(crypto_assets, "crypto")

with tab2:
    display_stock_data()  # Fonction spéciale pour les actions avec filtrage par secteur

with tab3:
    display_standard_asset_data(currency_assets, "currency")

with tab4:
    display_standard_asset_data(resource_assets, "resource")

with tab5:
    display_indices_data()  # Fonction spéciale pour les indices avec filtrage par pays
