import json
import math
import requests

import gw_ui_streamlit.core as gws
import gw_ui_streamlit._create_ui as create_ui
from gw_ui_streamlit.constants import DIALOG_TYPE
from gw_ui_streamlit.utils import construct_function, find_yaml_ui, build_model, update_session
from gw_settings_management.setting_management import get_endpoint


@gws.st.dialog(title="Add Row", width="large")
def table_row_add_dialog(table_input, dialog_values={}):
    if "dialog_inputs" not in gws.st.session_state:
        dialog_inputs = []
    else:
        dialog_inputs = gws.st.session_state["dialog_inputs"]
    if dialog_values is None:
        return
    #
    # Set the Dialog Anchor to the first column if it is not set
    #
    if table_input.DialogAnchor is not None:
        column = next(
            itemm for itemm in table_input.Columns if itemm.Code == table_input.DialogAnchor
        )
        create_ui.build_input(column, dialog_values, dialog=DIALOG_TYPE["add"])
        process_dialog_inputs(table_input)
    #
    # Construct the placeholders for the rest of the inputs
    #
    placeholder = gws.st.empty()
    container = placeholder.container(border=True)
    #
    # Generate the rest of the inputs in the container
    #
    for column in table_input.Columns:
        if table_input.DialogInputs is not None:
            if dialog_inputs == "all" or column.Code in dialog_inputs:
                if column.Code != table_input.DialogAnchor:
                    create_ui.build_input(
                        column, dialog_values, dialog=DIALOG_TYPE["add"], location=container
                    )
        else:
            if column.Code != table_input.DialogAnchor:
                create_ui.build_input(
                    column, dialog_values, dialog=DIALOG_TYPE["add"], location=container
                )
    #
    # Add the submit button to the bottom of the dialog
    #
    if gws.st.button("Submit"):
        update_df(table_input, dialog_values)
        gws.st.rerun()


@gws.st.dialog(title="Edit Row", width="large")
def table_row_edit_dialog(table_input, row, selected_index, dialog_values):
    if dialog_values is None:
        gws.st.rerun()
    for column in table_input.Columns:
        if column.Key not in dialog_values:
            value = row.get(column.Label)
            value = convert_value(column, value)
            dialog_values[column.Key] = value
        create_ui.build_input(column, dialog_values, dialog=DIALOG_TYPE["edit"])

    if gws.st.button("Submit"):
        update_df(table_input, dialog_values, selected_index)
        gws.st.rerun()

    process_dialog_inputs(table_input)


@gws.st.dialog(title="Search", width="large")
def search_dialog(yaml_file_code: str, dialog_values={}):
    yaml_object = find_yaml_ui(yaml_file_code)
    model = build_model(yaml_object)
    create_ui.discover_functions(alternative_model = model)
    gws.get_streamlit().session_state["search_model"] = model
    create_ui.create_ui_buttons(alternate_buttons=model.Buttons)
    for item_input in model.Inputs:
        create_ui.build_input(item_input, dialog_values, dialog=DIALOG_TYPE["search"])

    model = gws.get_streamlit().session_state["search_model"]
    model_input = next(item for item in model.Inputs if item.Type == "table")
    key = model_input.Key
    selected = gws.get_streamlit().session_state[key].selection
    if len(selected["rows"]) > 0:
        type = "primary"
    else:
        type = "secondary"
    if gws.st.button("Pick", type=type):
        fetch_selected_row(f"/{gws.model().Rest}/")
        gws.st.rerun()


def dialog_search(yaml_code: str):
    if "search_model" in gws.st.session_state:
        model = gws.get_streamlit().session_state["search_model"]
        gws.reset_inputs(alternate_model=model)
    dialog_values = {}
    search_dialog(yaml_code, dialog_values)



def convert_value(column, value):
    """Some values seem to the converted incorrectly this function fixes that
    Parameters
    ----------
    column
        model input for the column
    value
        Value to be tested and converted if needed
    Returns
    -------
    value
        Converted value"""
    if type(value) is float and math.isnan(value):
        value = None
        gws.st.session_state[column.Key] = value
    if column.Type == "integer_input" and value is not None:
        value = int(value)
        gws.st.session_state[column.Key] = value
        return value

    if column.Type == "checkbox" and value is not None:
        if type(value) is bool:
            ...
        elif value.lower() == "false" or value.lower() == "no" or value == "0":
            value = False
        elif value.lower() == "true" or value.lower() == "yes" or value == "1":
            value = True
        gws.st.session_state[column.Key] = value
        return value

    return value


def update_df(process_input, dialog_values, index=-1,* , use_fields=False):
    """Convert they keys in the dialog from Key to code, update the dataframe"""
    key_mapping = {}
    for column in process_input.Columns:
        key_mapping[column.Key] = column.Label
    updated_data = {
        key_mapping.get(key, key): value for key, value in dialog_values.items()
    }
    df = gws.st.session_state[f"{process_input.Key}_df"]
    if index == -1:
        df.loc[len(df)] = updated_data
    else:
        df.loc[index] = updated_data


def process_dialog_inputs(table_input):
    if table_input.DialogInputs is not None:
        if "dialog_input_function" not in gws.st.session_state:
            function = construct_function(table_input.DialogInputs)
            gws.st.session_state["dialog_input_function"] = function
        else:
            function = gws.st.session_state["dialog_input_function"]
        if function is not None:
            function()
    else:
        gws.st.session_state["dialog_inputs"] = "all"


def build_query():
    model = gws.get_streamlit().session_state["search_model"]
    selector = {}
    fields = []
    for model_input in [item for item in model.Inputs if item.Type != "table"]:
        value = gws.get_streamlit().session_state.get(model_input.Key)
        field = model_input.DBField
        if field is None:
            field = model_input.Code
        if value is not None:
            selector[field] = value

    for model_input in [item for item in model.Inputs if item.Type == "table"]:
        for column in model_input.Columns:
            if column.DBField is not None:
                fields.append(column.DBField)
            else:
                fields.append(column.Code)

    selector_dict = {}
    if fields:
        selector_dict["fields"] = fields
    if selector:
        selector_dict["selector"] = selector

    selector_json = json.dumps(selector_dict)
    return selector_json

def dialog_perform_search():
    """Performs the serach but creating the query and calling the endpoint, the results are populated into
    the serach results table."""
    selector_json = build_query()
    model = gws.get_streamlit().session_state["search_model"]
    model_input = next(item for item in model.Inputs if item.Type == "table")
    rest_endpoint = gws.model().Rest
    df = gws.get_streamlit().session_state[f"{model_input.Key}_df"]
    df.drop(list(df.index.values), inplace=True)
    endpoint_rest = get_endpoint(f"{rest_endpoint}/search/{selector_json}")
    results = requests.get(endpoint_rest)
    results_list = json.loads(results.text)
    for process_item in results_list:
        if "_id" in process_item:
            process_item["id"] = process_item["_id"]
        if "_rev" in process_item:
            process_item["rev"] = process_item["_rev"]
    process_input = next((item for item in model.Inputs if item.Type == "table"), None)
    for result_item in results_list:
        update_df(process_input, result_item)



def fetch_selected_row(endpoint: str):
    """Retrieves the row from the selection results table and updates the session state
    Parameters
    ----------
    endpoint : str
        The endpoint to be queried"""
    model = gws.get_streamlit().session_state["search_model"]
    model_input = next(item for item in model.Inputs if item.Type == "table")
    key = model_input.Key
    selected = gws.get_streamlit().session_state[key].selection
    if selected is None or len(selected["rows"]) == 0:
        return
    selected_index = selected["rows"][0]
    df = gws.get_streamlit().session_state[f"{key}_df"]
    row = df.iloc[selected_index].to_dict()
    primary_code = gws.get_primary_code(model)
    if endpoint.endswith("/"):
        endpoint_rest =get_endpoint(f"{endpoint}{row.get(primary_code)}")
    else:
        endpoint_rest = get_endpoint(f"{endpoint}/{row.get(primary_code)}")
    document = requests.get(endpoint_rest)
    document_dict = json.loads(document.text)
    update_session(document_dict, using_code=True)


def add_table_row_dialog(table_code: str):
    """Process the dialog for adding a row to a table
    Parameters
    ----------
    table_code : str
        The code representing the table to add the row to"""
    dialog_values = {}
    process_input = next(
        (item for item in gws.get_model().Inputs if item.Code == table_code and item.Type == "table"),
        None,
    )
    if process_input is not None:
        for column in process_input.Columns:
            gws.st.session_state[column.Key] = None
    table_row_add_dialog(process_input, dialog_values)


def edit_table_row_dialog(table_code: str):
    dialog_values = {}
    key = gws.fetch_key(table_code)
    selected = gws.st.session_state[key].selection
    if selected is None or len(selected["rows"]) == 0:
        return
    selected_index = selected["rows"][0]
    df = gws.st.session_state[f"{key}_df"]
    row = df.iloc[selected_index].to_dict()
    model = gws.get_model()
    process_input = None
    for model_input in model.Inputs:
        if model_input.Type == "table" and model_input.Code == table_code:
            process_input = model_input
    for column in process_input.Columns:
        gws.st.session_state[column.Key] = row.get(column.Label)
    table_row_edit_dialog(process_input, row, selected_index, dialog_values)


