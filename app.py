"""
有以下dirs:
1. raw input, 要先準備好: Input
2. 推薦標注: Recommend
3. 最後使用者標注，評分用: Final

flask cors的問題解法：（稍微試了一次，還可能要改）
https://stackoverflow.com/questions/25594893/how-to-enable-cors-in-flask

read/write json
https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/
"""
import os
import flask
from flask import request
from flask_cors import CORS, cross_origin
import json
from recommender import select_box

app = flask.Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config["DEBUG"] = True

class Dt: 
    key_word = "Tax"
    dirs = {
        "input" : "/Users/shanglinghsu/Downloads/labeling with ai/LabelingTrainingData/Input",
        "recommend" : "/Users/shanglinghsu/Downloads/labeling with ai/LabelingTrainingData/Recommend",
        "final" : "/Users/shanglinghsu/Downloads/labeling with ai/LabelingTrainingData/Final",
        "metadata" : "/Users/shanglinghsu/Downloads/labeling with ai/LabelingTrainingData/"
    }

    #file_idx = 0
    #images_per_page = 2
    fnames = []
    succeeded_fnames, other_fnames = [], []

#############################################
# Utils
#############################################
def check_dirs():
    dirs = Dt.dirs
    if not os.path.isdir(dirs["input"]):
        print("ERROR: Bad input dir path: " + dirs["input"])
        exit()
    for dkey in dirs.keys():
        if not os.path.isdir(dirs[dkey]):
            os.mkdir(dirs[dkey])
check_dirs()


#############################################
# APIs
#############################################
@app.route('/', methods=['GET'])
def home():
    return "<h1>Sample Home html</h1><p>This site is a prototype API</p>"

@app.route('/process', methods=['GET'])
def process():
    """
    開始prediction. （考慮user行為的算法、套neural的算法之後想）
    predict完存進recommend
    ##OUT: Number of files are successfully processed / number of files detected
    
    不對！我應該把圖片放進該放的html，直接return整個html
    """
    succeeded_fnames, other_fnames = [], []
    for root, dirs, files in os.walk(Dt.dirs["input"], topdown=False):
        fnames = list([name for name in files if name.endswith(".json")])
        
        fnames.sort() # Can be sorted according to the confidence levels of the prediction
        detected = len(fnames)
        for name in fnames:
            with open(os.path.join(Dt.dirs["input"], name)) as json_in:
                json_obj = json.loads(json_in.read())
                rtn = select_box(Dt.key_word, json_obj)
                
                if rtn ==0 : 
                    other_fnames.append(name)
                else:
                    succeeded_fnames.append(name)
                    json_dict = dict()
                    json_dict['filename'] = name
                    json_dict['elements'] = rtn
                    with open(os.path.join(Dt.dirs["recommend"], name), 'w') as json_out:
                        json.dump(json_dict, json_out)
    
    Dt.fnames = succeeded_fnames
    succeeded = len(succeeded_fnames)
    detected = len(other_fnames) + succeeded
    return "{} out of {} ({:.2f}%) processed successfully with recommendations.".format(succeeded, detected, succeeded/detected*100)

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
    for name in Dt.fnames:
        with open(os.path.join(Dt.dirs["recommend"], name)) as json_rec:
            json_objs.append(json_rec.read())

    return "[{}]".format(",".join(json_objs))

@app.route('/submit', methods=['GET'])
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
                {
                    "bounding box":[602,777,636,776,636,804,603,805],
                    "bounding box":[602,777,636,776,636,804,603,805],
                    ...
                }
            ]
        }
    }
    """
    if 'answer' in request.args:
        answer = str(request.args['answer'])
    else:
        return "Failed"
    
    json_objs = json.loads(answer)
    for obj in json_objs:
        with open(os.path.join(Dt.dirs['final'], obj['filename']),'w') as json_out:
            json.dump(obj["content"], json_out)
    
    return "Succeeded"

app.run()