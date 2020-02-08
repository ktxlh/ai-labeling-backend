"""
純bert得到每個框框的nlp feature，
對所有框框clustering，再根據選的框框，選最接近該cluster的框框(s?)？
或者純bert有sentence embedding之後，回傳「接下來每個框框，和使用者剛剛框的東西，屬於同個cluster的機率」

之後想想
1. 如何引入absolute/relative position當feature
2. 使用者feedback (不要的、新增的框框)回來的方式

## Dependencies
pip install pytorch
pip install transformers
第一次跑，huggingface transformers會把bert下載到local，會花比較久時間。之後就不會了
"""
import json

import numpy as np
from sklearn.cluster import SpectralClustering
from transformers import DistilBertModel, DistilBertTokenizer

import torch
from app import Dt

sentence = "Hello, my dog is cute"
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
model = DistilBertModel.from_pretrained('distilbert-base-uncased')

def embed_sentence(sentence):
    """
    IN: raw sentence
    OUT: a numpy array of embedding
    """

    input_ids = torch.tensor(tokenizer.encode(sentence, add_special_tokens=True)).unsqueeze(0)  # Batch size 1
    outputs = model(input_ids)

    last_hidden_states = outputs[0]  # The last hidden-state is the first element of the output tuple
    embedding = last_hidden_states[0,0]  # last_hidden_states.shape == (1, 8, 768)
    return embedding.detach().numpy()
#print(embed_sentence(sentence))

X = np.array([[1, 1], [2, 1], [1, 0],[4, 7], [3, 5], [3, 6]])
def cluster(X):
    clustering = SpectralClustering(n_clusters=7, random_state=0).fit(X)
    return clustering

def cluster_input():
    """
    Read training files and train a clustering model

    OUT model: The clustering
    OUT samples: (num of labels-len) list of (num of samples of the label-len) list of str
    """
    train = []
    sents, embeddings = [], [] # DistilBERT "dim": 768
    for root, dirs, files in os.walk(Dt.dirs["input"], topdown=False):
        fnames = list([name for name in files if name.endswith(".json")])
        fnames.sort()
        train = fnames[:90] # TODO For training, for now
        for name in train:
            with open(os.path.join(Dt.dirs["input"], name)) as json_in:
                json_obj = json.loads(json_in.read())
                for line in json_obj['recognitionResults']['lines']:
                    embedded = embed_sentence(line['text'])
                    embeddings.append(embedded)
                    sents.append(line['text'])
    
    X = np.array(embeddings)
    clustering = cluster(X)
    samples = [[] for i in range(len(set(clustering.labels_)))]
    for isent, sent in enumerate(sents):
        samples[clustering.labels_[isent]].append(sent)

    return clustering, samples

def predict(clustering):
    """
    Predict which cluster with the model

    OUT result
    """
    test = []
    sents, embeddings = [], []
    for root, dirs, files in os.walk(Dt.dirs["input"], topdown=False):
        fnames = list([name for name in files if name.endswith(".json")])
        fnames.sort()
        test = fnames[90:]  # TODO For training, for now
        for name in test:
            with open(os.path.join(Dt.dirs["input"], name)) as json_in:
                json_obj = json.loads(json_in.read())
                for line in json_obj['recognitionResults']['lines']:
                    embedded = embed_sentence(line['text'])
                    embeddings.append(embedded)
                    sents.append(line['text'])
    
    X = np.array(embeddings)
    clustering = cluster(X)
    samples = [[] for i in range(len(set(clustering.labels_)))]
    for isent, sent in enumerate(sents):
        samples[clustering.labels_[isent]].append(sent)

    name = test[0]
    test_sents, test_embeddings = [], []
    with open(os.path.join(Dt.dirs["input"], name)) as json_in:
        json_obj = json.loads(json_in.read())
        for line in json_obj['recognitionResults']['lines']:
            embedded = embed_sentence(line['text'])
            test_embeddings.append(embedded)
            test_sents.append(line['text'])
    X_prim = np.array(test_embeddings)
    labels = clustering.fit_predict(X_prim)

    return clustering, samples

