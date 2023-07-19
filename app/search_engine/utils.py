from tqdm import tqdm
from docarray import Document, DocumentArray
import fasttext


def load_model():
    return fasttext.load_model("model/model.bin")


def connect_search_engine():
    return DocumentArray(
        storage='sqlite', config={'connection': 'model/op_tags.db', 'table_name': 'op_tags'}
    )
