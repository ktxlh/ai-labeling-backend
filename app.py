"""
The following directrories are involved:
1. Input:       The raw input (the one given). It must be created explicitly in advance.
2. Recommend:   The predicted labels
3. Final:       The final labeling results for scoring
"""
import json
import os

import flask
from flask import request
from flask_cors import CORS, cross_origin

from recommender import select_box
from text_clustering import cluster_text

app = flask.Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config["DEBUG"] = True

class Dt: 
    key_word = "date"
    dirs = {
        "input" : "./LabelingTrainingData/Input",
        "recommend" : "./LabelingTrainingData/Recommend",
        "final" : "./LabelingTrainingData/Final",
        "metadata" : "./LabelingTrainingData/",
    }

    fnames = []
    other_fnames = []

#############################################
# Utils / methods
#############################################
def check_dirs():
    dirs = Dt.dirs
    if not os.path.isdir(dirs["input"]):
        return "ERROR: Bad input dir path: " + dirs["input"]
        
    for dkey in dirs.keys():
        if not os.path.isdir(dirs[dkey]):
            os.mkdir(dirs[dkey])
    return "Input directory's path checked"

def rule_based():
    """
    Returns the number of files are successfully 
    processed / the number of files detected
    """
    succeeded_fnames, other_fnames = [], []
    for root, dirs, files in os.walk(Dt.dirs["input"], topdown=False):
        fnames = list([name for name in files if name.endswith(".json")])
        
        detected = len(fnames)
        for name in fnames:
            with open(os.path.join(Dt.dirs["input"], name)) as json_in:
                json_obj = json.loads(json_in.read())
                rtn = select_box(Dt.key_word, json_obj)
                
                if rtn ==0 : 
                    other_fnames.append(name)
                    json_dict = {
                        'filename' : name,
                        'elements' : []
                    }
                else:
                    succeeded_fnames.append(name)
                    json_dict = {
                        'filename' : name,
                        'elements' : rtn
                    }
                with open(os.path.join(Dt.dirs["recommend"], name), 'w') as json_out:
                    json.dump(json_dict, json_out)
    
    Dt.fnames = succeeded_fnames
    Dt.other_fnames = other_fnames
    succeeded = len(succeeded_fnames)
    detected = len(other_fnames) + succeeded
    return "{} out of {} ({:.2f}%) processed successfully with recommendations.".format(succeeded, detected, succeeded/detected*100)


#############################################
# APIs
#############################################
@app.route('/process', methods=['GET'])
def process():
    """
    Do the prediction. The result will be 
    stored in /Recommend
    """
    check_dirs()
    return rule_based()
    #return cluster_text()
    
@app.route('/init_page', methods=['GET'])
def init_page():
    """
    Returns A JSON LIST of the following: 
    (containing all recommendations)
    {
        "filename": "labeling_....",
        "elements":
        [
            {
                "boundingBox":[602,777,636,776,636,804,603,805],
                "text": "Something",
                "confidence":"Low"
            },
            ...
        ]
    }
    """    
    json_objs = []
    if len(Dt.fnames) == 0:
        for root, dirs, files in os.walk(Dt.dirs["recommend"], topdown=False):
            Dt.fnames = list([name for name in files if name.endswith(".json")])
            Dt.fnames.sort()

    for name in Dt.fnames:
        with open(os.path.join(Dt.dirs["recommend"], name)) as json_rec:
            json_objs.append(json_rec.read())

    return "[{}]".format(",".join(json_objs))

@app.route('/submit', methods=['POST'])
def submit():
    """
    In the raw body of the POST, send a string of which 
    the format is a (json) list of the following:
    {
        "filename" : "labeling_0000.json",
        "content" : {
            "text" : "$13. 53",
            "elements":
            [
                {"bounding box":[602,777,636,776,636,804,603,805]},
                {"bounding box":[602,777,636,776,636,804,603,805]},
                ...
            ]
        }
    }
    """
    answer = request.stream.read()
    json_objs = json.loads(answer)
    for obj in json_objs:
        with open(os.path.join(Dt.dirs['final'], obj['filename']),'w') as json_out:
            if(not len(obj["content"]['text'])==0 and not len(obj["content"]['elements'])==0):
                json.dump(obj["content"], json_out)
    
    return "Succeeded"


#############################################
# Main
#############################################
if __name__ == "__main__":
    app.run()
