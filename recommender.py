
def has_date(date):
    import re
    from datetime import datetime
    
    if re.search(r"(\d{4}[-/]\d{1,2}[-/]\d{1,2})",date) != None :
        return True
    elif re.search(r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})",date) != None :
        return True
    elif re.search(r"(\d{4}[-/]\d{1,2}[-/]\d{2})",date) != None :
        return True
    elif re.search(r"(\d{4}[-/]\d{1,2}[-/]\d{1,2})",date) != None :
        return True
    elif re.search(r"([a-zA-Z]{2,9}[-/]\d{1,2}[-/]\d{1,2})",date) != None :
        return True
    elif re.search(r"([a-zA-Z]{2,9}[.]*\s*\d{1,2}[']*[-/]*\s*\d{1,2})",date) != None :
        return True
    elif re.search(r"(\d{1,2}[-/][a-zA-Z]{2,9}[-/]\d{1,2})",date) != None :
        return True
    elif re.search(r"(\d{4}[-/]\d{1,2}[-/]\d{1,2})",date) != None :
        return True
    elif re.search(r"(\d{4}[-/]\d{1,2}[-/]\d{1,2})",date) != None :
        return True
    else:
        return False

def select_box(keywords,img_json):
    def find_Y(keywords,img_json):
        upper=lower = 0
        if keywords != "date" :
            for boundingBox in img_json['recognitionResults'][0]['lines'] :
                if keywords.lower() in boundingBox['text'].lower() :
                    upper = boundingBox['boundingBox'][1]
                    lower = boundingBox['boundingBox'][7]
        else :
            for boundingBox in img_json['recognitionResults'][0]['lines'] :
                if has_date(boundingBox['text'].lower().replace(" ","")):
                    upper = boundingBox['boundingBox'][1]
                    lower = boundingBox['boundingBox'][7]
            
        return (upper,lower)
    
    upper,lower = find_Y(keywords,img_json)
    box_selected = []
    if upper or lower != 0:
        for boundingBox in img_json['recognitionResults'][0]['lines'] :
            if boundingBox['boundingBox'][1] > upper-20 and boundingBox['boundingBox'][7] < lower+20:
#                 for box in boundingBox['words']:
#                 for box in boundingBox['words']:
                box_selected.extend(boundingBox['words'])
            
    if box_selected == [] :
        return 0
    return box_selected
    