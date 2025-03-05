from dash import dcc, html
from dash.dependencies import Input, Output
import sqlite3
import pandas as pd
import plotly.express as px
import re
from dash import dash_table
import plotly.graph_objects as go
from collections import Counter


#Layout
search_page_layout=html.Div([
    ### left side page 1
    html.Div([
    ### headline and description
    html.H1("EPICOL18", style={'padding': '20px', 'backgroundColor': '#f6f6f6', 'color': '#929585'}),

    # Input for search term
    html.Div([
        html.Label("Search Query (REGEX):", style={'color': '#555'}),
        dcc.Input(id="search-input", type="text", value="polite\w+", debounce=True, style={
                "width": "100%",
                "border": "1px solid #ccc",  # Adding a border to match dropdown
                "borderRadius": "4px",  # Rounded corners to match dropdown
                "boxShadow": "none",  # Optional: Remove default box shadow
                'height': '40px', 'padding': '0',
            })
    ], style={'width': 'auto', 'padding': '10px', 'backgroundColor': '#f6f6f6'}),


    # Dropdown for selecting books
    html.Div(style={'display': 'flex', 'flexDirection': 'column', 'padding': '10px',
                    'marginTop': '0px', 'alignItems': 'left', 'width': '380px', 'backgroundColor': '#f6f6f6'},
    children=[
        html.Label("Text Selection:", style={'color': '#555', 'alignItems': 'left'}),
        dcc.Dropdown(
            id="book-dropdown",
            options=[
                {"label": "All Books", "value": "all"},
                {"label": "Love-Letters Between a Nobleman and His Sister", "value": "A Nobleman and His Sister"},
                {"label": "The Lover's Secretary", "value": "The Lover\'s Secretary"},
                {"label": "Evelina", "value": "Evelina"},
                {"label": "The Sylph", "value": "The Sylph"},
                {"label": "Familiar Letters Betwixt a Gentleman and a Lady", "value": "Familiar Letters"},
                {"label": "The Reform'd Coquet", "value": "The Reform'd Coquet"},
                {"label": "Leonora", "value": "Leonora"},
                {"label": "An Apology for the Life of Mrs. Shamela Andrews", "value": "Shamela"},
                {"label": "The History of Lady Barton", "value": "Lady Barton"},
                {"label": "The Story of Lady Juliana Harley", "value": "Lady Juliana Harley"},
                {"label": "The Delicate Distress", "value": "Delicate Distress"},
                {"label": "A series of genuine letters between Henry and Frances", "value": "Genuine Letters"},
                {"label": "Barford Abbey", "value": "Barford Abbey"},
                {"label": "The Anti-Pamela", "value": "The Anti-Pamela"},
                {"label": "The Fatal Secret", "value": "The Fatal Secret"},
                {"label": "Idalia", "value": "Idalia"},
                {"label": "Love in Excess", "value": "Love in Excess"},
                {"label": "The History of Miss Betsy Thoughtless", "value": "Miss Betsy"},
                {"label": "Alwyn", "value": "Alwyn"},
                {"label": "Anna St. Ives", "value": "Anna St. Ives"},
                {"label": "Hermione", "value": "Hermione"},
                {"label": "Mrs. Manley", "value": "Letters written by Mrs. Manley"},
                {"label": "Clarissa", "value": "Clarissa"},
                {"label": "Pamela", "value": "Pamela"},
                {"label": "The History of Sir Charles Grandison", "value": "Sir Charles Grandison"},
                {"label": "Frankenstein", "value": "Frankenstein"},
                {"label": "The Expedition of Humphry Clinker", "value": "Humphry Clinker"},
                {"label": "Olinda's Adventures", "value": "Olinda's Adventures"}
            ],
            multi=True,  # Allow multiple selections
            value=["all"],  # Default to all books selected
            searchable=True,
            style={
                "width": "100%",
                "border": "1px solid #ccc",  # Adding a border to match dropdown
                "borderRadius": "4px",  # Rounded corners to match dropdown
                "boxShadow": "none",  # Optional: Remove default box shadow
                'height': '40px',
                'padding': '0',
            }
        )
    ]
    ),

    # Navigation to other pages
    html.Div([
        html.Div([
            dcc.Link('Back', href='/', style={'margin': '20px', 'textDecoration': 'none', 'color': '#555',
                                              }),
        ], style={'textAlign': 'left', 'padding': '10px', 'backgroundColor': '#f6f6f6',
                  'font-family': 'Arial, sans-serif', "color": "#929585",
                  "position": "absolute", "bottom": "0",
                  'borderRadius': '8px', 'boxShadow': '2px 0 10px rgba(0, 0, 0, 0.1)'})
    ]),
    # Sidebar style of the page, all the elements above are on the left
    ], style={'width': '400px',  # Sidebar width
            'position': 'fixed',  # Keep it fixed on the left
            'top': '0',
            'left': '0',
            'height': '100vh',  # Full height of the page
            'backgroundColor': '#929585',
            'boxShadow': '2px 0 5px rgba(0,0,0,0.1)',
           }),

    ### right side of page search
    html.Div([
        html.H1("Text Search Tool",
                style={'fontSize': '32px', 'textAlign': 'center',
                       'padding': '20px','font-family': 'Arial, sans-serif', "color":"#929585"}),

        # Loading circle always at the top
        dcc.Loading(id="loading-1", type="circle", children=[

            # Total match count display
            html.Div([html.Label(id="total-count", style={"fontSize": "20px","color":"rgb(85, 85, 85)",
                                                'padding': '10px', "marginTop":"5px"})]),

            # Error message display
            html.Div([
                html.Br(),
                html.Label(id="error-message", style={"color":"rgb(85, 85, 85)", "fontWeight": "bold",
                                                      "fontSize": "20px","marginTop":"5px",
                                                      "padding": "10px"})],
                 ),

            # Table to display search results with horizontal and vertical scrolling
            html.Div([
                dash_table.DataTable(id="table-container",
                                     style_table={
                                         'overflowX': 'auto',  # Enable horizontal scrolling
                                         'overflowY': 'auto',  # Enable vertical scrolling
                                         'maxHeight': '400px',  # Set a fixed height
                                         'maxWidth': '100%'     # Ensure the table stays within the container width
                                     },
                                     style_cell={
                                         'textAlign': 'left',  # Align all text to the left by default
                                         'padding': '10px'     # Padding for cells
                                     },
                                     style_data_conditional=[
                                         {
                                             'if': {'state': 'selected'},  # Target selected cells
                                             'backgroundColor': '#dddddd',
                                             'color': 'black',  # Text color
                                             'border': '2px #343d46'
                                         },
                                    ],
                                     sort_action='native', #allows sorting desc/asc every column
                                     sort_by=[{"column_id": "Normalized Frequency", "direction": "desc"}]
                                     #filter_action='native', #filters rows
                                     )
            ], style={'padding': '10px', "fontSize": "12px"}),

            # Button to trigger download
            html.Div([
                html.Button("Download", id="download-button",
                            style={
                                "backgroundColor": "rgb(246, 246, 246)",
                                "color": "#333333",
                                "border": "1px solid rgb(246, 246, 246)",
                                "borderRadius": "4px",
                                "padding": "8px 16px",
                                "fontSize": "14px",
                                "cursor": "pointer",
                                "transition": "all 0.2s ease",
                            }),
                dcc.Download(id="download-dataframe-csv")
            ], id="download-button-container", style={'padding': '20px'}),

            # Graph to display frequency of search term
            html.Div([
                html.Div([dcc.Graph(id="frequency-graph", figure={'layout': {
                    'title': 'Bar Chart with No Background or Gridlines',
                    'plot_bgcolor': 'rgba(0,0,0,0)',  # Transparent plot area
                    'paper_bgcolor': 'rgba(0,0,0,0)',  # Transparent overall background
                    'xaxis': {
                        'showgrid': False,  # Remove gridlines on the x-axis
                        'zeroline': False,  # Remove the zero line on the x-axis
                        'showline': False,  # Remove the x-axis line
                        'ticks': '',         # Remove axis ticks
                    },
                    'yaxis': {
                        'showgrid': False}}}
                                    , style={'height': '650px', 'width': '100%'})],
                         id="frequency-graph-container",
                         style={'display': 'none'}),  # Default hidden until valid input
            ], style={'padding': '20px'}),

        ], style={'position': 'absolute', 'top': '0', 'left': '50%', 'transform': 'translateX(-50%)',
                  'z-index': '100', 'padding': '20px'}),

    ], style={'margin-left': '400px', 'padding': '20px'}),

], style={'font-family': 'Arial, sans-serif'})


def query_books(query):
    conn = sqlite3.connect('./data/books.db')
    c = conn.cursor()

    total_word_count = 0
    matched_results = []
    total_count = 0

    # Query the books table for the content
    c.execute('''SELECT title, author, year, tokenized_content FROM books''')  # Fetch all books content
    results = c.fetchall()

    for row in results:
        title, author, year, tokens = row
        word_count = 0
        cleaned_content = [word.lower() for word in tokens.split(",") if word.isalpha()]
        counted_words = Counter(cleaned_content)
        word_count += sum(counted_words.values())
        total_word_count += word_count

        # Search for matches using regex (convert query to lowercase to match)
        matches = re.findall(query, tokens)  # both content and query are lowercase
        match_count = len(matches)

        if match_count > 0:
            match_freq = {match: matches.count(match) for match in set(matches)}
            match_list = [f"{match} ({freq})" for match, freq in match_freq.items()]
            total_match_count = sum(match_freq.values())  # Total count for the book
            matched_results.append((", ".join(match_list), total_match_count, word_count, title, author, year))
            total_count += match_count

    conn.close()

    return pd.DataFrame(matched_results, columns=["Match (Raw Frequency)", "Total Matches", "Token Total",
                                                  "Title", "Author", "Year"
                                                  ]), total_word_count


def register_callbacks(app):
    @app.callback(
        [Output("table-container", "data"),
         Output("table-container", "columns"),
         Output("frequency-graph", "figure"),
         Output("total-count", "children"),
         Output("download-dataframe-csv", "data"),
         Output("error-message", "children"),
         Output("download-button-container", "style"),
         Output("frequency-graph-container", "style")],  # Control visibility of the graph container
        [Input("book-dropdown", "value"),
         Input("search-input", "value"),
         Input("download-button", "n_clicks")]
    )
    def update_results(selected_books, search_term, n_clicks):
        error_message = None
        data = []
        columns = []
        fig = go.Figure()
        total_count_message = "Matches across all selected books: 0"

        try:
            if "all" in selected_books:
                selected_books = []

            # Query the books database
            results_df, total_count = query_books(search_term)

            # Handle no results case
            if results_df.empty:
                error_message = f"No results found for the search query '{search_term}'. Try a different search query."
                return data, columns, {}, total_count_message, None, error_message, {'display': 'none'}, {
                    'display': 'none'}

        # Handle regex errors
        except re.error:
            error_message = "Invalid regex syntax. Please check your search query."
            return data, columns, {}, total_count_message, None, error_message, {'display': 'none'}, {'display': 'none'}

        # Calculate normalized frequencies
        results_df.insert(2, 'Normalized Frequency', round((results_df['Total Matches'] / total_count) * 10000, 5))

        # Handle selection filtering
        if selected_books:
            results_df = results_df[results_df["Title"].isin(selected_books)]

        if results_df.empty:
            error_message = f"No results found for the search query '{search_term}' in the selected book(s)."
            return data, columns, {}, total_count_message, None, error_message, {'display': 'none'}, {'display': 'none'}

        # Set columns and prepare data
        columns = [{"name": col, "id": col} for col in results_df.columns]
        data = results_df.to_dict('records')

        # Create the frequency bar graph
        fig = px.bar(results_df, x="Title", y="Normalized Frequency",
                     hover_data=["Year", "Author"], template="plotly_white",
                     title=f"Normalized Frequency of matches for '{search_term}'",
                     labels={"Normalized Frequency": "Normalized Frequency (per 10,000 words)"})
        fig.update_layout(xaxis_title=None)
        fig.update_traces(marker_color='#929585')
        fig.update_layout(
            autosize=True,
            margin=dict(t=150, b=50, l=100, r=50),
            showlegend=False
        )

        total_count_message = f"Matches across all selected books: {results_df['Total Matches'].sum()}"

        # Handle download button logic only if clicked and no error exists
        if n_clicks and error_message is None:
            return data, columns, fig, total_count_message, dcc.send_data_frame(results_df.to_csv,
                                                                                "epicol18_results.csv"), error_message, {
                       'padding': '20px'}, {'display': 'block'}

        # Default visible state with no errors
        return data, columns, fig, total_count_message, None, None, {'padding': '20px'}, {'display': 'block'}
