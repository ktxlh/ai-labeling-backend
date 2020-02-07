"""
會有以下dirs:
1. raw input: input_dir
2. 得到的 推薦標注: recommended_dir
3. 最後確定標注: final_dir
"""
import os
import flask
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

    
def load_page():
    json_objs = []
    for i in range(Dt.images_per_page):
        Dt.file_idx += 1
        if(Dt.file_idx >= len(Dt.fnames)):
            break
        name = Dt.fnames[Dt.file_idx]
        with open(os.path.join(Dt.dirs["recommend"], name)) as json_rec:
            json_objs.append(json_rec.read())

    return "[{}]".format(",".join(json_objs))

@app.route('/init_page', methods=['GET'])
def init_page():
    """
    翻頁。每次enter再進下一頁
    OUT: A JSON LIST (len=4) of the following:
    {
        "filename": "labeling_....",
        "elements":
        [
            {"boundingBox":[602,777,636,776,636,804,603,805]},
            {"boundingBox":[641,776,668,776,668,804,642,804]}
        ]
    }
    """
    Dt.file_idx = 0
    return load_page()

app.run()