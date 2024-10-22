from shiny import ui, render

from dp_creator_ii.utils.template import make_notebook_py, make_script_py
from dp_creator_ii.utils.converters import convert_py_to_nb


def results_ui():
    return ui.nav_panel(
        "Download results",
        ui.markdown(
            "You can now make a differentially private release of your data. "
            "This will lock the configuration you’ve provided on the previous pages."
        ),
        ui.markdown("TODO: Button: “Download Report (.txt)” (implemented as yaml?)"),
        ui.markdown("TODO: Button: “Download Report (.csv)"),
        ui.markdown(
            "You can also download code that can be executed to produce a DP release. "
            "Downloaded code does not lock the configuration."
        ),
        ui.download_button(
            "download_script",
            "Download Script (.py)",
        ),
        ui.download_button(
            "download_notebook_unexecuted",
            "Download Notebook (.ipynb)",
        ),
        value="results_panel",
    )


def results_server(input, output, session):
    @render.download(
        filename="dp-creator-script.py",
        media_type="text/x-python",
    )
    async def download_script():
        contributions = input.contributions()
        script_py = make_script_py(
            contributions=contributions,
            loss=1,
            weights=[1],
        )
        yield script_py

    @render.download(
        filename="dp-creator-notebook.ipynb",
        media_type="application/x-ipynb+json",
    )
    async def download_notebook_unexecuted():
        contributions = input.contributions()
        notebook_py = make_notebook_py(
            csv_path="todo.csv",
            contributions=contributions,
            loss=1,
            weights=[1],
        )
        notebook_nb = convert_py_to_nb(notebook_py)
        yield notebook_nb

    @render.download(
        filename="dp-creator-notebook-executed.ipynb",
        media_type="application/x-ipynb+json",
    )
    async def download_notebook_executed():
        contributions = input.contributions()
        notebook_py = make_notebook_py(
            csv_path="todo.csv",
            contributions=contributions,
            loss=1,
            weights=[1],
        )
        notebook_nb = convert_py_to_nb(notebook_py, execute=True)
        yield notebook_nb
