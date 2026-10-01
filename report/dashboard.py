from fasthtml.common import *
import matplotlib.pyplot as plt
from pandas import options
from pathlib import Path
from fasthtml.common import RedirectResponse

from employee_events import QueryBase, Employee, Team
from utils import load_model

from base_components import (
    Dropdown,
    BaseComponent,
    Radio,
    MatplotlibViz,
    DataTable
    )

from combined_components import FormGroup, CombinedComponent


class ReportDropdown(Dropdown):

    # The label follows whichever entity type is being viewed
    def build_component(self, entity_id, model):
        self.label = model.name.title()
        return super().build_component(entity_id, model)

    def component_data(self, entity_id, model):
        return model.names()


class Header(BaseComponent):

    def build_component(self, entity_id, model):

        return H1(f"{model.name.title()} Performance")


# Cumulative positive/negative event counts over time
class LineChart(MatplotlibViz):

    def visualization(self, entity_id, model):

        data = model.event_counts(entity_id)
        data = data.fillna(0)
        data = data.set_index('event_date')
        data = data.sort_index()

        cumulative = data.cumsum()
        cumulative.columns = ['Positive', 'Negative']

        fig, ax = plt.subplots()
        cumulative.plot(ax=ax)

        self.set_axis_styling(ax, bordercolor='black', fontcolor='black')

        ax.set_title(f"{model.name.title()} Event Counts")
        ax.set_xlabel("Date")
        ax.set_ylabel("Cumulative Events")


# Predicted probability of being recruited
class BarChart(MatplotlibViz):

    predictor = load_model()

    def visualization(self, entity_id, model):

        data = model.model_data(entity_id)
        probability_of_recruitment = self.predictor.predict_proba(data)[:, 1]

        # A team's model_data returns one row per member, so a team is
        # summarized by its mean; an employee has a single row
        if model.name == 'team':
            pred = probability_of_recruitment.mean()
        else:
            pred = probability_of_recruitment[0]

        fig, ax = plt.subplots()

        # Continuous color scale across the observed prediction range:
        # green for low risk through amber to red for high. This model
        # never predicts above ~0.2, so a fixed 0-1 domain would render
        # every bar the same green; mapping to the real range keeps the
        # color informative.
        low, high = 0.0, 0.21
        t = (float(pred) - low) / (high - low)
        t = min(max(t, 0.0), 1.0)
        bar_color = plt.get_cmap('RdYlGn_r')(t)

        ax.barh([''], [pred], color=bar_color)
        ax.set_xlim(0, 1)
        ax.set_title('Predicted Recruitment Risk', fontsize=20)
        self.set_axis_styling(ax, bordercolor='black', fontcolor='black')


# The two charts, side by side
class Visualizations(CombinedComponent):

    children = [
        LineChart(),
        BarChart()
    ]

    outer_div_type = Div(cls='grid')


class NotesTable(DataTable):

    def component_data(self, entity_id, model):

        notes = model.notes(entity_id)

        notes = notes.rename(columns={
            'note_date': 'Date',
            'note': 'Note',
            })

        # Newest note first
        return notes.sort_values('Date', ascending=False)


class DashboardFilters(FormGroup):

    id = "top-filters"
    action = "/update_data"
    method="POST"

    children = [
        Radio(
            values=["Employee", "Team"],
            name='profile_type',
            hx_get='/update_dropdown',
            hx_target='#selector'
            ),
        ReportDropdown(
            id="selector",
            name="user-selection")
        ]

class Report(CombinedComponent):

    children = [
        Header(),
        DashboardFilters(),
        Visualizations(),
        NotesTable()
    ]

report_css = (Path(__file__).resolve().parent.parent
              / "assets" / "report.css").read_text()

app = FastHTML(
    title="Employee Performance",
    hdrs=[Style(report_css)],
    )

report = Report()


def valid_ids(model):
    """The ids that actually exist for a model, as strings."""
    return {str(value) for _, value in model.names()}


def render(entity_id, model):
    """Render the report and set the page title to match the filter."""
    app.title = f"{model.name.title()} Performance"
    return report(entity_id, model)


@app.get('/')
def get_root():
    return render(1, Employee())


@app.get('/employee/{employee_id}')
def get_employee(employee_id: str):

    # An id with no matching row makes event_counts return an empty
    # frame, and matplotlib raises "no numeric data to plot" on it.
    if employee_id not in valid_ids(Employee()):
        return RedirectResponse('/employee/1', status_code=303)

    return render(employee_id, Employee())


@app.get('/team/{team_id}')
def get_team(team_id: str):

    # Same guard as the employee route: an unknown id yields no rows
    # to plot.
    if team_id not in valid_ids(Team()):
        return RedirectResponse('/team/1', status_code=303)

    return render(team_id, Team())


# Repopulate the dropdown when the entity type changes
@app.get('/update_dropdown{r}')
def update_dropdown(r):
    dropdown = DashboardFilters.children[1]
    if r.query_params['profile_type'] == 'Team':
        return dropdown(None, Team())
    elif r.query_params['profile_type'] == 'Employee':
        return dropdown(None, Employee())


@app.post('/update_data')
async def update_data(r):
    data = await r.form()
    profile_type = data._dict['profile_type']
    id = data._dict['user-selection']
    if profile_type == 'Employee':
        return RedirectResponse(f"/employee/{id}", status_code=303)
    elif profile_type == 'Team':
        return RedirectResponse(f"/team/{id}", status_code=303)



serve()
