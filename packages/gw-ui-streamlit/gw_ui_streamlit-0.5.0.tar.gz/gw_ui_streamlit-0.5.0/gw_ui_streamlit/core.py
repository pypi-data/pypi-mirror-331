from typing import Any
import json

import streamlit as st
from pathlib import Path

import gw_ui_streamlit._create_ui as gwu
import gw_ui_streamlit.database as gwd
from gw_ui_streamlit._utils import build_default_rows
from gw_ui_streamlit.cache import GWSCache
from gw_ui_streamlit.create_ui import build_columns
from gw_ui_streamlit.dialog_ui import (
    table_row_add_dialog,
    table_row_edit_dialog,
    search_dialog,
)
from gw_ui_streamlit.models import UserInterface, InputFields
from gw_ui_streamlit.process_templates import _process_template_by_name
from gw_ui_streamlit.utils import (
    find_yaml_ui,
    find_yaml_other,
    build_model,
    _fetch_key,
    _fetch_configs,
    _completed_required_fields,
    _create_saved_state,
    _save_config,
    _load_config,
    _write_string,
    _fetch_tab,
    _create_storage_key,
    _show_info,
    _show_warning,
    _show_error,
    codeify_string,
)


class GWStreamlit:

    def create_ui(self):
        """Builds the UI for the application"""
        if self.built_ui:
            return
        gwu.create_ui_title()
        gwu.create_ui_buttons()
        if not self.model.Title:
            gwu.create_ui_tabs()
        gwu.create_tab_buttons()
        gwu.create_ui_inputs()
        self.built_ui = True

    def find_model_part(self, identifier: str) -> None | InputFields:
        """Finds a model part by the identifier provided. The identifier can be the code or the
        label of the item. If the item is not found None is returned.
        Parameters
        ----------
        identifier: str
            Identifier of the item to find"""
        items = [item for item in self.model.Inputs 
            if codeify_string(item.Code) == codeify_string(identifier)
        ]
        if len(items) == 0:
            items = [item for item in self.model.Inputs if item.Label == identifier]
        if len(items) == 0:
            return None
        return items[0]

    def __init__(
        self,
        application: str = None,
        yaml_file: dict = None,
        *,
        single_application: bool = False,
    ):
        self.application = application
        self.yaml_file = yaml_file
        self.model = build_model(self.yaml_file)
        self.keys = []
        self.input_values = {}
        self.button_values = {}
        self.built_ui = False
        self.tab_dict = {}
        self.default_rows = build_default_rows(self)
        self.child = None
        self.saved_state: dict
        self.modal = False
        self.cache = GWSCache()
        self.single_application = single_application

    def populate(
        self,
        application: str = None,
        yaml_file: dict = None,
        *,
        single_application: bool = False,
    ):
        """Populates the GWStreamlit object with the application and yaml file

        Parameters
        ----------
        application : str, optional
            Application Code to use, by default None
        yaml_file : dict, optional
            yaml file code or the path to a yaml file, by default None
        single_application : bool, optional
            Indicates that this constitues a single application of one or more pages
            If True, the application will not be reset when the user navigates to another page*
        """
        self.application = application
        self.yaml_file = yaml_file
        self.model = build_model(self.yaml_file)
        self.default_rows = build_default_rows(self)
        self.built_ui = False
        gwu.discover_functions()


def initialize(application: str, yaml_file_name: str, *, single_application: bool = False):
    """Initializes the application
    Parameters
    ----------
    application : str
        Name of the application
    yaml_file_name : str
        Name of the yaml file, if file is not in the default location then this needs to be the full path
    """
    if Path(yaml_file_name).name == yaml_file_name:
        yaml_file = find_yaml_ui(yaml_file_name)
    else:
        yaml_file = find_yaml_other(yaml_file_name)
    st.session_state["GWStreamlit"].populate(
        application, yaml_file, single_application=single_application
    )
    st.session_state["GWStreamlit"].create_ui()


def cache() -> GWSCache:
    gws = st.session_state["GWStreamlit"]
    return gws.cache


def required_fields() -> bool:
    """Checks if all required fields have been completed"""
    return _completed_required_fields()


def fetch_key(ui_item: Any) -> str:
    """Fetches the key for the item provided"""
    return _fetch_key(ui_item)


def fetch_configs(application_name: str = None) -> list:
    """Extract the configurations for the application"""
    if application_name is None:
        application_name = st.session_state["GWStreamlit"].application
    return _fetch_configs(application_name)


def create_saved_state(*, short_key: bool = False, fields=False):
    """Creates a saved state for the application"
    Parameters
    ----------
    short_key : bool, optional
        If True, creates a short key for the saved state"""
    return _create_saved_state(short_key=short_key, fields=fields)


def save_config(file_name, config_data: None):
    """Save the configuration information"""
    if config_data is None:
        config_data = create_saved_state()
    application_name = st.session_state["GWStreamlit"].application
    _save_config(application_name, file_name, config_data)


def load_config(file_name):
    """Loads a configuration file"""
    _load_config(file_name)


def process_template_by_name(template_name, input_dict: dict, location="resources/templates"):
    """Processes a template by name"""
    return _process_template_by_name(template_name, input_dict, location)


def write_string(location, file_name, content, **kwargs):
    """Writes a string to a file"""
    _write_string(location, file_name, content, **kwargs)


def write_json(location, file_name, content, **kwargs):
    """Writes json to a file"""
    string_content = json.dumps(content)
    _write_string(location, file_name, string_content, **kwargs)


def fetch_tab(item: Any):
    """Fetches a tab by the item provided"""
    return _fetch_tab(item)


def create_storage_key(key_value: str) -> str:
    """Creates a storage key for the value provided"""
    return _create_storage_key(key_value)


def generate_image(item):
    gws = st.session_state["GWStreamlit"]
    gwu.generate_image(gws, item)


def find_model_part(identifier: str):
    gws = st.session_state["GWStreamlit"]
    return gws.find_model_part(identifier)


def show_info(message, tab="Output"):
    """Displays an information message on the UI, optionaly a tab can be define,
    by default it will display on the Output Tab

    Parameters
    ----------
    message
        Text to display
    tab (optional)
        tab to where the message will be displayed
    """
    _show_info(message, tab)


def show_warning(message, tab="Output"):
    _show_warning(message, tab)


def show_error(message, tab="Output"):
    _show_error(message, tab)


def model() -> UserInterface:
    gws = st.session_state["GWStreamlit"]
    return gws.model


def model_inputs() -> list[InputFields]:
    gws = st.session_state["GWStreamlit"]
    return gws.model.Inputs


def value(identifier: str):
    item = find_model_part(identifier)
    if item is None:
        key = create_storage_key(identifier)
        return st.session_state.get(key)
    else:
        return st.session_state.get(item.Key)


def save_storage(key, storage_value: Any):
    key = create_storage_key(key)
    st.session_state[key] = storage_value


def fetch_value(*, key: str = None, name: str = None):
    """Extract the value from the session state, if there is no key that corresponds to the name
    supplied the cache is interrogated for the key and value"""
    if key is None:
        key = fetch_key(name)
    item_value = st.session_state.get(key)
    if item_value is None:
        gws = st.session_state["GWStreamlit"]
        if gws.cache.has_key(key):
            item_value = gws.cache.get(name)
    return item_value


def fetch_value_reset(*, key: str = None, name: str = None):
    return_value = fetch_value(key=key, name=name)
    if key is not None:
        st.session_state[key] = None
    return return_value


def set_value(name: str, input_value):
    """Sets the value in either the session state or in the cache, if the name provided matched a key in
    the session state it is updated with the value, otherwise the cache is updated"""
    if name in st.session_state:
        st.session_state[name] = input_value
    else:
        gws = st.session_state["GWStreamlit"]
        gws.cache.set(name, input_value)


def get_model() -> UserInterface:
    """Returns the model for the application"""
    return st.session_state["GWStreamlit"].model






def reset_inputs(*, alternate_model=None, table_only=False):
    """Resets the inputs on the UI, most inputs will be reset to None. Tables will have the contents
    of the dataframe erased and recreated with the default values if they exist
    """
    gws = st.session_state["GWStreamlit"]
    process_model = get_model()
    if alternate_model is not None:
        process_model = alternate_model
    for model_input in process_model.Inputs:
        if model_input.Type != "table":
            if table_only == False:
                st.session_state[model_input.Key] = None
        else:
            if model_input.DefaultFunction:
                defined_function = model_input.DefaultFunctionBuilt
                default_rows = defined_function()
            else:
                default_rows = gws.default_rows.get(model_input.Label, dict())
            columns = build_columns(model_input)
            if model_input.Key in st.session_state:
                st.session_state[model_input.Key]["deleted_rows"] = []
                st.session_state[model_input.Key]["added_rows"] = []
                st.session_state[model_input.Key]["edited_rows"] = []

            df = st.session_state[f"{model_input.Key}_df"]
            df.drop(list(df.index.values), inplace=True)

            for default in default_rows:
                df.loc[len(df)] = default
            df.reset_index(drop=True, inplace=True)


def get_search_model():
    if "search_model" not in st.session_state:
        return None
    return st.session_state["search_model"]


def get_streamlit():
    return st


def get_primary_code(model: UserInterface):
    """Extract the code corrisponding to the value marked as Primary, this is the key to the row in the database
    The promary could be a standard input or in the case of serach a column in a table, for tables the label is
    extracted as this is what is used to form the column in the dataframe.
    Parameters
    ----------
    model : UserInterface
        The model to extract the code from"""
    for input_item in model.Inputs:
        if input_item.Primary == True:
            return input_item.Code
        if input_item.Type == "table":
            for input_column in input_item.Columns:
                if input_column.Primary == True:
                    return input_column.Label
    return None


def update_couchdb_record():
    gwd.update_couchdb_record()

