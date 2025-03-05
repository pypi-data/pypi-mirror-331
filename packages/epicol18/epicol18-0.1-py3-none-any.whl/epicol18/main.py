from pages.text_search import *
from pages.topwordspos import *
from pages.ngrams import *
from pages.kwic import *
from bs4 import BeautifulSoup
from pages.diachronic_search import *

def create_app():
    # Initialize the Dash app
    app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=['./assets/style.css'])

    # Apply global font-family for consistency
    app.layout = html.Div(style={'font-family': "Merriweather:serif" }), #'Arial, sans-serif'


    # Function to parse the HTML file and return Dash-compatible table
    def parse_html_table():
        with open('data/books_table.html', 'r') as f:  # Adjust path as necessary
            soup = BeautifulSoup(f, 'html.parser')
            table = soup.find('table')  # Locate the first table in the file
            if table:
                # Extract table headers
                headers = [col.get_text(strip=True) for col in table.find_all('th')]

                # Extract and transform table rows into dictionaries
                rows = []
                for row in table.find_all('tr')[1:]:  # Skip the header row
                    cells = row.find_all('td')
                    if cells:
                        row_data = {headers[i]: cell.get_text(strip=True) for i, cell in enumerate(cells) if i < len(headers)}
                        rows.append(row_data)

                return headers, rows
            else:
                return [], []  # No table found


    # Parse the table data into headers and rows
    table_headers, table_rows = parse_html_table()


    # Layout for the homepage
    about_page_layout = html.Div([

        html.Div([
            html.H1("EPICOL18", style={'backgroundColor': '#f6f6f6', 'textAlign': 'left', 'padding': '20px',
                                       'font-family': 'Arial, sans-serif', 'color': '#929585'}),
            html.Div([
                        html.Div([
                            dcc.Link(
                                'Top Words/POS',
                                href='/top_words_pos',
                                style={
                                    'textDecoration': 'none',
                                    'color': 'black',
                                    'padding': '10px 15px',
                                    'transition': 'background-color 0.3s ease',
                                    'font-family': 'Arial, sans-serif',
                                    "boxShadow": "2px 2px 5px rgba(0,0,0,0.2)",
                                    'backgroundColor': '#f6f6f6'

                                }
                            ),
                            dcc.Link(
                                'KWIC',
                                href="/kwic",
                                style={
                                    'textDecoration': 'none',
                                    'color': 'black',
                                    'padding': '10px 15px',
                                    'transition': 'background-color 0.3s ease',
                                    'font-family': 'Arial, sans-serif','backgroundColor': '#f6f6f6',
                                    "boxShadow": "2px 2px 5px rgba(0,0,0,0.2)"
                                }
                            ),
    dcc.Link(
                                'Diachronic Search',
                                href='/diachronic_search',
                                style={
                                    'textDecoration': 'none',
                                    'color': 'black',
                                    'padding': '10px 15px',
                                    'transition': 'background-color 0.3s ease', "boxShadow": "2px 2px 5px rgba(0,0,0,0.2)",
                                    'font-family': 'Arial, sans-serif','backgroundColor': '#f6f6f6'
                                }
                            ),
                            dcc.Link(
                                'Text Search',
                                href='/search',
                                style={
                                    'textDecoration': 'none',
                                    'color': 'black',
                                    'padding': '10px 15px',"boxShadow": "2px 2px 5px rgba(0,0,0,0.2)",
                                    'transition': 'background-color 0.3s ease',
                                    'font-family': 'Arial, sans-serif',
                                    'backgroundColor': '#f6f6f6'
                                }
                            ),
                            dcc.Link(
                                'N-Gram',
                                href="/ngrams",
                                style={
                                    'textDecoration': 'none',
                                    'color': 'black',
                                    'padding': '10px 15px',"boxShadow": "2px 2px 5px rgba(0,0,0,0.2)",
                                    'transition': 'background-color 0.3s ease',
                                    'font-family': 'Arial, sans-serif','backgroundColor': '#f6f6f6'
                                }
                            )
                        ], style={
                            'display': 'flex',
                            'flexDirection': 'column',  # Stack links vertically
                            'gap': '10px',  # Space between each link
                            'padding': '10px',
                        })
                    ], style={
                        'width': '60%'  # Allow the links to use the entire column space
                    })
                ],


            style={'width': '400px',
                'position': 'fixed',
                'top': '0',
                'left': '0',
                'height': '100vh',
                'backgroundColor': "#929585",    #'',
                'boxShadow': '2px 0 5px rgba(0,0,0,0.1)',
                   }),

        html.Footer(
            children=[
                html.Div("© ycvogt 2025", style={'textAlign': 'left', 'padding': '10px', 'font-family': 'Arial, sans-serif', 'color': '#f6f6f6', 'backgroundColor': '#929585'})
            ],
            style={'position': 'fixed', 'bottom': 0, 'left':0}
        ),

        # Content of the analysis page (for example, another graph or table)
        html.Div([
        html.Div([
            html.H1("Corpus of Long Eighteenth-Century Epistolary Novels",
                    style={'fontSize': '32px', 'textAlign': 'center', 'padding': '20px',"color":"#929585",
                           'font-family': 'Arial, sans-serif'}),
            html.H4(
                "Discover the Epistolary World of the Long 18th Century",
                style={
                    "textAlign": "center",
                    "color": "#555",
                    "fontSize": "18px",
                    "fontFamily": "Arial, sans-serif",
                    'padding': '5px'
                }
            )], style={"paddingBottom": "5px"}),

            html.P(
                "Explore this rich and dynamic digital corpus of epistolary novels from the late 17th to the early 19th century."
                " Uncover a collection of fictional letters and correspondences that reveal the intimate themes of love, duty, virtue, "
                "and class in early modern society. This interactive platform offers a variety of advanced tools to "
                "analyze trends and patterns:",
                style={
                    "fontSize": "16px",
                    "lineHeight": "1.8",
                    "padding": "15px 15px",
                    "textAlign": "justify",
                    "fontFamily": "Arial, sans-serif",
                }
            ),
            html.Ul([
                html.Li(
                    "Top Words/POS: Discover the most frequent words and parts-of-speech across the entire corpus or individual texts and visualize them in word clouds."
                    ,
                    style={"fontSize": "16px", "lineHeight": "1.8"}
                ),
                html.Li(
                    "Keyword-in-Context (KWIC): Investigate how specific words or phrases were used across the entire corpus, "
                    "authors, and timelines to uncover nuanced contexts and patterns.",
                    style={"fontSize": "16px", "lineHeight": "1.6"}
                ),
                html.Li(
                    "Diachronic Search: Visualize diachronic developments of search term frequencies across the entire corpus and visualize them in a line chart.",
                    style={"fontSize": "16px", "lineHeight": "1.6"}
                ),
                html.Li(
                    "Text Search: Search and compare the frequency of specific phrases across multiple texts and visualize their frequencies in a bar chart.",
                    style={"fontSize": "16px", "lineHeight": "1.6"}
                ),
                html.Li(
                    "N-Gram Analysis: Create and explore recurring linguistic patterns by generating n-grams"
                    "over selected texts.",
                    style={"fontSize": "16px", "lineHeight": "1.6"}
                ),

            ], style={
            'padding-left': '60px',
            'fontFamily': 'Arial, sans-serif'
        }),
            html.P(
                "This corpus interface is fully interactive: tweak search parameters, explore results visually, and download "
                "findings for in-depth analysis. "
                "Whether you’re a researcher, historian, linguist, or literary scholar, this digital tool provides a "
                "powerful way to explore historical fiction and examine the linguistic evolution of the 18th-century "
                "literary world.",
                style={
                    "fontSize": "16px",
                    "lineHeight": "1.8",
                    "padding": "15px 20px",
                    "textAlign": "justify",
                    "fontFamily": "Arial, sans-serif"
                }
            ),

            html.H4(
                "Corpus Structure",
                style={
                    "textAlign": "center",
                    "color": "#555",
                    "fontSize": "18px",
                    "fontFamily": "Arial, sans-serif",
                    'paddingBottom': '5px'
                }
            ),

            html.Div([
                dash_table.DataTable(
                    id="interactive-table",
                    columns=[{"name": header, "id": header} for header in table_headers],
                    data=table_rows,
                    page_size=15,
                    style_table={
                        'overflowX': 'auto',
                        "width": "95%",
                        'padding': "10px",
                    },
                    sort_action="native",
                    style_header={
                        'backgroundColor': '#f6f6f6',
                        'fontWeight': 'bold',
                        'textAlign': 'center',
                        'padding': "8px"
                    },
                    style_cell={"textAlign": "center"},
                    style_data={
                        'textAlign': 'center',
                        "fontSize": "14px",
                        'padding': '8px'
                    },
                    style_data_conditional=[
                        {
                            'if': {'state': 'selected'},

                            'backgroundColor': '#929585',
                            'color': 'black',
                            'border': '2px solid #555',
                            'textAlign': 'center'},
                    ],
                    fixed_columns={'headers': True},
                    editable=False
                ),
            ], style={
                #"border": "1px solid #ccc",
                #"boxShadow": "2px 2px 5px rgba(0,0,0,0.1)",
                "padding": "10px"
            }),

        ], style={'margin-left': '450px', 'padding': '20px', 'font-family': 'Arial, sans-serif', "margin-right":"80px",
                  "border": "1px solid #ccc"})
    ])


    app.layout = html.Div([
        dcc.Location(id="url", refresh=False),  # Keeps track of the current URL
        html.Div(id="page-content")  # This will render the current page's layout
    ])

    #### Callback for pages
    @app.callback(
        Output("page-content", "children"),
        [Input("url", "pathname")]
    )

    def display_page(pathname):
        if pathname == "/search":
            return search_page_layout # Display the search page layout
        elif pathname == "/diachronic_search":
            return diachronic_page_layout
        elif pathname == "/top_words_pos":
            return word_cloud_page_layout
        elif pathname == "/ngrams":
            return o_layout
        elif pathname == "/kwic":
            return kwic_layout
        else:
            return about_page_layout # Default to about page layout


    register_callbacks(app)
    word_cloud_callback(app)
    ngrams_callback(app)
    kwic_callbacks(app)
    diac_callbacks(app)

    return app

def run():
    app = create_app()
    # Run the app with `debug=False` for production
    app.run_server(debug=False)

# Run the app
if __name__ == '__main__':
    #app.run_server(debug=True)
    run()
