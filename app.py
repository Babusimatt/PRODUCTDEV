import dash
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from utils.data_generator import generate_synthetic_data
from utils.analytics import get_summary_stats, sales_by, detect_anomalies, top_marketing_strategies
from utils.auth import authenticate
from dash.exceptions import PreventUpdate

# Initialize the app with Bootstrap theme
app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Base layout: stores session and routes view
app.layout = html.Div([
    dcc.Location(id='url'),
    dcc.Store(id='session', storage_type='session'),
    html.Div(id='content')
])

# Login screen layout
def login_layout():
    return dbc.Container([
        html.H2("Login", className="mb-4 text-center"),
        dbc.Input(id="username", placeholder="Username", type="text", className="mb-2"),
        dbc.Input(id="password", placeholder="Password", type="password", className="mb-3"),
        dbc.Button("Login", id="login-btn", color="primary", className="btn btn-primary w-100"),
        html.Div(id="login-alert", className="text-danger mt-3 text-center")
    ], style={"maxWidth": "400px", "marginTop": "100px"}, className="mx-auto")

# Dashboard layout, varies based on user role
def dashboard_layout(role):
    df = generate_synthetic_data(1000)
    logo_src = '/assets/logo_admin.jpg' if role == "admin" else '/assets/logo_user.jpg'

    # Dashboard tabs
    tabs = [
        dcc.Tab(label='Distribution by Location', children=[
            html.Div([
                html.Label("Select Continents:"),
                dcc.Dropdown(
                    id='continent-dropdown',
                    options=[{'label': c, 'value': c} for c in [
                        'Europe', 'North America', 'Asia', 'Africa', 'Oceania', 'South America']],
                    value=['Europe'], multi=True
                ),
                dcc.Graph(id='geo-distribution-graph')
            ])
        ]),
        dcc.Tab(label='Distribution By Time', children=[
            html.Div([
                html.Label("Select Time Unit:"),
                dcc.Dropdown(
                    id='time-unit-dropdown',
                    options=[{'label': i, 'value': i.lower()} for i in ['Hour', 'Day', 'Week', 'Month', 'Year']],
                    value='day'
                ),
                dcc.Graph(id='time-distribution-graph')
            ])
        ]),
        dcc.Tab(label='Distribution by Age', children=[
            html.Div([
                html.Label("Select Countries:"),
                dcc.Dropdown(
                    id='country-dropdown',
                    options=[{'label': loc, 'value': loc} for loc in df['location'].unique()],
                    value=[df['location'].unique()[0]], multi=True
                ),
                dcc.Graph(id='age-distribution-graph')
            ])
        ]),
        dcc.Tab(label='Summary Statistics', children=[
            html.Div(html.Pre(get_summary_stats(df)))
        ]),
        dcc.Tab(label='Marketing Strategies', children=[
            html.Div(dcc.Graph(figure=top_marketing_strategies(df)))
        ])
    ]

    if role == "admin":
        tabs.append(dcc.Tab(label='Anomalies', children=[
            html.Div(dcc.Graph(figure=detect_anomalies(df)))
        ]))

    return html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col(html.Img(src=logo_src, height="70px"), width="auto"),
                dbc.Col(html.H2("AI-Solution Business Intelligence Dashboard", className="my-auto text-center")),
                dbc.Col([
                    dbc.Button("Feedback", href="https://forms.office.com/Pages/ResponsePage.aspx?id=dykp7lh79E2BOFDQ3n0o2FXvAWPKJcJIkLt78GHgXp5UOUEwMldMOFdLNjNGVFJTTldUVTZTTE5WNC4u",
                               target="_blank", className="me-2", color="secondary"),
                    dbc.Button("Logout", id="logout-btn", color="danger")
                ], width="auto", className="d-flex justify-content-end align-items-center")
            ], className="align-items-center g-3 my-3")
        ]),

        dbc.Container([
            dcc.Tabs(tabs, className="mt-4")
        ])
    ])

# Route to login or dashboard
@app.callback(
    Output("content", "children"),
    Input("session", "data")
)
def display_page(session_data):
    if session_data and "role" in session_data:
        return dashboard_layout(session_data["role"])
    return login_layout()

# Handle login
@app.callback(
    Output("session", "data"),
    Output("login-alert", "children"),
    Input("login-btn", "n_clicks"),
    State("username", "value"),
    State("password", "value"),
    prevent_initial_call=True
)
def process_login(n_clicks, username, password):
    if not username or not password:
        return dash.no_update, "Username and password are required."
    role = authenticate(username, password)
    if role:
        return {"username": username, "role": role}, ""
    else:
        return dash.no_update, "Invalid credentials. Try again."

# Handle logout
@app.callback(
    Output("session", "data", allow_duplicate=True),
    Input("logout-btn", "n_clicks"),
    prevent_initial_call=True
)
def logout(n_clicks):
    return {}

# Update geo graph
@app.callback(
    Output('geo-distribution-graph', 'figure'),
    Input('continent-dropdown', 'value')
)
def update_geo_distribution(continents):
    df = generate_synthetic_data(1000)
    continent_map = {
        'Europe': ['UK', 'Germany', 'France', 'Spain', 'Italy', 'Russia'],
        'North America': ['USA', 'Canada', 'Mexico'],
        'Asia': ['India', 'China', 'Japan'],
        'Africa': ['South Africa', 'Nigeria', 'Kenya'],
        'Oceania': ['Australia', 'New Zealand'],
        'South America': ['Brazil']
    }
    selected_countries = []
    for continent in continents:
        selected_countries.extend(continent_map.get(continent, []))
    filtered_df = df[df['location'].isin(selected_countries)]
    return sales_by(filtered_df, 'location')

# Update time graph
@app.callback(
    Output('time-distribution-graph', 'figure'),
    Input('time-unit-dropdown', 'value')
)
def update_time_distribution(unit):
    df = generate_synthetic_data(1000)
    if unit == 'hour':
        df['time_unit'] = df['timestamp'].dt.hour
    elif unit == 'day':
        df['time_unit'] = df['timestamp'].dt.date
    elif unit == 'week':
        df['time_unit'] = df['timestamp'].dt.isocalendar().week
    elif unit == 'month':
        df['time_unit'] = df['timestamp'].dt.month
    elif unit == 'year':
        df['time_unit'] = df['timestamp'].dt.year
    return sales_by(df, 'time_unit')

# Update age graph
@app.callback(
    Output('age-distribution-graph', 'figure'),
    Input('country-dropdown', 'value')
)
def update_age_distribution(countries):
    df = generate_synthetic_data(1000)
    filtered_df = df[df['location'].isin(countries)]
    return sales_by(filtered_df, 'age')

# Run app
if __name__ == "__main__":
    app.run(debug=True)
