from math import pow

from shiny import ui, reactive, render

from dp_creator_ii.app.components.inputs import log_slider
from dp_creator_ii.app.components.column_module import column_ui, column_server
from dp_creator_ii.utils.csv_helper import read_field_names
from dp_creator_ii.utils.argparse_helpers import get_csv_contrib
from dp_creator_ii.app.components.outputs import output_code_sample
from dp_creator_ii.utils.templates import make_privacy_loss_block


def analysis_ui():
    return ui.nav_panel(
        "Define Analysis",
        ui.markdown(
            "Select numeric columns of interest, "
            "and for each numeric column indicate the expected range, "
            "the number of bins for the histogram, "
            "and its relative share of the privacy budget."
        ),
        ui.input_checkbox_group("columns_checkbox_group", None, []),
        ui.output_ui("columns_ui"),
        ui.markdown(
            "What is your privacy budget for this release? "
            "Values above 1 will add less noise to the data, "
            "but have a greater risk of revealing individual data."
        ),
        log_slider("log_epsilon_slider", 0.1, 10.0),
        ui.output_text("epsilon"),
        output_code_sample("Privacy Loss", "privacy_loss_python"),
        ui.input_action_button("go_to_results", "Download results"),
        value="analysis_panel",
    )


def analysis_server(input, output, session):  # pragma: no cover
    (csv_path, contributions) = get_csv_contrib()

    csv_path_from_cli_value = reactive.value(csv_path)
    weights = reactive.value({})

    def set_column_weight(column_id, weight):
        weights.set({**weights(), column_id: weight})

    def get_weights_sum():
        return sum(weights().values())

    @reactive.effect
    def _():
        ui.update_checkbox_group(
            "columns_checkbox_group",
            label=None,
            choices=csv_fields_calc(),
        )

    @render.ui
    def columns_ui():
        column_ids = input.columns_checkbox_group()
        for column_id in column_ids:
            column_server(
                column_id,
                name=column_id,
                contributions=contributions,
                epsilon=epsilon_calc(),
                set_column_weight=set_column_weight,
                get_weights_sum=get_weights_sum,
            )
        return [
            [
                ui.h3(column_id),
                column_ui(column_id),
            ]
            for column_id in column_ids
        ]

    @reactive.calc
    def csv_path_calc():
        csv_path_from_ui = input.csv_path_from_ui()
        if csv_path_from_ui is not None:
            return csv_path_from_ui[0]["datapath"]
        return csv_path_from_cli_value.get()

    @render.text
    def csv_path():
        return csv_path_calc()

    @reactive.calc
    def csv_fields_calc():
        path = csv_path_calc()
        if path is None:
            return None
        return read_field_names(path)

    @render.text
    def csv_fields():
        return csv_fields_calc()

    @reactive.calc
    def epsilon_calc():
        return pow(10, input.log_epsilon_slider())

    @render.text
    def epsilon():
        return f"Epsilon: {epsilon_calc():0.3}"

    @render.code
    def privacy_loss_python():
        return make_privacy_loss_block(epsilon_calc())

    @reactive.effect
    @reactive.event(input.go_to_results)
    def go_to_results():
        ui.update_navs("top_level_nav", selected="results_panel")
