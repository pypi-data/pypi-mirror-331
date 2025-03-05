import streamlit as st
import json
import sys
from grapher import Grapher as grr


def display_results(fp, tp):
    st.title("Payload Visualizer")
    try:
        json_obj_1 = fp
        json_obj_2 = tp
    except json.JSONDecodeError:
        st.error("Invalid JSON format. Please check your input.")

    with st.sidebar:
        fp_graph = st.button("First Party Graph", use_container_width=True)
        fp_raw = st.button("First Party Raw Payload", use_container_width=True)
        tp_graph = st.button("Third Party Graph", use_container_width=True)
        tp_raw = st.button("Third Party Raw Payload", use_container_width=True)

    if fp_graph:
        for element in json_obj_1:
            if isinstance(element, dict) and 'wss' not in element:
                with st.container():
                    grr.generate(element)
    elif fp_raw:
        st.write(json_obj_1)
    elif tp_graph:
        for element in json_obj_2:
            if isinstance(element, dict) and 'wss' not in element:
                grr.generate(element)
    elif tp_raw:
        st.write(json_obj_2)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        json_data = json.loads(sys.argv[1])  # Decode JSON from argument
        fp, tp = json_data.get("fp", {}), json_data.get("tp", {})
    else:
        fp, tp = {}, {}
    display_results(fp, tp)
