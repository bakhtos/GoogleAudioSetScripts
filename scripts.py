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

def map_file_and_label(file):
    file = open(file, 'r')
    file_to_label = dict()
    label_to_file = dict()
    for line in file:
        parts = line.split('\t')
        filename = parts[0]
        label = parts[1].removesuffix('\n')
        if parts[0] == 'filename': continue
        s = file_to_label.setdefault(filename, set())
        s.add(label)
        s = label_to_file.setdefault(label, set())
        s.add(file)
    file.close()
    return file_to_label, label_to_file

if __name__ == '__main__':
    labels = load_labels(os.path.join('src', 'class_labels.tsv'))
    se_ftl, se_ltf = map_file_and_label(os.path.join('src', 'audioset_strong_eval.tsv'))
    st_ftl, st_ltf = map_file_and_label(os.path.join('src', 'audioset_strong_train.tsv'))
