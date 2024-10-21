from math import pow

from shiny import ui, reactive, render

from dp_creator_ii.mock_data import mock_data, ColumnDef
from dp_creator_ii.app.plots import plot_error_bars_with_cutoff
from dp_creator_ii.app.components.log_slider import log_slider
from dp_creator_ii.csv_helper import read_field_names
from dp_creator_ii.argparse_helpers import get_csv_contrib


def analysis_ui():
    return ui.nav_panel(
        "Define Analysis",
        ui.markdown(
            "Select numeric columns of interest, "
            "and for each numeric column indicate the expected range, "
            "the number of bins for the histogram, "
            "and its relative share of the privacy budget."
        ),
        ui.markdown(
            "[TODO: Column selection]"
            "(https://github.com/opendp/dp-creator-ii/issues/33)"
        ),
        ui.output_text("csv_fields"),
        ui.markdown(
            "What is your privacy budget for this release? "
            "Values above 1 will add less noise to the data, "
            "but have greater risk of revealing individual data."
        ),
        log_slider("log_epsilon_slider", 0.1, 10.0),
        ui.output_text("epsilon"),
        ui.markdown(
            "## Preview\n"
            "These plots assume a normal distribution for the columns you've selected, "
            "and demonstrate the effect of different parameter choices."
        ),
        ui.output_plot("plot_preview"),
        "(This plot is only to demonstrate that plotting works.)",
        ui.input_action_button("go_to_results", "Download results"),
        value="analysis_panel",
    )


def analysis_server(input, output, session):
    (csv_path, _contributions) = get_csv_contrib()

    csv_path_from_cli_value = reactive.value(csv_path)

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

    def epsilon_calc():
        return pow(10, input.log_epsilon_slider())

    @render.text
    def epsilon():
        return f"Epsilon: {epsilon_calc():0.3}"

    @render.plot()
    def plot_preview():
        min_x = 0
        max_x = 100
        df = mock_data({"col_0_100": ColumnDef(min_x, max_x)}, row_count=20)
        return plot_error_bars_with_cutoff(
            df["col_0_100"].to_list(),
            x_min_label=min_x,
            x_max_label=max_x,
            y_cutoff=30,
            y_error=5,
        )

    @reactive.effect
    @reactive.event(input.go_to_results)
    def go_to_results():
        ui.update_navs("top_level_nav", selected="results_panel")
