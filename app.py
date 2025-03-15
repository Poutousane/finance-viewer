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
                    formatted_close = f"${latest_close_value:.2f}" if tab_key != "currency" else f"{latest_close_value:.4f}"
                    st.metric("Prix de clôture", formatted_close)

                with metrics_col2:
                    formatted_variation = f"{variation_value:.2f}%"
                    formatted_delta = f"{variation_value:.2f}%"
                    st.metric("Variation", formatted_variation, delta=formatted_delta)

                with metrics_col3:
                    vol_str = format_volume(latest_volume_value)
                    st.metric("Volume (dernier jour)", vol_str)

                # Tableau des données
                st.subheader("Données historiques")

                # Calculer la variation quotidienne
                data['Daily_Change'] = data['Close'].pct_change() * 100

                # Créer un DataFrame pour l'affichage avec l'index recréé sans l'heure
                display_data = pd.DataFrame(index=[d.date() for d in data.index])

                # Convertir les valeurs numpy en valeurs Python natives
                open_values = [float(x) for x in data['Open'].to_numpy()]
                high_values = [float(x) for x in data['High'].to_numpy()]
                low_values = [float(x) for x in data['Low'].to_numpy()]
                close_values = [float(x) for x in data['Close'].to_numpy()]

                # Formater les prix
                if tab_key == "currency":
                    # Format spécial pour les devises (4 décimales)
                    display_data['Open'] = [f"{x:.4f}" for x in open_values]
                    display_data['High'] = [f"{x:.4f}" for x in high_values]
                    display_data['Low'] = [f"{x:.4f}" for x in low_values]
                    display_data['Close'] = [f"{x:.4f}" for x in close_values]
                else:
                    # Format standard avec dollar sign
                    display_data['Open'] = [f"${x:.2f}" for x in open_values]
                    display_data['High'] = [f"${x:.2f}" for x in high_values]
                    display_data['Low'] = [f"${x:.2f}" for x in low_values]
                    display_data['Close'] = [f"${x:.2f}" for x in close_values]

                # Formater la variation avec gestion des NaN
                daily_changes = []
                for x in data['Daily_Change'].to_numpy():
                    if pd.isna(x):
                        daily_changes.append("N/A")
                    else:
                        daily_changes.append(f"{float(x):.2f}%")
                display_data['Variation (%)'] = daily_changes

                # Formater le volume
                volumes = []
                for vol in data['Volume'].to_numpy():
                    volumes.append(format_volume(vol))
                display_data['Volume'] = volumes

                # Affichage du tableau avec filtres
                st.dataframe(display_data)

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


def display_stock_data():
    """
    Affiche les données des actions avec filtrage par secteur
    """
    # Option de filtrage par secteur
    all_sectors = list(stock_categories.keys())
    all_sectors.insert(0, "Tous les secteurs")

    selected_sector = st.selectbox(
        "Filtrer par secteur",
        options=all_sectors,
        key="sector_filter"
    )

    # Filtrer les actions en fonction du secteur
    filtered_stocks = {}

    if selected_sector == "Tous les secteurs":
        filtered_stocks = stock_assets
    else:
        # Filtrer les actions du secteur sélectionné
        filtered_stocks = stock_categories[selected_sector]

    # Sélection d'une action
    col1, col2, col3 = st.columns(3)

    with col1:
        selected_asset = st.selectbox("Choisissez une action", list(filtered_stocks.keys()), key="select_stock")

    with col2:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=365)
        start_date_input = st.date_input("Date de début", value=start_date, key="start_stock")

    with col3:
        end_date_input = st.date_input("Date de fin", value=end_date, key="end_stock")

    # Récupération des données
    ticker_symbol = filtered_stocks[selected_asset]
    try:
        # Récupérer les données avec un intervalle quotidien explicite
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

                # Tableau des données
                st.subheader("Données historiques")

                # Calculer la variation quotidienne
                data['Daily_Change'] = data['Close'].pct_change() * 100

                # Créer un DataFrame pour l'affichage avec l'index recréé sans l'heure
                display_data = pd.DataFrame(index=[d.date() for d in data.index])

                # Convertir les valeurs numpy en valeurs Python natives
                open_values = [float(x) for x in data['Open'].to_numpy()]
                high_values = [float(x) for x in data['High'].to_numpy()]
                low_values = [float(x) for x in data['Low'].to_numpy()]
                close_values = [float(x) for x in data['Close'].to_numpy()]

                # Formater les prix
                display_data['Open'] = [f"${x:.2f}" for x in open_values]
                display_data['High'] = [f"${x:.2f}" for x in high_values]
                display_data['Low'] = [f"${x:.2f}" for x in low_values]
                display_data['Close'] = [f"${x:.2f}" for x in close_values]

                # Formater la variation avec gestion des NaN
                daily_changes = []
                for x in data['Daily_Change'].to_numpy():
                    if pd.isna(x):
                        daily_changes.append("N/A")
                    else:
                        daily_changes.append(f"{float(x):.2f}%")
                display_data['Variation (%)'] = daily_changes

                # Formater le volume
                volumes = []
                for vol in data['Volume'].to_numpy():
                    volumes.append(format_volume(vol))
                display_data['Volume'] = volumes

                # Affichage du tableau avec filtres
                st.dataframe(display_data)

                # Créer un excel avec les colonnes inversées et le format pourcentage pour la variation
                excel_data = create_excel(data, clean_text(selected_asset))

                # Nettoyer le nom du fichier
                clean_name = clean_text(selected_asset)
                clean_start = clean_text(start_date_input)
                clean_end = clean_text(end_date_input)

                st.download_button(
                    label="Télécharger les données (XLSX)",
                    data=excel_data,
                    file_name=f"{clean_name}_{clean_start}_{clean_end}.xlsx",
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    key="download_stock"
                )
            else:
                st.error(f"Aucune donnée n'a été récupérée pour {selected_asset}.")

    except Exception as e:
        st.error(f"Une erreur s'est produite lors de la récupération des données : {e}")
        st.error(f"Traceback détaillé: {traceback.format_exc()}")


def display_indices_data():
    """
    Affiche les données des indices avec filtrage par pays
    """
    # Option de filtrage par pays
    all_countries = list(index_categories.keys())
    all_countries.insert(0, "Tous les pays")

    selected_country = st.selectbox(
        "Filtrer par pays",
        options=all_countries,
        key="country_filter"
    )

    # Filtrer les indices en fonction du pays
    filtered_indices = {}

    if selected_country == "Tous les pays":
        filtered_indices = index_assets
    else:
        # Filtrer les indices du pays sélectionné
        filtered_indices = index_categories[selected_country]

    # Sélection d'un indice
    col1, col2, col3 = st.columns(3)

    with col1:
        selected_asset = st.selectbox("Choisissez un indice", list(filtered_indices.keys()), key="select_index")

    with col2:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=365)
        start_date_input = st.date_input("Date de début", value=start_date, key="start_index")

    with col3:
        end_date_input = st.date_input("Date de fin", value=end_date, key="end_index")

    # Récupération des données
    ticker_symbol = filtered_indices[selected_asset]
    try:
        # Récupérer les données avec un intervalle quotidien explicite
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
                    formatted_close = f"{latest_close_value:.2f} pts"
                    st.metric("Clôture", formatted_close)

                with metrics_col2:
                    formatted_variation = f"{variation_value:.2f}%"
                    formatted_delta = f"{variation_value:.2f}%"
                    st.metric("Variation", formatted_variation, delta=formatted_delta)

                with metrics_col3:
                    vol_str = format_volume(latest_volume_value)
                    st.metric("Volume (dernier jour)", vol_str)

                # Tableau des données
                st.subheader("Données historiques")

                # Calculer la variation quotidienne
                data['Daily_Change'] = data['Close'].pct_change() * 100

                # Créer un DataFrame pour l'affichage avec l'index recréé sans l'heure
                display_data = pd.DataFrame(index=[d.date() for d in data.index])

                # Convertir les valeurs numpy en valeurs Python natives
                open_values = [float(x) for x in data['Open'].to_numpy()]
                high_values = [float(x) for x in data['High'].to_numpy()]
                low_values = [float(x) for x in data['Low'].to_numpy()]
                close_values = [float(x) for x in data['Close'].to_numpy()]

                # Formater les prix pour les indices (en points)
                display_data['Open'] = [f"{x:.2f} pts" for x in open_values]
                display_data['High'] = [f"{x:.2f} pts" for x in high_values]
                display_data['Low'] = [f"{x:.2f} pts" for x in low_values]
                display_data['Close'] = [f"{x:.2f} pts" for x in close_values]

                # Formater la variation avec gestion des NaN
                daily_changes = []
                for x in data['Daily_Change'].to_numpy():
                    if pd.isna(x):
                        daily_changes.append("N/A")
                    else:
                        daily_changes.append(f"{float(x):.2f}%")
                display_data['Variation (%)'] = daily_changes

                # Formater le volume
                volumes = []
                for vol in data['Volume'].to_numpy():
                    volumes.append(format_volume(vol))
                display_data['Volume'] = volumes

                # Affichage du tableau avec filtres
                st.dataframe(display_data)

                # Créer un excel avec les colonnes inversées et le format pourcentage pour la variation
                excel_data = create_excel(data, clean_text(selected_asset))

                # Nettoyer le nom du fichier
                clean_name = clean_text(selected_asset)
                clean_start = clean_text(start_date_input)
                clean_end = clean_text(end_date_input)

                st.download_button(
                    label="Télécharger les données (XLSX)",
                    data=excel_data,
                    file_name=f"{clean_name}_{clean_start}_{clean_end}.xlsx",
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    key="download_index"
                )
            else:
                st.error(f"Aucune donnée n'a été récupérée pour {selected_asset}.")

    except Exception as e:
        st.error(f"Une erreur s'est produite lors de la récupération des données : {e}")
        st.error(f"Traceback détaillé: {traceback.format_exc()}")


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
