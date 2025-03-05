from dash import dcc, html, Input, Output
from dash.dash_table import DataTable
import dask.dataframe as dd
import pandas as pd
import re
import dash
import os
#n-gram's frequency by the total n-gram count and then scaling it to represent "per 10,000 words".

# Layout
o_layout = html.Div([
    html.Div([
        html.H1("EPICOL18", style={'color': '#929585', 'padding': '20px', 'backgroundColor': '#f6f6f6',
                                   'font-family': 'Arial, sans-serif'}),
        # Dropdown for selecting books
        html.Div([
            html.Label("Select Books:", style={'color': '#555'}),
            dcc.Dropdown(
                id="book-dropdown",
                options=[
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
                    {"label": "Olinda's Adventures", "value": "Olinda's Adventures"}],
                multi=True,
                placeholder="...",
                value=["Evelina"],
                searchable=True,
                style={
                    'width': '100%',
                    'border': '1px solid #ccc',  # Adding a border to match input
                    'borderRadius': '4px',  # Matching rounded corners
                    'boxShadow': 'none',  # Optional: Remove the default box shadow
                    'height': 'auto',
                    'padding': '0',
                }
            ),
        ], style={'width': 'auto', 'color': '#555', 'padding': '10px',
                  'backgroundColor': '#f6f6f6', 'font-family': 'Arial, sans-serif'
                  }),

        # Input field for searching specific word in n-grams
        html.Div([
            html.Label("Search Query (REGEX):", style={'color': '#555'}),
            dcc.Input(id='word-input', type='text', placeholder="Enter a word...", value="\\bhonour\\b", style={
                "width": "100%",
                "border": "1px solid #ccc",  # Adding a border to match dropdown
                "borderRadius": "4px",  # Rounded corners to match dropdown
                "boxShadow": "none",  # Optional: Remove default box shadow
                'height': '40px', 'padding': '0',
            })],
            style={'color': '#555', 'padding': '10px', 'backgroundColor': '#f6f6f6', 'font-family': 'Arial, sans-serif',
                   'width': 'auto'}),

        # Slider for selecting n-gram size
        html.Div([
            html.Label("N-Gram Size:", style={'color': '#555'}),
            dcc.Slider(id='ngram-window-slider',
                       min=2, max=5, step=1, marks={i: str(i) for i in range(2, 6)}, value=2,
                       tooltip={"placement": "bottom", "always_visible": True})],
                 style={"width":"auto",'padding': '10px', 'backgroundColor': '#f6f6f6', 'font-family': 'Arial, sans-serif'}),

        # Navigation to other pages
        html.Div([dcc.Link('Back', href='/',
                           style={'margin': '20px', 'textDecoration': 'none', 'color': '#555',
                                  })],
                 style={'textAlign': 'left', 'padding': '10px', 'backgroundColor': '#f6f6f6',
                        'font-family': 'Arial, sans-serif',
                        "position": "absolute", "bottom": "0",
                        'borderRadius': '8px', 'boxShadow': '2px 0 10px rgba(0, 0, 0, 0.1)'}),

    ], style={'width': '400px', 'position': 'fixed', 'top': '0', 'left': '0', 'height': '100vh',
              'backgroundColor': '#929585', 'boxShadow': '2px 0 5px rgba(0,0,0,0.1)', }),

    # Right panel
    html.Div([
        html.H1("N-Gram Tool", style={'fontSize': '32px', 'textAlign': 'center',"color":"#929585",
                                      'padding': '20px','font-family': 'Arial, sans-serif'}),

        # Loading circle always at the top
        dcc.Loading(id="loading-1", type="circle", children=[

            html.Div(id="error-message2", style={"color":"rgb(85, 85, 85)", "fontWeight": "bold",'font-family': 'Arial, sans-serif',
                                                      "fontSize": "20px","marginTop":"5px",
                                                      "padding": "10px"}),

            # Table container
            html.Div(
                [DataTable(
                    id='ngram-table',
                    columns=[
                        {"name": "N-Gram", "id": "N-Gram"},
                        {"name": "Frequency", "id": "Frequency"},
                        {"name": "Relative Frequency", "id": "Relative Frequency"}
                    ],
                    page_size=10,
                    style_table={"overflowY": "auto", "width": "auto"},
                    style_cell={"textAlign": "left", "padding": "10px"},
                    style_data_conditional=[
                        {
                        'if': {'state': 'selected'},  # Target selected cells
                        'backgroundColor': '#dddddd',
                        'color': 'black',  # Text color
                        'border': '2px #343d46'
                        },
                    ],
                sort_action='native',
                sort_by=[{"column_id": "Relative Frequency", "direction": "desc"}]
                )],
                id="ngram_table-container",
                style={"display": "none"}  # Default hidden

            ),

            html.Div([
            html.Button("Download", id="ngram_download-button", n_clicks=0,
                        style={
                            "backgroundColor": "rgb(246, 246, 246)",
                            "color": "#333333",
                            "border": "1px solid rgb(246, 246, 246)",
                            "borderRadius": "4px",
                            "padding": "8px 16px",
                            "fontSize": "14px",
                            "cursor": "pointer",
                            "transition": "all 0.2s ease",
                        })
            ]),

            # Hidden download link for the CSV download
            dcc.Download(id="ngram_download-dataframe-csv"),

        ], style={'position': 'absolute', 'top': '20px', 'left': '50%', 'transform': 'translateX(-50%)',
                          'z-index': '100', 'padding': '20px'}),

    ], style={'margin-left': '400px', 'padding': '20px', "overflow-y": "auto"})
])


def get_ngram_frequencies(selected_books, ngram_size, input_word):
    # Ensure selected_books is a list
    if isinstance(selected_books, str):
        selected_books = [selected_books]

    # Load the appropriate n-gram file based on selected ngram size
    file_name = os.path.join('data', f'ngrams_{ngram_size}.csv')
    #file_name = f'ngrams_{ngram_size}.csv'

    try:
        df = dd.read_csv(file_name, blocksize="16MB",
                         dtype={'Book Title': 'str', 'N-Gram': 'str', 'Frequency': 'int64'})
    except Exception as e:
        print(f"Error loading file: {e}")
        return {}, 0

    df = df.persist()

    # Filter by selected books
    filtered_data = df[df['Book Title'].isin(selected_books)]

    # Apply the input word filter (regex search)
    if input_word:
        filtered_data = filtered_data[
            filtered_data['N-Gram'].str.contains(input_word, case=False, na=False, regex=True)]

    # Check if there's any data left after filtering
    if len(filtered_data) == 0:
        print("No data after filtering.")
        return {}, 0

    # Calculate the total frequency count
    total_ngram_count = filtered_data['Frequency'].sum().compute()

    # Group by 'N-Gram' and aggregate frequencies
    ngram_freq = filtered_data.groupby('N-Gram')['Frequency'].sum().compute().to_dict()

    return ngram_freq, total_ngram_count


def ngrams_callback(app):
    @app.callback(
        [
            Output('ngram-table', 'data'),
            Output('error-message2', 'children'),
            Output('ngram_table-container', 'style')
        ],
        [
            Input('word-input', 'value'),
            Input('book-dropdown', 'value'),
            Input('ngram-window-slider', 'value')
        ]
    )
    def update_ngram_analysis(word, selected_books, ngram_size):
        # Ensure that a book is selected
        if not selected_books:
            return [], "Please select at least one book to proceed.", {"display": "none"}

        # Validate the regex input
        try:
            if word:
                re.compile(word)  # Validate regex
        except re.error:
            return [], "Invalid regular expression. Please try again.", {"display": "none"}

        # Fetch n-gram frequencies
        ngram_freq, total_ngram_count = get_ngram_frequencies(selected_books, ngram_size, word)

        # Handle case where no data is found
        if not ngram_freq or total_ngram_count == 0:
            return [], "No matching terms found. Try a different search term.", {"display": "none"}

        # Prepare the relative frequencies and data
        relative_frequencies = [(ngram, (freq / total_ngram_count) * 100) for ngram, freq in ngram_freq.items()]
        sorted_ngrams = sorted(relative_frequencies, key=lambda x: x[1], reverse=True)[:50]
        ngrams = [x[0] for x in sorted_ngrams]
        relative_freqs = [x[1] for x in sorted_ngrams]

        # Prepare table data
        table_data = [
            {
                "N-Gram": ngram,
                "Frequency": ngram_freq[ngram],
                "Relative Frequency": round(relative_freq, 2)
            }
            for ngram, relative_freq in zip(ngrams, relative_freqs)
        ]

        # Ensure table data is valid
        if not table_data:
            return [], "No data to display.", {"display": "none"}

        # Return table data and show the table
        return table_data, "", {"display": "block"}

    @app.callback(
        Output("ngram_download-dataframe-csv", "data"),
        [Input("ngram_download-button", "n_clicks")],
        [Input("ngram-table", "data")]
    )
    def handle_download(n_clicks, table_data):
        if n_clicks and table_data:
            # Convert table data into a DataFrame
            df = pd.DataFrame(table_data)
            return dcc.send_data_frame(df.to_csv, "ngram_table.csv", index=False)

        return dash.no_update