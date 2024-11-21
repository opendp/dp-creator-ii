from shiny import ui, render, reactive

from dp_wizard.utils.code_generators import (
    NotebookGenerator,
    ScriptGenerator,
    AnalysisPlan,
    AnalysisPlanColumn,
)
from dp_wizard.utils.converters import convert_py_to_nb
from dp_wizard.app.components.outputs import info_box

results_panel_id = "3_results_panel"


def results_ui():
    return ui.nav_panel(
        "Download results",
        ui.output_ui("results_panel_warning"),
        ui.markdown("You can now make a differentially private release of your data."),
        ui.download_button(
            "download_script",
            "Download Script (.py)",
        ),
        ui.download_button(
            "download_notebook",
            "Download Notebook (.ipynb)",
        ),
        value=results_panel_id,
    )


def results_server(
    input,
    output,
    session,
    csv_path,
    contributions,
    lower_bounds,
    upper_bounds,
    bin_counts,
    weights,
    epsilon,
    current_panel,
):  # pragma: no cover
    @render.text
    def results_panel_warning():
        if current_panel() < results_panel_id:
            return info_box(
                """
                This tab is locked until you've confirmed your
                analysis details.
                """
            )
        return ""

    @reactive.calc
    def analysis_plan() -> AnalysisPlan:
        # weights().keys() will reflect the desired columns:
        # The others retain inactive columns, so user
        # inputs aren't lost when toggling checkboxes.
        columns = {
            col: AnalysisPlanColumn(
                lower_bound=lower_bounds()[col],
                upper_bound=upper_bounds()[col],
                bin_count=int(bin_counts()[col]),
                weight=int(weights()[col]),
            )
            for col in weights().keys()
        }
        return AnalysisPlan(
            csv_path=csv_path(),
            contributions=contributions(),
            epsilon=epsilon(),
            columns=columns,
        )

    @render.download(
        filename="dp-wizard-script.py",
        media_type="text/x-python",
    )
    async def download_script():
        script_py = ScriptGenerator(analysis_plan()).make_py()
        yield script_py

    @render.download(
        filename="dp-wizard-notebook.ipynb",
        media_type="application/x-ipynb+json",
    )
    async def download_notebook():
        notebook_py = NotebookGenerator(analysis_plan()).make_py()
        notebook_nb = convert_py_to_nb(notebook_py, execute=True)
        yield notebook_nb
