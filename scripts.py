import os
from collections import Counter

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
        if filename == 'filename': continue
        s = file_to_label.setdefault(filename, set())
        s.add(label)
        s = label_to_file.setdefault(label, set())
        s.add(filename)
    file.close()
    return file_to_label, label_to_file

def count_events(file):
    file = open(file, 'r')
    event_counts = Counter()
    for line in file:
        parts = line.split('\t')
        label = parts[1].removesuffix('\n')
        event_counts[label] += 1
    file.close()
    return event_counts

def dict_to_counter(d):
    c = Counter()
    for k, v in d.items():
        c[k] = len(v)
    c = c.most_common()
    return c

if __name__ == '__main__':
    l_path = os.path.join('src','class_labels.tsv')
    ase_path = os.path.join('src','audioset_strong_eval.tsv')
    ast_path = os.path.join('src','audioset_strong_train.tsv')

    labels = load_labels(l_path)
    se_ftl, se_ltf = map_file_and_label(ase_path)
    st_ftl, st_ltf = map_file_and_label(ast_path)

    st_ltf_counter = dict_to_counter(st_ltf)
    se_ltf_counter = dict_to_counter(se_ltf)

    se_ec = count_events(ase_path)
    st_ec = count_events(ast_path)
    print(st_ec)
