import streamlit as st
import pandas as pd
import altair as alt

st.title("Analyse de pourcentages croisés")

path_file = "./Questionnaire atelier recherche.csv"

try:
    df = pd.read_csv(path_file, encoding="ISO-8859-1", sep=";")
    st.write("## Aperçu des données")
    st.dataframe(df)

    categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()

    if categorical_cols:
        group_col = st.selectbox("Variable de regroupement (ex : âge)", categorical_cols)
        target_col = st.selectbox("Variable analysée (ex : télévision)", categorical_cols)

        if st.button("Calculer les pourcentages"):
            st.write(f"## Résultats : {group_col} → {target_col}")

            valid_df = df[[group_col, target_col]].dropna()
            total_global = len(df)
            total_valid = len(valid_df)

            st.write(f"**Nombre total de répondants (toutes données)** : {total_global}")
            st.write(f"**Nombre de réponses utilisées pour ce croisement** : {total_valid}")

            global_distribution = valid_df[target_col].value_counts()
            global_pct = round((global_distribution / total_valid) * 100, 2)

            total_group = valid_df[group_col].value_counts().rename("Total")
            cross = pd.crosstab(valid_df[group_col], valid_df[target_col])
            percentage = round((cross.T / total_group).T * 100, 2)

            cross_with_global = cross.copy()
            for col in cross.columns:
                cross_with_global[col + " (global %)"] = global_pct[col] if col in global_pct else 0

            st.write("### Tableau récapitulatif complet (avec % globaux sur les données croisées)")
            st.dataframe(cross_with_global)

            st.write("### Résumé automatique regroupé (avec % globaux)")

            for group in cross.index:
                total = total_group[group]
                st.write(f"## 📌 {group} ({total} personnes exploitées) ")

                for val in global_pct.index:
                    count = cross.loc[group, val] if val in cross.columns else 0
                    pct = percentage.loc[group, val] if val in percentage.columns else 0
                    global_value = global_pct[val]

                    st.write(f"• **{val}** : {count} ({pct}%) — global (sur croisement) : {global_value}%")

            st.write("### Répartition générale (camembert) sur les données croisées")

            st.write(f"#### Pourcentages globaux par catégorie (sur {total_valid} réponses croisées) :")
            for val in global_distribution.index:
                st.write(f"• **{val}** : {global_distribution[val]} personnes ({global_pct[val]}%)")

            pie_data = global_distribution.reset_index()
            pie_data.columns = [target_col, 'count']

            pie_chart = alt.Chart(pie_data).mark_arc().encode(
                theta='count',
                color=target_col,
                tooltip=[target_col, 'count']
            )

            st.altair_chart(pie_chart, use_container_width=True)

            st.write("## Analyse inversée : par appareil (avec % globaux)")

            expanded = df[target_col].str.split(";", expand=True)
            unique_devices = pd.unique(expanded.values.ravel())
            unique_devices = [d for d in unique_devices if pd.notna(d)]

            age_global = df[group_col].dropna().value_counts()
            age_global_pct = round((age_global / age_global.sum()) * 100, 2)

            for device in unique_devices:
                subset = df[df[target_col].str.contains(device, na=False)][[group_col, target_col]].dropna()
                count_total = len(subset)

                st.write(f"### 📌 {device} ({count_total} personnes exploitées)")

                if count_total == 0:
                    st.write("Aucun utilisateur exploitable pour ce croisement.")
                    continue

                age_counts = subset[group_col].value_counts()
                age_pct = round((age_counts / count_total) * 100, 2)

                for age in age_global.index:
                    c = age_counts[age] if age in age_counts else 0
                    p = age_pct[age] if age in age_pct else 0
                    global_age = age_global_pct[age] if age in age_global_pct else 0

                    st.write(f"• **{age}** : {c} ({p}%) — global (tous répondants) : {global_age}%")

                st.write("---")

            st.success("Analyse réalisée avec succès !")

    else:
        st.warning("Aucune colonne texte trouvée dans le CSV.")

except Exception as e:
    st.error(f"Erreur : {e}")
