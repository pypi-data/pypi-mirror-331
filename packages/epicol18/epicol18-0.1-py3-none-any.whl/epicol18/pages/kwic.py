from dash import dcc, html, Input, Output
import sqlite3
import re

# App layout
kwic_layout = html.Div([
    html.Div([
        html.H1("EPICOL18", style={'color': '#929585', 'padding': '20px', 'backgroundColor': '#f6f6f6',
                                   'font-family': 'Arial, sans-serif'}),
        # Input for regex query
        html.Div([
            html.Label("Search Query (REGEX)",style={'color': '#555'}),
            dcc.Input(id="regex-input", type="text", debounce=True, placeholder="Enter a regex pattern...",
                      value="delight\w+",
                      style={
                          "width": "100%",
                          "border": "1px solid #ccc",  # Adding a border to match dropdown
                          "borderRadius": "4px",  # Rounded corners to match dropdown
                          "boxShadow": "none",  # Optional: Remove default box shadow
                          'height': '40px', 'padding': '0'
                      }
                      ),

        ], style={'color': '#555', 'padding': '10px', 'backgroundColor': '#f6f6f6', 'font-family': 'Arial, sans-serif',
                   'width': 'auto'}),

            html.Div([dcc.Link('Back', href='/',
                           style={'margin': '20px', 'textDecoration': 'none', 'color': '#555',
                                  })],
                 style={'textAlign': 'left', 'padding': '10px', 'backgroundColor': '#f6f6f6',
                        'font-family': 'Arial, sans-serif',
                        "position": "absolute", "bottom": "0",
                        'borderRadius': '8px', 'boxShadow': '2px 0 10px rgba(0, 0, 0, 0.1)'}),

    ], style={'width': '400px', 'position': 'fixed', 'top': '0', 'left': '0', 'height': '100vh',
              'backgroundColor': '#929585', 'boxShadow': '2px 0 5px rgba(0,0,0,0.1)'}),

    # Right side
    html.Div([
        html.H1("Key-Word-In-Context", style={'fontSize': '32px', 'textAlign': 'center',"color":"#929585",
                                      'padding': '20px','font-family': 'Arial, sans-serif'}),

        html.Div([
            dcc.Loading(
                id="loading-1",
                type="circle",
                children=[
                    html.Div(id="total-hits", style={"fontWeight": "bold", "marginBottom": "10px"}),
                    html.Div(id="results-container", children=[]),
                ]
            )
        ])

    ], style={'margin-left': '400px', 'padding': '20px', "overflow-y": "auto"})
])

# Custom REGEXP function to add regex support
def regexp(pattern, value):
    """Define regex support for SQLite."""
    if value is None:
        return False
    return re.search(pattern, value, re.IGNORECASE) is not None


# Function to query database using REGEXP
def query_corpus_db_with_fts(regex_pattern):
    """Query database using SQLite's REGEXP capabilities."""
    try:
        conn = sqlite3.connect('./data/books.db')
        # Register custom REGEXP function for SQLite
        conn.create_function("REGEXP", 2, regexp)
        cursor = conn.cursor()

        # Search query using REGEXP
        cursor.execute(
            "SELECT year, title, tokenized_content FROM books_fts WHERE tokenized_content REGEXP ?",
            (regex_pattern,)
        )
        results = cursor.fetchall()
        conn.close()

        # Extract KWIC contexts from matched content
        final_results = []
        for year, title, tokenized_string in results:
            try:
                if tokenized_string:
                    # Preprocess tokenized string
                    tokenized_string = tokenized_string.replace(',', ' ')
                    # Extract all matches and their contexts
                    matches = extract_all_contexts(tokenized_string, regex_pattern)
                    if matches:
                        final_results.extend([
                            {
                                "year": year,
                                "title": title,
                                "left_context": match["left"],
                                "token": match["match"],
                                "right_context": match["right"]
                            }
                            for match in matches
                        ])
            except Exception as e:
                print(f"Skipping invalid database entry: {e}")

        return final_results
    except Exception as e:
        print(f"Error querying database with regex: {e}")
        return []


# Function to extract **all occurrences** of context around FTS search hits
def extract_all_contexts(tokenized_string, regex_pattern, window_size=5):
    """
    Extract left and right contexts for all occurrences of the regex pattern.
    Loops over all matches in the string.
    """
    try:
        matches = []
        tokens = tokenized_string.split()

        # Find matches and compute contexts for each match
        for index, word in enumerate(tokens):
            if re.search(regex_pattern, word, re.IGNORECASE):
                left_start = max(index - window_size, 0)
                right_end = min(index + window_size + 1, len(tokens))

                left_context = ' '.join(tokens[left_start:index])
                right_context = ' '.join(tokens[index + 1:right_end])

                # Save context information
                matches.append({
                    "left": left_context,
                    "match": word,
                    "right": right_context
                })

        return matches
    except Exception as e:
        print(f"Regex context extraction failed: {e}")
    return []


# Function to safely highlight matches in the context
def highlight_matches_safe(text, regex_pattern):
    """
    Highlight matches by wrapping them in styled spans without using raw HTML.
    """
    try:
        # Split the text using regex
        parts = re.split(f"({regex_pattern})", text, flags=re.IGNORECASE)
        highlighted = [
            html.Span(
                part,
                style={"fontWeight": "bold", "color": "#929585"}
            ) if re.search(regex_pattern, part, flags=re.IGNORECASE) else part
            for part in parts
        ]
        return highlighted
    except Exception as e:
        print(f"Regex invalid for highlighting: {e}")
        return [text]


# Callback
def kwic_callbacks(app):
    @app.callback(
        [Output("total-hits", "children"),
         Output("results-container", "children")],
        Input("regex-input", "value")
    )
    def display_results(regex_pattern):
        if not regex_pattern:
            # No clicks yet or invalid regex string
            return html.Div(), html.Div()

        try:
            # Query database using REGEXP
            results = query_corpus_db_with_fts(regex_pattern)

            if not results:
                return html.Div(
                    "No contexts found for the given search pattern.",
                    style={
                        "fontFamily": "Arial, sans-serif",
                        "fontSize": "16px",
                        "color": "black",
                        "fontWeight": "bold",
                        "marginBottom": "10px"
                    }
                ), html.Div([])

            # Dynamically generate the table with the results
            table_header = [
                html.Tr([
                    html.Th("Left Context", style={"textAlign": "right", "fontSize": "16px"}),
                    html.Th("Token", style={"textAlign": "center", "fontSize": "16px"}),
                    html.Th("Right Context", style={"textAlign": "left", "fontSize": "16px"}),
                    html.Th("Year", style={"textAlign": "left", "fontSize": "16px"}),
                    html.Th("Reference", style={"textAlign": "left", "fontSize": "16px"})
                ])
            ]

            table_rows = [
                html.Tr([
                    html.Td(
                        highlight_matches_safe(row["left_context"], regex_pattern),
                        style={"textAlign": "right"}
                    ),
                    html.Td(
                        html.Span(row["token"], style={"fontWeight": "bold", "color": "#929585"}),
                        style={"textAlign": "center"}
                    ),
                    html.Td(
                        highlight_matches_safe(row["right_context"], regex_pattern),
                        style={"textAlign": "left"}
                    ),
                    html.Td(row["year"], style={"textAlign": "left"}),
                    html.Td(row["title"], style={"textAlign": "left"})
                ])
                for row in results
            ]

            table = html.Table(
                table_header + table_rows,
                style={
                    "maxHeight": "500px",
                    "overflowY": "scroll",
                    "overflowX": "scroll",
                    "padding": "10px",
                    "fontFamily": "Arial, sans-serif",
                    "fontSize": "14px",
                }
            )

            total_hits_message = html.Div(
                f"Total hits found: {len(results)}",
                style={
                    "fontFamily": "Arial, sans-serif",
                    "fontSize": "18px",
                    "color": "black",
                    "fontWeight": "bold",
                    "marginBottom": "10px"
                }
            )

            return total_hits_message, table
        except Exception as e:
            print(f"Error processing regex request: {e}")
            return html.Div(
                f"Error: {str(e)}",
                style={
                    "fontFamily": "Arial, sans-serif",
                    "fontSize": "18px",
                    "color": "black",
                    "fontWeight": "bold",
                    "marginBottom": "10px"
                }
            ), html.Div([])
