from cluster import get_cluster
class Dt: 
    key_word = "Date"
    dirs = {
        "input" : "./LabelingTrainingData/Input",
        "recommend" : "./LabelingTrainingData/Recommend",
        "final" : "./LabelingTrainingData/Final",
        "metadata" : "./LabelingTrainingData/"
    }

    #file_idx = 0
    #images_per_page = 2
    fnames = []
    succeeded_fnames, other_fnames = [], []

def sort_by_clusters():
    c = get_cluster(Dt.dirs['input'])
    print(c)

sort_by_clusters()