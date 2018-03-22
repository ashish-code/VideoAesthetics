"""
Compute a histogram based aesthetic descriptor for trailer.
The aesthetic scores of the scene-exemplar frames is used to generate this histogram.
"""

# import libraries
import numpy as np 
import os 
import sys
from sklearn import svm
from sklearn.model_selection import train_test_split

from scipy import interp
import matplotlib.pyplot as plt
from itertools import cycle

from sklearn.metrics import roc_curve, auc
from sklearn.model_selection import StratifiedKFold

data_root = '/home/ashish/Data/VideoAesthetics/'
trailer_video_dir = 'trailer_video'
video_file_type = 'mp4'
frame_file_type = 'png'
rating_file_name = 'trailer_ratings.txt'
scene_list_file_name = 'scene_list.csv'
scene_frame_dir = 'scene_frame_images/'
scene_frame_list_dir = 'scene_frame_list/'
scene_aesthetic_score_dir = 'scene_aesthetics/'
aesthetic_feature_file = 'aesthetic_data.csv'

RATING_THRESHOLD = 5.5


def get_aesthetic_score_file_path(trailer_id):
    return os.path.join(data_root, scene_aesthetic_score_dir, trailer_id + '.csv')


def process_trailer_list(trailer_rating_file_path):
    with open(data_root+aesthetic_feature_file, 'w+') as ff:
        with open(trailer_rating_file_path, 'r') as f:
            lines = f.readlines()
            trailer_id_list = []
            trailer_rating_list = []
            for line in lines:
                trailer_id = line.split(',')[0]
                trailer_rating = float(line.split(',')[1])
                trailer_id_list.append(trailer_id)
                trailer_rating_list.append(trailer_rating)
        
        for i_id, trailer_id in enumerate(trailer_id_list):
            # print('{}: processing {}'.format(i_id, trailer_id))
            aesthetic_score_file = get_aesthetic_score_file_path(trailer_id)
            if not os.path.exists(aesthetic_score_file):
                print('{} does not exists!'.format(trailer_id))
                continue
            a_score = []
            with open(aesthetic_score_file, 'r') as af:
                lines = af.readlines()
                if len(lines) < 2:
                    print('{} has too few scenes'.format(trailer_id))
                    continue
            for line in lines:
                a_score.append(float(line.split(',')[1]))
            
            # print(a_score)
            _h,_ = np.histogram(np.array(a_score), bins=16, range=(0.0, 1.0), normed=True)
            # print(_h)
            if trailer_rating_list[i_id] > 8.2 or trailer_rating_list[i_id] < 2.8:
                t_label = 1
                if trailer_rating_list[i_id] <= RATING_THRESHOLD:
                    t_label = 0
                h = _h.tolist()
                for item in h:
                    ff.write('{},'.format(item))
                ff.write('{}\n'.format(t_label))


def compute_svm_results():
    data = np.loadtxt(data_root+aesthetic_feature_file, dtype=float, delimiter=',')
    X = data[:,:-1]
    y = data[:,-1]
    print('{},{}'.format(np.sum(y==1), np.sum(y==0)))
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    clf = svm.SVC(kernel='linear', C=1).fit(X_train, y_train)
    perf = clf.score(X_test, y_test)
    print(data.shape)
    print('classification performance: {}'.format(perf))
    n_samples, n_features = X.shape
    random_state = np.random.RandomState(0)
    # #############################################################################
    # Classification and ROC analysis

    # Run classifier with cross-validation and plot ROC curves
    cv = StratifiedKFold(n_splits=6)
    classifier = svm.SVC(kernel='linear', probability=True,
                        random_state=random_state)

    tprs = []
    aucs = []
    mean_fpr = np.linspace(0, 1, 100)

    i = 0
    for train, test in cv.split(X, y):
        probas_ = classifier.fit(X[train], y[train]).predict_proba(X[test])
        # Compute ROC curve and area the curve
        fpr, tpr, thresholds = roc_curve(y[test], probas_[:, 1])
        tprs.append(interp(mean_fpr, fpr, tpr))
        tprs[-1][0] = 0.0
        roc_auc = auc(fpr, tpr)
        aucs.append(roc_auc)
        plt.plot(fpr, tpr, lw=1, alpha=0.3,
                label='ROC fold %d (AUC = %0.2f)' % (i, roc_auc))

        i += 1
    plt.plot([0, 1], [0, 1], linestyle='--', lw=2, color='r',
            label='Luck', alpha=.8)

    mean_tpr = np.mean(tprs, axis=0)
    mean_tpr[-1] = 1.0
    mean_auc = auc(mean_fpr, mean_tpr)
    std_auc = np.std(aucs)
    plt.plot(mean_fpr, mean_tpr, color='b',
            label=r'Mean ROC (AUC = %0.2f $\pm$ %0.2f)' % (mean_auc, std_auc),
            lw=2, alpha=.8)

    std_tpr = np.std(tprs, axis=0)
    tprs_upper = np.minimum(mean_tpr + std_tpr, 1)
    tprs_lower = np.maximum(mean_tpr - std_tpr, 0)
    plt.fill_between(mean_fpr, tprs_lower, tprs_upper, color='grey', alpha=.2,
                    label=r'$\pm$ 1 std. dev.')

    plt.xlim([-0.05, 1.05])
    plt.ylim([-0.05, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic example')
    plt.legend(loc="lower right")
    plt.show()
    
    


if __name__ == '__main__':
    trailer_rating_file_path = os.path.join(data_root, rating_file_name)
    if not os.path.exists(trailer_rating_file_path):
        print('Trailer rating file not found!')
        exit
    process_trailer_list(trailer_rating_file_path)
    compute_svm_results()