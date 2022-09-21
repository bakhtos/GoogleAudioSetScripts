import os

def load_labels(file):
    file = open(file, 'r')
    labels = dict()
    for line in file:
        id_, label = line.split('\t')
        if id_ == 'id': continue
        labels[id_] = label[:-1] 
    file.close()
    return labels


if __name__ == '__main__':
    labels = load_labels(os.path.join('src', 'class_labels.tsv'))
