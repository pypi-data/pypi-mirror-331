import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import sqlite3
import pandas as pd
import plotly.express as px
import re

#counts match count/total count of words for the year times 1 million

# Define Layout
diachronic_page_layout = html.Div([
    # Sidebar for input
    html.Div([
        html.H1("EPICOL18", style={
            'font-family': 'Arial, sans-serif',
            'padding': '20px',
            'backgroundColor': '#f6f6f6',
            'color': '#929585'}),

        html.Div([
            html.Label("Search Query (REGEX):", style={'font-family': 'Arial, sans-serif', 'color': '#555'}),
            dcc.Input(
                id="diachronic-search-input",
                type="text",
                value="polite\\w+",
                debounce=True,
                style={
                    "width": "100%",
                    "border": "1px solid #ccc",
                    "borderRadius": "4px",
                    "boxShadow": "none",
                    'height': '40px',
                    'padding': '0',
                })
        ], style={'width': 'auto', 'padding': '10px', 'backgroundColor': '#f6f6f6'}),

        html.Div([dcc.Link('Back', href='/',
                           style={'margin': '20px', 'textDecoration': 'none', 'color': '#555',
                                  })],
                 style={'textAlign': 'left', 'padding': '10px', 'backgroundColor': '#f6f6f6',
                        'font-family': 'Arial, sans-serif',
                        "position": "absolute", "bottom": "0",
                        'borderRadius': '8px', 'boxShadow': '2px 0 10px rgba(0, 0, 0, 0.1)'}),

    ], style={'width': '400px', 'position': 'fixed', 'top': '0', 'left': '0',
              'height': '100vh', 'backgroundColor': '#929585', 'boxShadow': '2px 0 5px rgba(0,0,0,0.1)'}),

    # Main Graph visualization area
    html.Div([
        html.H1("Diachronic Search", style={'fontSize': '32px', 'textAlign': 'center', "color": "#929585",
                                            'padding': '20px', 'font-family': 'Arial, sans-serif'}),
        dcc.Loading(id="loading-1", type="circle", children=[
            html.Div([dcc.Graph(id="diachronic-line-plot", figure={})])
        ])
    ], style={'padding': '20px', 'margin-left': '400px'}),
])


# Query function for database interaction
def query_diachronic_data(query):
    """Query the database and return raw match counts and token counts over time."""
    conn = sqlite3.connect('./data/books.db')
    c = conn.cursor()

    # Fetch book data
    c.execute('SELECT title, year, tokenized_content FROM books')
    results = c.fetchall()
    matched_records = []
    token_counts_by_year = {}

    total_corpus_tokens = 0  # Total token count across the entire corpus

    for title, year, tokens in results:
        # Regex matching for the given search term
        matches = re.findall(query, tokens)  # Regex search matches
        match_count = len(matches)  # Raw number of matches

        # Tokenize content
        cleaned_tokens = [word.lower() for word in tokens.split(",") if word.isalpha()]
        token_count = len(cleaned_tokens)  # Token count for this record

        # Aggregate match counts by year
        if year not in token_counts_by_year:
            token_counts_by_year[year] = 0
        token_counts_by_year[year] += token_count

        # Record the raw number of matches
        matched_records.append({
            "Year": year,
            "Match Count": match_count
        })

        # Keep track of the total word count across all records
        total_corpus_tokens += token_count

    # Aggregate match counts by year
    df_matches = pd.DataFrame(matched_records)
    if df_matches.empty:
        conn.close()
        return pd.DataFrame(), 0

    # Group matches by year
    df_grouped_matches = df_matches.groupby('Year')['Match Count'].sum().reset_index()

    # Normalize by the total number of words across the corpus
    if total_corpus_tokens > 0:
        df_grouped_matches['Normalized Matches'] = df_grouped_matches['Match Count'] / total_corpus_tokens * 1_000_000
    else:
        df_grouped_matches['Normalized Matches'] = 0  # Handle edge case if token counts are zero

    conn.close()

    return df_grouped_matches, total_corpus_tokens


# Set up callbacks
def diac_callbacks(app):
    @app.callback(
        Output("diachronic-line-plot", "figure"),
        [Input("diachronic-search-input", "value")]
    )
    def update_diachronic_line_plot(search_term):
        # Query database for results
        df, total_corpus_tokens = query_diachronic_data(search_term)

        if df.empty or total_corpus_tokens == 0:
            fig = px.line()
            fig.update_layout(title="No results found or invalid search term")
            return fig

        # Generate line chart for normalized match counts
        fig = px.line(
            df,
            x="Year",
            y="Normalized Matches",
            title=f"Normalized Frequency of Matches for '{search_term}' Over Time",
            labels={"Normalized Matches": "Matches per Million Tokens", "Year": "Year"},
            markers=True,
            hover_data={"Match Count": True}
        )

        fig.update_layout(
            template="plotly_white",
            autosize=True,
            margin=dict(t=100, b=50, l=50, r=50),
            showlegend=True
        )
        fig.update_traces(marker_color='#929585', line=dict(color='#929585', width=2))

        return fig
