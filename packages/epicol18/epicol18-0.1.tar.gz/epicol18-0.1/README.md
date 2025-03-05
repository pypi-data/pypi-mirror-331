# **EPICOL18 \- Corpus Query Interface**

### **📖 About EPICOL18 WebApp** 

The *Corpus of Long Eighteenth-Century Epistolary Novels* (EPICOL18) lends itself well to genre-specific research questions, text-specific research questions, stylometry and author stylistic analyses. This web-based corpus interface allows for an easy and user-friendly exploration of EPICOL18. It may also lend itself well for historical corpus linguistic questions, but it should be considered that the spelling was modernised and the text was cleaned from any meta-information (e.g. headers, front/back matter). 

### 📜 **Corpus Structure** 

The texts for this corpus were collected from online databases and archives such as *Project Gutenberg*, *The Oxford Text Archive*, *The Online Books Page* at the University of Pennsylvania, *Early English Books Online* (EEBO), and *Eighteenth Century Collections Online* (ECCO). The texts themselves are not necessarily the originally published edition, but rather those that are available on the afore-mentioned platforms. What is counted here, is the original publication date of the text.

Selection criteria:

* fictional text  
* vast majority/all of the text is in letter correspondences  
* not a translation  
* written by a British author  
* originally published between 1680 and 1820  
* acceptable transcription quality and completion
* electronically accessible  
* copyright free

The time frame for this corpus is set from the years leading up to the Glorious Revolution in 1688 and the years following the end of the Napoleonic Wars in 1815 and the death of George III in 1820\. This time-frame might however be under revision, depending on how the corpus will continue to evolve. Literary resources were           consulted to find and also verify whether a novel qualified as "epistolary" (Beebee 1999, Bray 2003 and others). The corpus was originally designed for my Master's Thesis Project, which analysed lexico-grammatical patterns in the meta-discourse on proper and improper behaviour through collocations. For that reason, the corpus size had to be manageable enough for qualitative contextualization, but also big enough for statistically sound results. Now, the corpus may be expanded further to allow for a more comprehensive overview of the texts.

The text was edited to match the modernised spelling in VARD2, and front/back matter as well as chapter headers were removed. For example, remov’d was normalized to removed, ca to can (split from tokenization can’t) and Further manual edits were done to eliminate annotations that might impact machine-readability. Any research concerning old spelling variants or the novel structure is not possible. 

The following table (Table 1) describes the structure of EPICOL. Tokens are individual words.  Types represent unique words and lemmas are the number of unique word root forms. Of the 28 texts,spanning over 4 million words. This corpus was also tagged for parts-of-speech and tokenized with the spacy tagger and tokenizer, which uses the Universal POS-Tag Set. The tagged results were checked and a domain-specific vocabulary with POS-tag mapping was created for frequent mistakes, in addition to manual correction after inspection. This tagger tags with roughly 97 percent reported accuracy for modern texts, and did quite well here as well. Punctuation is excluded.

| Year | Title                                                                      | Author                  | Tokens  | RF(%) | Types | Lemmas |  
|------|----------------------------------------------------------------------------|-------------------------|---------|-------|-------|--------|  
| 1684 | Love-Letters Between a Nobleman and His Sister                             | Aphra Behn              | 177074  | 4.33  | 7536  | 6621   |  
| 1702 | The Lover's Secretary; or, the Adventures of Lindamira, a Lady of Quality  | Thomas Brown (Editor)   | 51630   | 1.26  | 4086  | 3788   |  
| 1778 | Evelina, or the History of a Young Lady's Entrance into the World          | Frances Burney          | 153260  | 3.75  | 7378  | 6785   |  
| 1778 | The Sylph                                                                  | Georgiana Cavendish     | 80160   | 1.96  | 6529  | 5936   |  
| 1725 | Familiar Letters Betwixt a Gentleman and a Lady                            | Mary Davys              | 12591   | 0.31  | 2377  | 2230   |  
| 1724 | The Reform'd Coquet                                                        | Mary Davys              | 39327   | 0.96  | 3494  | 3223   |  
| 1806 | Leonora                                                                    | Maria Edgeworth         | 66189   | 1.62  | 6063  | 5497   |  
| 1741 | An Apology for the Life of Mrs. Shamela Andrews                            | Henry Fielding          | 14382   | 0.35  | 2254  | 2128   |  
| 1771 | The History of Lady Barton                                                 | Elizabeth Griffith      | 107888  | 2.64  | 7526  | 6845   |  
| 1776 | The Story of Lady Juliana Harley                                           | Elizabeth Griffith      | 63608   | 1.56  | 6180  | 5673   |  
| 1769 | The Delicate Distress                                                      | Elizabeth Griffith      | 89404   | 2.19  | 6448  | 5874   |  
| 1757 | A Series of Genuine Letters between Henry and Frances                      | Richard Griffith        | 137250  | 3.36  | 8641  | 7800   |  
| 1768 | Barford Abbey                                                              | Susannah Gunning        | 52109   | 1.27  | 4912  | 4513   |  
| 1741 | The Anti-Pamela; or, Feign'd Innocence Detected                            | Eliza Haywood           | 72608   | 1.78  | 4745  | 4361   |  
| 1725 | The Fatal Secret: or, Constancy in Distress                                | Eliza Haywood           | 16766   | 0.41  | 2593  | 2448   |  
| 1723 | Idalia, or, The Unfortunate Mistress                                       | Eliza Haywood           | 57522   | 1.41  | 4832  | 4450   |  
| 1719 | Love in Excess; or, The Fatal Enquiry                                      | Aphra Behn              | 88198   | 2.16  | 5735  | 5219   |  
| 1684 | The History of Miss Betsy Thoughtless                                      | Eliza Haywood           | 228428  | 5.59  | 8449  | 7587   |  
| 1780 | Alwyn: or the Gentleman Comedian                                           | Thomas Holcroft         | 55025   | 1.35  | 6496  | 5915   |  
| 1792 | Anna St. Ives                                                              | Thomas Holcroft         | 188355  | 4.61  | 11068 | 9886   |  
| 1791 | Hermione, or the orphan sisters                                            | Charlotte Lennox        | 166935  | 4.08  | 7934  | 7217   |  
| 1696 | Letters writen \[sic\] by Mrs. Manley                                      | Delarivier Manley       | 10348   | 0.25  | 2088  | 1983   |  
| 1747 | Clarissa, or, The History of a Young Lady                                  | Samuel Richardson       | 942390  | 23.04 | 17814 | 15598  |  
| 1740 | Pamela; or, Virtue Rewarded                                                | Samuel Richardson       | 222172  | 5.43  | 7623  | 6805   |  
| 1753 | The History of Sir Charles Grandison                                       | Samuel Richardson       | 748900  | 18.31 | 14357 | 12656  |  
| 1818 | Frankenstein or, the Modern Prometheus                                     | Mary Shelley            | 75131   | 1.84  | 6943  | 6320   |  
| 1771 | The Expedition of Humphry Clinker                                          | Tobias Smollett         | 149999  | 3.67  | 12130 | 10743  |  
| 1693 | Olinda's Adventures: or the Amours of a Young Lady                         | Catharine Trotter       | 22110   | 0.54  | 2240  | 2103   |  
|      | Total                                                                      |                         | 4089759 | \-    | 33679 | 29222  |
Table 1. Works included in EPICOL18 with their token, type and lemma counts.

### **💡 Functions and Features (with Examples/Screenshots)**

**1. Top Words and Parts-of-Speech** 

Based on your text and POS-Tag selection, a table and word cloud with the top 100 key terms of the selected books and selected part-of-speech tag filter will be generated. Key words are the most frequent words excluding stopwords. The table displays the word, its raw frequency and its relative frequency in the selected books. The wordcloud visualizes these results with bigger words being more frequent than smaller words. You can either analyse word frequencies only, or filter them by their part-of-speech additionally. You can then choose to download the resulting Table as a CSV-file and the image as a PNG-file. As default option, the key terms calculated from all texts are displayed. 

**2. Key-Word-In-Context (KWIC)**

Enter a search term using regular expressions and search its appearanches across the entire corpus. By default, the text search is case-insensitive. The results are displayed in a column format with the left and right context of the search term next to the search term column. Further columns include the publication date and the book it appeared in. At the top, a total count of hits is displayed.

**3. Diachronic Search**

Enter a search term using regular expressions and visualize its frequencies across the entire corpus in a diachronic line chart. By default, the text search is case-sensitive. The years on the x-axis correspond to the publication dates of the books, the data points along the y-axis are accumulated frequences of the books in which the search term appears. 

**4. Text Search** 

Search for an individual word or phrase using regular expressions in a selection of texts. By default, the text search is case-sensitive. A table and bar chart are generated displaying the tokens that were matched with their raw frequencies in parenthesis, their sum, and normalized frequency with additional information on the size of the book, title, author, and publication year, where it was identified. The table is also downloadable as CSV-file. At the top, a total match count is displayed.

**5. N-Grams** 

Based on your text selection and a search query formulated as regular expression, create word n-grams spanning two to five words and display their frequencies in a table with their raw and normalized frequencies. By default, the text search is case-insensitive, as all ngrams are lowercased.

### 🔍 **Technical Details and Requirements**

The app uses Dash for the frontend, Flask as the web server, and SQL for storing and querying the corpus database. It is written in Python and uses an additional style sheet in CSS to add to the HTML structures. For the requirements, please see the corresponding file.

### **🛠️ Using EPICOL18**

**Step 1** 

Install the package through your terminal:
```
pip install epicol18
```

**Step 2** 

Install the requests:
```
pip install requests
```

Run the web-app:
```
python my_script.py
```

After a few seconds, this link should appear:
```
http://127.0.0.1:8050/
```
   
Click the link, which will open a browser window. 

**Step 3**

Now you are on the main page of EPICOL18. Enjoy perusing!

### **License**

You may use my app to do research, but please cite my work appropriately.

### 📚 **Sources** 

Please see the sources.txt file for an entire list of the sources for the corpus compilation on my GitHub.

### **Outlook and Contact**

The text selection might be extended and additional features added (any suggestions are highly welcome). 
If you have any questions or encounter any problems, feel free to reach out to me!