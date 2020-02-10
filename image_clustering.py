"""
pip3 install opencv-python
"""
def get_cluster(path):
    import os, codecs
    import cv2
    import numpy as np
    from sklearn.cluster import KMeans
    cluster_num = 5 
    def get_file_name(path):
        '''
        Args: path to list;  Returns: path with filenames
        '''
        filenames = os.listdir(path)
        path_filenames = []
        filename_list = []
        for file in filenames:
            if not file.startswith('.'):
                if '.json' not in file :
                    path_filenames.append(os.path.join(path, file))
                    filename_list.append(file)

        return path_filenames

    def knn_detect(file_list, cluster_nums, randomState = None):
        features = []
        files = file_list
        sift = cv2.xfeatures2d.SIFT_create()
        for file in files:

                print(file)
                img = cv2.imread(file)
                img = cv2.resize(img, (350,350 ), interpolation=cv2.INTER_CUBIC)
                gray= cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    #             sift = cv2.xfeatures2d.SIFT_create()
    #             kp = sift.detect(gray,None)
    #             img=cv2.drawKeypoints(gray,kp,img)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 			print(gray.dtype)
                _, des = sift.detectAndCompute(gray, None)

                if des is None:
                    file_list.remove(file)
                    continue

                reshape_feature = des.reshape(-1, 1)
                features.append(reshape_feature[0].tolist())

        input_x = np.array(features)

    # 	kmeans = KMeans(n_clusters = cluster_nums, random_state = randomState).fit(input_x)
        clustering = SpectralClustering(n_clusters=cluster_num,assign_labels="discretize",random_state=0).fit(input_x)
    # 	return kmeans.labels_, kmeans.cluster_centers_
        return clustering.labels_

    def res_fit(filenames, labels):

        files = [file.split('/')[-1] for file in filenames]

        return dict(zip(files, labels))

    def save(path, filename, data):
        file = os.path.join(path, filename)
        with codecs.open(file, 'w', encoding = 'utf-8') as fw:
            for f, l in data.items():
                fw.write("{}\t{}\n".format(f, l))


    path_filenames = get_file_name(path)

    # labels, cluster_centers = knn_detect(path_filenames, 5)
    labels = knn_detect(path_filenames, cluster_num) 
    res_dict = res_fit(path_filenames, labels)
    # save(r'E:\Study\CareerHack\OneDrive_2_2020-2-7\train20200205\LabelingTrainingData\Input', 'knn_res.txt', res_dict)
    res_dict



    cluster = []
    for i in range(cluster_num):
        cluster.append([])
    for key in res_dict :
        cluster[res_dict[key]].append(key.replace(path+"\\",""))
    return cluster