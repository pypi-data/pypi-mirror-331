from dash import dcc, html
from dash.dependencies import Input, Output
import sqlite3
from collections import Counter
import re
from wordcloud import WordCloud
import base64
from io import BytesIO
from dash.dash_table import DataTable
import nltk
from matplotlib.colors import LinearSegmentedColormap
from io import StringIO
import csv
from nltk.corpus import stopwords

nltk.download('stopwords', quiet=True)

stopwords = set(stopwords.words('english'))

# Layout
word_cloud_page_layout = html.Div([
    html.Div([
        html.H1("EPICOL18", style={'color': '#929585', 'padding': '20px', 'backgroundColor': '#f6f6f6',
                                   'font-family': 'Arial, sans-serif'}),
        # Dropdown for selecting books
        html.Div([
            html.Label("Select Books:", style={'color': '#555'}),
            dcc.Dropdown(
                id="book-dropdown",
                options=[{"label": "All Books", "value": "all"},
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
                multi=True,  # Allow selecting multiple books
                value=["all"],
                placeholder="Select Books",
                searchable=True,
                style={'width': '100%','outline': 'none', 'boxShadow': 'none'}
            ),
        ], style={'padding': '10px', 'backgroundColor': '#f6f6f6', 'font-family': 'Arial, sans-serif'}),

        html.Div([
            html.Label("Select POS Tag:", style={'color': '#555'}),
            dcc.Dropdown(
                id="pos-tag-dropdown",
                options=[{"label": "No POS", "value": "no_tag"},
                    {"label": "Noun", "value": "NOUN"}, #NOUNS
                    {"label": "Adjective", "value": "ADJ"},
                    {"label": "Adverb", "value": "ADV"},
                    {"label": "Auxiliary", "value": "AUX"},
                    {"label": "Interjection", "value": "INTJ"},
                    {"label": "Particle", "value": "PART"},
                    {"label": "Pronoun", "value": "PRON"},
                    {"label": "Proper Noun", "value": "PROPN"},
                    {"label": "Verb", "value": "VERB"},
                ],
                multi=True,
                value=["no_tag"],  # Default to None for no filter
                style={'width': '100%'},
                searchable=True
            ),
        ], style={'padding': '10px', 'backgroundColor': '#f6f6f6', 'font-family': 'Arial, sans-serif'}),

        # Navigation to other pages
        html.Div([dcc.Link('Back', href='/',
                           style={'margin': '20px', 'textDecoration': 'none', 'color': '#555',
                                  })],
                 style={'textAlign': 'left', 'padding': '10px', 'backgroundColor': '#f6f6f6',
                        'font-family': 'Arial, sans-serif', "color": "#484848",
                        "position": "absolute", "bottom": "0",
                        'borderRadius': '8px', 'boxShadow': '2px 0 10px rgba(0, 0, 0, 0.1)'}),

    ], style={'width': '400px', 'position': 'fixed', 'top': '0', 'left': '0', 'height': '100vh',
              'backgroundColor': '#929585', 'boxShadow': '2px 0 5px rgba(0,0,0,0.1)',
              }),

    # Right side to display the Word Cloud
    html.Div([
        html.H1("Top Words and Parts-of-Speech",
                style={'fontSize': '32px', 'textAlign': 'center', 'padding': '20px', "color":"#929585",
                       'font-family': 'Arial, sans-serif'}),

        # Loading circle always at the top
        dcc.Loading(id="loading-1", type="circle", children=[

                # DataTable to display the word frequencies
                html.Div([
                    DataTable(
                        id='word-frequencies-table',
                        columns=[
                            {"name": "Word", "id": "word"},
                            {"name": "Frequency", "id": "frequency"},
                            {"name": "Relative Frequency (per 10,000 words)", "id": "relative frequency"}
                        ],
                        page_size=10,  # Pagination: Show 10 rows per page
                        style_table={'height': '400px', 'overflowY': 'auto'},
                        sort_action="native",  # Sorting enabled
                        sort_by=[{"column_id": "Frequency", "direction": "desc"}],
                        style_cell={'maxWidth': '100px', 'textAlign': 'left', 'padding': '10px'},
                        style_data_conditional=[{
                            'if': {'state': 'selected'},  # Target selected cells
                            'backgroundColor': '#dddddd',
                            'color': 'black',  # Text color
                            'border': '2px #343d46'}],

                    )
                ], style={'padding': '20px',"fontSize": "12px"}),
                html.Button("Download", id="download-table-button", n_clicks=0,
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
                dcc.Download(id="download-table"),

                html.Div([html.Div(id="word-cloud", style={'padding': '20px'})]),

                html.Button("Download", id="download-button", n_clicks=0,
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
                dcc.Download(id="download-wordcloud"),

        ], style={'position': 'absolute', 'top': '20px', 'left': '50%', 'transform': 'translateX(-50%)',
                  'z-index': '100', 'padding': '20px'}),

    ], style={'margin-left': '400px', 'padding': '20px', "overflow-y": "auto"})
])


# Function to get word frequencies from selected books
def get_word_frequencies(selected_books, pos_tag_filter):
    conn = sqlite3.connect('./data/books.db')
    c = conn.cursor()

    # Build the query for selected books
    if "all" in selected_books:
        if pos_tag_filter == ["no_tag"]:
            query = "SELECT tokenized_content, title FROM books_fts"
        else:
            query = "SELECT pos_tagged_content, title FROM books_fts"
        c.execute(query)
        results = c.fetchall()
    else:
        if pos_tag_filter == ["no_tag"]:
            query = '''SELECT tokenized_content, title FROM books_fts WHERE title IN ({})'''.format(
                ', '.join(['?'] * len(selected_books)))
        else:
            query = '''SELECT pos_tagged_content, title FROM books_fts WHERE title IN ({})'''.format(
                ', '.join(['?'] * len(selected_books)))
        c.execute(query, selected_books)
        results = c.fetchall()

    conn.close()

    book_contents = {}
    for result in results:
        if pos_tag_filter == ["no_tag"]:
            content, title = result
            word_list = [word.lower() for word in content.split(",") if word.isalpha()]
            word_counts = Counter(word_list)
            book_contents[title] = word_counts
        else:
            pos_tagged_content, title = result
            tagged_tokens = pos_tag_tokens(pos_tagged_content)
            filtered_tokens = [word.lower() for word, tag in tagged_tokens if tag in pos_tag_filter]
            word_counts = Counter(filtered_tokens)
            book_contents[title] = word_counts

    return book_contents


# Function to parse POS-tagged content and extract word-tag pairs
def pos_tag_tokens(pos_tagged_content):
    tokens = pos_tagged_content.split()
    tagged_tokens = []

    for token in tokens:
        if "_" in token:
            word, tag = token.rsplit('_', 1)
            tagged_tokens.append((word, tag))

    return tagged_tokens


def generate_wordcloud(book_contents, pos_tag_filter=None):
    all_word_counts = {}
    for title, word_counts in book_contents.items():
        for word, frequency in word_counts.items():
            if word not in stopwords:
                all_word_counts[word] = all_word_counts.get(word, 0) + frequency

    custom_colormap = ["#929585", "#999999", "#777777", "#555555", "#333333"]
    custom_cmap = LinearSegmentedColormap.from_list("custom_gray", custom_colormap)
    wordcloud = WordCloud(width=700,
                          height=400,
                          background_color='white',
                          min_font_size=12,
                          colormap=custom_cmap,
                          relative_scaling=0.5,
                          prefer_horizontal=0.7,
                          max_words=100,
                          stopwords=stopwords
                          ).generate_from_frequencies(all_word_counts)

    img = BytesIO()
    wordcloud.to_image().save(img, format='PNG')
    img.seek(0)
    img_b64 = base64.b64encode(img.read()).decode('utf-8')

    return img_b64


# Main callback to update word cloud and table
def word_cloud_callback(app):
    @app.callback(
        [Output('word-cloud', 'children'),
         Output("download-wordcloud", "data"),
         Output("download-table", "data"),
         Output('word-frequencies-table', 'data')],
        [Input('book-dropdown', 'value'),
         Input('pos-tag-dropdown', 'value'),
         Input('download-button', 'n_clicks'),
         Input('download-table-button', 'n_clicks')]
    )
    def update_word_cloud(selected_books, pos_tag_filter, n_clicks_wordcloud, n_clicks_table):
        if not selected_books:
            selected_books = ["all"]

        # Fetch word frequencies from the selected books
        word_counts = get_word_frequencies(selected_books, pos_tag_filter)

        # If no words are found, return a message
        if not word_counts or all(len(counts) == 0 for counts in word_counts.values()):
            return html.Div("No words to display for the selected filters."), None, None, []

        # Generate the word cloud and get word frequencies using words_
        wordcloud_img_b64 = generate_wordcloud(word_counts, pos_tag_filter)

        # Create an image to display
        wordcloud_img_tag = html.Img(src=f"data:image/png;base64,{wordcloud_img_b64}",
                                     style={'width': '90%', 'height': 'auto'})

        # Create a dictionary to hold aggregated word frequencies across all books
        aggregated_word_counts = {}
        total_word_count = 0

        # Flatten the word counts dictionary into a list of dictionaries for each word's frequency
        for book, counts in word_counts.items():
            for word, frequency in counts.items():
                word = word.lower()  # Normalize word to lowercase
                if word not in stopwords:
                    if word not in aggregated_word_counts:
                        aggregated_word_counts[word] = 0  # Initialize the word frequency if not already present
                    aggregated_word_counts[word] += frequency  # Aggregate the frequency for the word
                    total_word_count += frequency  # Accumulate the total word count

        # If no total word count exists, return an empty table (avoid division by zero)
        if total_word_count == 0:
            return wordcloud_img_tag, None, None, []

        # Convert the aggregated dictionary into a list for the table
        all_word_counts = [{"word": word,
                            "frequency": frequency,
                            "relative frequency": round((frequency / total_word_count) * 10000, 2)}
                           for word, frequency in aggregated_word_counts.items()]

        # Sort the words by frequency in descending order
        all_word_counts = sorted(all_word_counts, key=lambda x: x['frequency'], reverse=True)

        # Limit the output to the top 150 words
        all_word_counts = all_word_counts[:100]

        # Provide the content for the download if requested
        if n_clicks_wordcloud > 0:
            return wordcloud_img_tag, dict(content=base64.b64encode(wordcloud_img_b64.encode()).decode('utf-8'),
                                           filename="epicol18_results.png"), None, all_word_counts

        # Handle table download if the download button is clicked
        if n_clicks_table > 0:
            # Create a CSV file in memory
            csv_output = StringIO()
            writer = csv.DictWriter(csv_output, fieldnames=["word", "frequency", "relative frequency"])
            writer.writeheader()
            writer.writerows(all_word_counts)
            csv_output.seek(0)

            return wordcloud_img_tag, None, dict(content=csv_output.getvalue(),
                                                 filename="epicol18_results.csv"), all_word_counts

        return wordcloud_img_tag, None, None, all_word_counts