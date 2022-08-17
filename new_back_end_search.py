import nltk
# from google.cloud import storage
import re
import pickle
from nltk.corpus import stopwords
from pathlib import Path

nltk.download('stopwords')
english_stopwords = frozenset(stopwords.words('english'))
corpus_stopwords = ["category", "references", "also", "external", "links",
                    "may", "first", "see", "history", "people", "one", "two",
                    "part", "thumb", "including", "second", "following",
                    "many", "however", "would", "became"]

all_stopwords = english_stopwords.union(corpus_stopwords)
RE_WORD = re.compile(r"""[\#\@\w](['\-]?\w){,24}""", re.UNICODE)


def tokenize(text):
    return [token.group() for token in RE_WORD.finditer(text.lower())]

# def load():
#     bucket_name = 'newbodysearch'
#     client = storage.Client()
#     for blob in client.list_blobs(bucket_name):
#         if not blob.name.endswith('page_view.pickle'):
#             continue
#         with blob.open("rb") as file:
#             PageViewDT = pickle.load(file)
#     for blob in client.list_blobs(bucket_name):
#         if not blob.name.endswith('page_rank.pickle'):
#             continue
#         with blob.open("rb") as file:
#             PageRankD = pickle.load(file)
#     for blob in client.list_blobs(bucket_name):
#         if not blob.name.endswith('id_to_title.pickle'):
#             continue
#         with blob.open("rb") as file:
#             ID_Title_dict = pickle.load(file)
#     for blob in client.list_blobs(bucket_name):
#         if not blob.name.endswith('postings_gcp/index.pickle'):
#             continue
#     for blob in client.list_blobs(bucket_name):
#         if not blob.name.endswith('DL_dict_DL_dict.pickle'):
#             continue
#     dict_DL= read_index('DL_dict_DL_dict')
#     dict_title= read_index('id_to_title')
#     page_view_data_frame= read_index('page_view')
#     page_rank_dict= read_index('page_rank')
#     idx_body= read_index('index')
#     return dict_title, page_view_data_frame, page_rank_dict, idx_body, dict_DL


def read_index(base_dir, name):
    with open(Path(base_dir) / f'{name}.pkl', 'rb') as f:
        return pickle.load(f)


def get_posting_gen(index, word):
    words, pls = zip(index.read_posting_list(word))
    return (words, pls)

def cossim(query, index, dict_Dl):
    result_dict = {}
    query_vector = {}
    for idDoc in dict_Dl.keys():
        result_dict[idDoc]=float(0)
    for word in query:
        query_vector[word] = query.count(word)
    for term in query:
        try:
            words, pls = get_posting_gen(index, term)
            pls_post = pls[0]
        except:
            pls_post=[]
        for id, tf in pls_post:
            result_dict[id] += query_vector[term] * tf
    for id in dict_Dl.keys():
        result_dict[id] = result_dict[id] * (1/len(query) * (1/dict_Dl[id]))
    return result_dict


# def get_top_n(sim_dict, N=3):
#     return sorted([(doc_id, round(score, 5)) for doc_id, score in sim_dict.items()], key=lambda x: x[1], reverse=True)[:N]