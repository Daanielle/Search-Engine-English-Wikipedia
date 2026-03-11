from flask import Flask, request, jsonify
import pandas as pd
import pickle

from inverted_index_gcp import *
import new_back_end_search

class MyFlaskApp(Flask):
    def run(self, host=None, port=None, debug=None, **options):
        # Try to load the data, but skip if missing
        try:
            self.idx_body = InvertedIndex.read_index("/home/aspirdanielle/newbodysearch/postings_gcp", 'index')
        except FileNotFoundError:
            print("Index file not found, using empty index")
            self.idx_body = {}

        try:
            self.dict_title = InvertedIndex.read_index("/home/aspirdanielle", 'id_to_title')
        except FileNotFoundError:
            print("Title dictionary not found, using empty dict")
            self.dict_title = {}

        try:
            self.dict_DL = InvertedIndex.read_index("/home/aspirdanielle", 'DL_dict_DL_dict')
        except FileNotFoundError:
            print("DL dictionary not found, using empty dict")
            self.dict_DL = {}

        try:
            self.page_rank_dict = InvertedIndex.read_index("/home/aspirdanielle", 'page_rank')
        except FileNotFoundError:
            print("PageRank dict not found, using empty dict")
            self.page_rank_dict = {}

        try:
            self.page_view_data_frame = InvertedIndex.read_index("/home/aspirdanielle", 'page_view')
        except FileNotFoundError:
            print("Page view data not found, using empty dict")
            self.page_view_data_frame = {}

        # Minimal fix: call parent run() so Flask actually starts
        super(MyFlaskApp, self).run(host=host, port=port, debug=debug, **options)

app = MyFlaskApp(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

BASE_PATH = '/content/MyDrive/hw3bucketmor'

# ---------------- ROUTES ----------------

@app.route("/search")
def search():
    ''' Returns up to a 100 of your best search results for the query. This is
        the place to put forward your best search engine, and you are free to
        implement the retrieval however you'd like within the bound of the
        project requirements (efficiency, quality, etc.). That means it is up to
        you to decide on whether to use stemming, remove stopwords, use
        PageRank, query expansion, etc.

        To issue a query navigate to a URL like:
         http://YOUR_SERVER_DOMAIN/search?query=hello+world
        where YOUR_SERVER_DOMAIN is something like XXXX-XX-XX-XX-XX.ngrok.io
        if you're using ngrok on Colab or your external IP on GCP.
    Returns:
    --------
        list of up to 100 search results, ordered from best to worst where each
        element is a tuple (wiki_id, title).
    '''
    res = []
    query = request.args.get('query', '')
    if len(query) == 0:
        return jsonify(res)
    # BEGIN SOLUTION
    if not app.idx_body or not app.dict_DL:
        return jsonify(res)

    query_tokens = new_back_end_search.tokenize(query)
    result_can = new_back_end_search.cossim(query_tokens, app.idx_body, app.dict_DL)
    sorted_result = sorted(result_can.items(), key=lambda item: item[1], reverse=True)[:100]
    for k, v in sorted_result:
        if v != 0.0:
            res.append((k, app.dict_title.get(k, "UNKNOWN")))
    # END SOLUTION
    return jsonify(res)


@app.route("/search_body")
def search_body():
    ''' Returns up to a 100 search results for the query using TFIDF AND COSINE
        SIMILARITY OF THE BODY OF ARTICLES ONLY. DO NOT use stemming. DO USE the
        staff-provided tokenizer from Assignment 3 (GCP part) to do the
        tokenization and remove stopwords.
    '''
    res = []
    query = request.args.get('query', '')
    if len(query) == 0:
        return jsonify(res)
    # BEGIN SOLUTION
    if not app.idx_body or not app.dict_DL:
        return jsonify(res)

    query_tokens = new_back_end_search.tokenize(query)
    result_can = new_back_end_search.cossim(query_tokens, app.idx_body, app.dict_DL)
    sorted_result = sorted(result_can.items(), key=lambda item: item[1], reverse=True)[:100]
    for k, v in sorted_result:
        if v != 0.0:
            res.append((k, app.dict_title.get(k, "UNKNOWN")))
    # END SOLUTION
    return jsonify(res)


@app.route("/search_title")
def search_title():
    ''' Returns ALL (not just top 100) search results that contain A QUERY WORD
        IN THE TITLE of articles, ordered in descending order of the NUMBER OF
        QUERY WORDS that appear in the title. 
    '''
    res = []
    query = request.args.get('query', '')
    if len(query) == 0 or not app.dict_title:
        return jsonify(res)
    query_words = query.lower().split()
    for wiki_id, title in app.dict_title.items():
        title_words = title.lower().split()
        count = sum(1 for w in query_words if w in title_words)
        if count > 0:
            res.append((wiki_id, title, count))
    # Sort by number of matching words
    res.sort(key=lambda x: x[2], reverse=True)
    return jsonify([(x[0], x[1]) for x in res])


@app.route("/search_anchor")
def search_anchor():
    ''' Returns ALL (not just top 100) search results that contain A QUERY WORD
        IN THE ANCHOR TEXT of articles, ordered in descending order of the
        NUMBER OF QUERY WORDS that appear in anchor text linking to the page.
    '''
    return jsonify([])  # placeholder, no anchor index loaded


@app.route("/get_pagerank", methods=['POST'])
def get_pagerank():
    ''' Returns PageRank values for a list of provided wiki article IDs. '''
    wiki_ids = request.get_json() or []
    res = [app.page_rank_dict.get(i, 0.0) for i in wiki_ids]
    return jsonify(res)


@app.route("/get_pageview", methods=['POST'])
def get_pageview():
    ''' Returns the number of page views that each of the provided wiki articles had in August 2021. '''
    wiki_ids = request.get_json() or []
    res = [app.page_view_data_frame.get(i, 0) for i in wiki_ids]
    return jsonify(res)


# ---------------- RUN FLASK ----------------

if __name__ == "__main__":
    print("Starting Flask server on port 8080...")
    app.run(host="0.0.0.0", port=8080, debug=False)