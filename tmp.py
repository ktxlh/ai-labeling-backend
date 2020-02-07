@app.route('/score', methods=['GET'])
def score():
    """
    Output
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