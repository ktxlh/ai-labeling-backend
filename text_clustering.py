"""
We cluster bounding boxes according to their semantic meaning 
and postitions. Then, we predict the box to label according
to the cluster label chosen.

* Granularity: Each bounding box
* Features:
    * Semantic: DistilBERT embedding
    * Position: Relative position (normalized to range [-1, 1])
* Algorithms:
    * DBSCAN / O(n^2)
    * Spectral clustering / O(n^3)

*** *** 之後可做: 使用者feedback (不要的、新增的框框)回來的方式 *** *** 
—— 讓使用者標過的東西的weight變大，再跑clustering、再predict，感覺會有用，但也會很慢
或者return「接下來每個框框，和使用者剛剛框的東西，屬於同個cluster的機率」，這樣還可以根據confidence visualize (e.g.越confident的顏色越偏紅)

## Dependencies
pip install pytorch transformers

NOTE 第一次跑的時候，huggingface transformers會下載bert，要花比較久時間。之後就不會了
"""
import json
import os

import numpy as np
from sklearn.cluster import DBSCAN #SpectralClustering
from transformers import DistilBertModel, DistilBertTokenizer

import torch

class Dt: 
    dirs = {
        "input" : "./LabelingTrainingData/Input",
        "recommend" : "./LabelingTrainingData/Recommend",
        "final" : "./LabelingTrainingData/Final"
    }
    fnames = []

sentence = "Hello, my dog is cute"
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
model = DistilBertModel.from_pretrained('distilbert-base-uncased')

def cluster_text():
    """
    Read training files and train a clustering model

    OUT model: The clustering
    OUT samples: (num of labels-len) list of (num of samples of the label-len) list of str

    Label each bounding box with its cluster index
    """

    def embed_sentence(sentence):
        """
        IN: raw sentence
        OUT: a numpy array of embedding
        """

        input_ids = torch.tensor(tokenizer.encode(sentence, add_special_tokens=True)).unsqueeze(0)  # Batch size 1
        outputs = model(input_ids)

        last_hidden_states = outputs[0]  # The last hidden-state is the first element of the output tuple
        embedding = last_hidden_states[0,0]  # last_hidden_states.shape == (1, n, 768); n == len(tokens)
        return embedding.detach().numpy()
        
    def normalize_location(height,width,boundingBox):
        for i in range(len(boundingBox)):
            if i%2==0: #y
                boundingBox[i] = (boundingBox[i]-height/2)/height * 2
            else: #x
                boundingBox[i] = (boundingBox[i]-width/2)/width * 2
        return np.array(boundingBox)

    def cluster(X):
        #clustering = SpectralClustering(n_clusters=7, random_state=0).fit(X)   # O(n^3): too slow
        clustering = DBSCAN(eps=100, min_samples=5).fit(X)                      # O(n^2): better
        return clustering

    train = []
    sents, embeddings = [], [] # DistilBERT "dim": 768
    predictions = dict() # dict of filename of str(boundingBox) of its predicted label number
    mapping = [] # list of (filename, tuple(boundingBox))
    for root, dirs, files in os.walk(Dt.dirs["input"], topdown=False):
        fnames = list([name for name in files if name.endswith(".json")])
        fnames.sort()
        train = fnames
        for name in train:
            predictions[name] = []
            with open(os.path.join(Dt.dirs["input"], name)) as json_in:
                json_obj = json.loads(json_in.read())
                height = json_obj['recognitionResults'][0]['height']
                width = json_obj['recognitionResults'][0]['width']
                sents = [word['text'] for line in json_obj['recognitionResults'][0]['lines'] for word in line["words"]]
                
                for line in json_obj['recognitionResults'][0]['lines']:
                    for word in line["words"]:
                        embedded = embed_sentence(word['text'])
                        box = normalize_location(height,width,word["boundingBox"].copy())  # Normalize to +-1
                        embeddings.append([*embedded, *box])

                        mapping.append((name, len(predictions[name])))
                        predictions[name].append({
                            "boundingBox" : word["boundingBox"],
                            'text' : word['text']
                        })
    
    X = np.array(embeddings)
    clustering = cluster(X)

    for i, ith_label in enumerate(clustering.labels_):
        name, idx = mapping[i]
        predictions[name][idx]["label"] = ith_label.item()

    for fname, elements in predictions.items():
         with open(os.path.join(Dt.dirs['recommend'], fname),'w') as json_out:
            obj = {
                "filename" : fname,
                "elements" : elements
            }
            json.dump(obj, json_out)

    return "Text clustering finished."
