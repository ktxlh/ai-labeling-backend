def select_box(keywords,img_json):
    def find_Y(keywords,img_json):
        upper=lower = 0
        if keywords != "date" :
            for boundingBox in img_json['recognitionResults'][0]['lines'] :
                if keywords.lower() in boundingBox['text'].lower():
                    upper = boundingBox['boundingBox'][1]
                    lower = boundingBox['boundingBox'][7]
        else :
            return 0

 
        return (upper,lower)
    
    upper,lower = find_Y(keywords,img_json)
    box_selected = []
    for boundingBox in img_json['recognitionResults'][0]['lines'] :
        if boundingBox['boundingBox'][1] > upper-5 and boundingBox['boundingBox'][7] < lower+5:
            for box in boundingBox['words']:
                box_selected.append(box["boundingBox"])
            
    if box_selected == [] :
        return 0
    return box_selected