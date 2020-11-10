import os
import json
import logging

import streamlit as st

from ipapi.base.pipeline_launcher import launch


def _max_width_():
    max_width_str = f"max-width: 2000px;"
    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
    }}
    </style>    
    """,
        unsafe_allow_html=True,
    )


_max_width_()


st.title("IPSO runner - streamlit version")

STORED_STATES_PATH = os.path.join(
    "C:/", "Users", "fmavianemac", "Documents", "ipso_phen", "pipeline_state", ""
)


@st.cache
def get_stored_states():
    return ["Pick One"] + [
        name
        for name in os.listdir(STORED_STATES_PATH)
        if os.path.isfile(os.path.join(STORED_STATES_PATH, name))
    ]


progress_bar = None


def progress_callback(step, total):
    progress_bar.progress(step / total)


def error_callback(error_level, error_message):
    if error_level <= logging.WARNING:
        st.warning(error_message)
    else:
        st.error(error_message)


def main():
    stored_state = st.selectbox(
        label="Select stored state",
        options=get_stored_states(),
        index=0,
    )

    params = {}

    if stored_state == "Pick One":
        return
    else:
        params["stored_state"] = os.path.join(STORED_STATES_PATH, stored_state)
        if os.path.isfile(params["stored_state"]):
            with open(params["stored_state"], "r") as f:
                stored_state = json.load(f)

        params["thread_count"] = st.number_input(
            label="Thread count:",
            min_value=1,
            max_value=8,
            value=stored_state.get("thread_count", 1),
        )
        params["output_folder"] = st.text_input(
            label="Output folder:", value=stored_state.get("output_folder", "")
        )
        params["csv_file_name"] = st.text_input(
            label="CSV file name:", value=stored_state.get("csv_file_name", "")
        )
        params["overwrite"] = st.checkbox(
            label="Overwrite existing data",
            value=stored_state.get("overwrite", False),
        )
        params["build_annotation_csv"] = st.checkbox(
            label="Build annotation CSV",
            value=stored_state.get("build_annotation_csv", False),
        )
        params["generate_series_id"] = st.checkbox(
            label="Generate series IDs",
            value=stored_state.get("generate_series_id", False),
        )
        if params["generate_series_id"] is True:
            params["series_id_time_delta"] = st.number_input(
                label="Series ID time delta:",
                min_value=1,
                max_value=240,
                value=stored_state.get("series_id_time_delta", 20),
            )

        if st.button(label="Start", key="launch_mass_processing"):
            global progress_bar
            progress_bar = st.progress(0)
            params["progress_callback"] = progress_callback
            params["error_callback"] = error_callback
            launch(**params)


main()
