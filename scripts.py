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
    return c

def make_counts_table(file, labels, st_ltf, se_ltf, st_ec, se_ec, wtb_ec, wtu_ec, we_ec):
    file = open(file, 'w')
    file.write("class_id\ttrain_event_count\ttrain_file_count\teval_event_count\teval_file_count\tweak_train_balanced_count\tweak_train_unbalanced_count\tweak_eval_count\n")
    for id_ in labels:
        file.write(f"{id_}\t{st_ec[id_]}\t{st_ltf[id_]}\t{se_ec[id_]}\t{se_ltf[id_]}\t{wtb_ec[id_]}\t{wtu_ec[id_]}\t{we_ec[id_]}\n")
    file.close()

def filter_by_file(file_list, data_old, data_new, i):
    file_list = open(file_list, 'r')
    files = set()
    for line in file_list:
        files.add(line[:-1])
    file_list.close()
    data_old = open(data_old, 'r')
    data_new = open(data_new, 'w')
    for line in data_old:
        filename = line.split('\t')[i].removesuffix('\n')
        if filename in files or filename == 'filename':
            data_new.write(line)
    data_old.close()
    data_new.close()
    

if __name__ == '__main__':
    l_path = os.path.join('src','class_labels.tsv')
    ase_path = os.path.join('src','audioset_strong_eval.tsv')
    ast_path = os.path.join('src','audioset_strong_train.tsv')
    awtb_path = os.path.join('src','audioset_weak_train_balanced.tsv')
    awtu_path = os.path.join('src','audioset_weak_train_unbalanced.tsv')
    awe_path = os.path.join('src','audioset_weak_eval.tsv')

    labels = load_labels(l_path)
    se_ftl, se_ltf = map_file_and_label(ase_path)
    st_ftl, st_ltf = map_file_and_label(ast_path)
    we_ftl, we_ltf = map_file_and_label(awe_path)
    wtb_ftl, wtb_ltf = map_file_and_label(awtb_path)
    wtu_ftl, wtu_ltf = map_file_and_label(awtu_path)

    st_ltf_counter = dict_to_counter(st_ltf)
    se_ltf_counter = dict_to_counter(se_ltf)
    we_ec = dict_to_counter(we_ltf)
    wtb_ec = dict_to_counter(wtb_ltf)
    wtu_ec = dict_to_counter(wtu_ltf)

    se_ec = count_events(ase_path)
    st_ec = count_events(ast_path)

    make_counts_table('table3.tsv', labels, st_ltf_counter, se_ltf_counter, st_ec, se_ec,
                      wtb_ec, wtu_ec, we_ec)
