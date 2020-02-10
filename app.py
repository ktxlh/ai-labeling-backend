"""
有以下dirs:
1. raw input, 要先準備好: Input
2. 推薦標注: Recommend
3. 最後使用者標注，評分用: Final

flask cors的問題解法：
https://stackoverflow.com/questions/25594893/how-to-enable-cors-in-flask
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
@app.route('/', methods=['GET'])
def home():
    return check_dirs()

@app.route('/process', methods=['GET'])
def process():
    """
    開始prediction. （考慮user行為的算法、套neural的算法之後想）
    predict完存進recommend
    ##OUT: Number of files are successfully processed / number of files detected
    
    不對！我應該把圖片放進該放的html，直接return整個html
    """
    check_dirs()
    return rule_based()
    #return cluster_text()
    
@app.route('/init_page', methods=['GET'])
def init_page():
    """
    OUT: A JSON LIST of the following: (containing all recommendations)
    {
        "filename": "labeling_....",
        "elements":
        [
            {
                "boundingBox":[602,777,636,776,636,804,603,805],
                "text": "Something",
                "confidence":"Low"
            }
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
    key: "answer"
    value: A string, which is a json list of the following:
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

app.run()
