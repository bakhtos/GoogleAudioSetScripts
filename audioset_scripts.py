import os
from collections import Counter

def load_labels(file):
    ''' Load a dictionary from labels ids to label names from specified file.'''
    file = open(file, 'r')
    labels = dict()
    for line in file:
        id_, label = line.split('\t')
        if id_ == 'id': continue
        labels[id_] = label[:-1] 
    file.close()
    return labels

def map_file_and_label(file):
    ''' Map files and occuring events and vice versa.

    Parameters
    _________

    file : str, one of the Audioset files (in 'Reformatted' format).

    Returns
    _______

    file_to_labels : dict[str] -> set[str],
        Map from files in the dataset to a set of label ids they contain.
    label_to_file : dict[str -> set[str],
        Map from label ids to files in the dataset that contain them.
    '''
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
    ''' Count event occurences in the dataset.

    Parameters
    __________

    file : str, one of the Audioset files (in 'Reformatted' format)

    Returns
    _______

    event_counts : Counter[str],
        For each label id gives the total count of events in the specified file. 
    '''

    file = open(file, 'r')
    event_counts = Counter()
    for line in file:
        parts = line.split('\t')
        label = parts[1].removesuffix('\n')
        event_counts[label] += 1
    file.close()
    return event_counts

def dict_to_counter(d):
    ''' Convert a dict to a counter changing the values into their sizes.'''
    c = Counter()
    for k, v in d.items():
        c[k] = len(v)
    return c

def make_counts_table(file, labels, st_ltf, se_ltf, st_ec, se_ec, wtb_ec, wtu_ec, we_ec):
    ''' Make a tsv file with counts of files and events for weak and strong, train and eval splits.'''
    file = open(file, 'w')
    file.write("class_id\ttrain_event_count\ttrain_file_count\teval_event_count\teval_file_count\tweak_train_balanced_count\tweak_train_unbalanced_count\tweak_eval_count\n")
    for id_ in labels:
        file.write(f"{id_}\t{st_ec[id_]}\t{st_ltf[id_]}\t{se_ec[id_]}\t{se_ltf[id_]}\t{wtb_ec[id_]}\t{wtu_ec[id_]}\t{we_ec[id_]}\n")
    file.close()

def make_top_counts_table(file, top, st_ltf, se_ltf, st_ec, se_ec, wtb_ec, wtu_ec, we_ec):
    ''' Make a tsv table with counts of the 'top' most common classes.'''
    file = open(file, 'w')
    top_classes = st_ec.most_common(top)
    file.write("class_id\ttrain_event_count\ttrain_file_count\teval_event_count\teval_file_count\tweak_train_balanced_count\tweak_train_unbalanced_count\tweak_eval_count\n")
    for id_, _ in top_classes:
        file.write(f"{id_}\t{st_ec[id_]}\t{st_ltf[id_]}\t{se_ec[id_]}\t{se_ltf[id_]}\t{wtb_ec[id_]}\t{wtu_ec[id_]}\t{we_ec[id_]}\n")
    file.close()

def make_downloaded_counts_table(file, top, st_ltf, se_ltf, st_ec, se_ec, sttd_ltf, setd_ltf, sttd_ec, setd_ec):
    ''' Make a tsv table with counts of files and events in the dataset vs actually downloaded files.'''
    file = open(file, 'w')
    top_classes = st_ec.most_common(top)
    file.write("class_id\ttrain_event_count\ttrain_event_count_downloaded\ttrain_file_count\ttrain_file_count_downloaded\teval_event_count\teval_event_count_downloaded\teval_file_count\teval_file_count_downloaded\n")
    for id_, _ in top_classes:
        file.write(f"{id_}\t{st_ec[id_]}\t{sttd_ec[id_]}\t{st_ltf[id_]}\t{sttd_ltf[id_]}\t{se_ec[id_]}\t{setd_ec[id_]}\t{se_ltf[id_]}\t{setd_ltf[id_]}\n")
    file.close()

def filter_by_file(filter_list, data_old, data_new, i):
    ''' Only keep lines in the datasets file where a specific column contains one of the specified values.

    Parameters
    __________

    filter_list : str, file that contains the set of allowed values, one on a line.
    data_old : str, a dataset file to load (in the 'Reformatted' format').
    data_new : str, filename to save the filtered dataset into.
    i : int, dataset's i'th column will be filtered (base-0 indexing).
    '''

    header_set = {'filename', 'event_label', 'onset', 'offset'}
    filter_list = open(filter_list, 'r')
    items = set()
    for line in filter_list:
        items.add(line[:-1])
    filter_list.close()
    data_old = open(data_old, 'r')
    data_new = open(data_new, 'w')
    for line in data_old:
        item = line.split('\t')[i].removesuffix('\n')
        if item in items or item in header_set:
            data_new.write(line)
    data_old.close()
    data_new.close()


def select_classes(data, top, output):
    ''' Select the 'top' most common classes by the specified counts.

    Parameters
    __________

    data : Counter(), counter whose counts are use to deduce most common classes.
    top : int, this many most common classes are taken.
    output: str, selected classes are written into this file one on line in 'desceding' order.

    Returns
    _______

    classes : set, set of the selected classes.
    '''

    classes = set()
    top110 = data.most_common(top)
    file = open(output, 'w')
    for c, _ in top110:
        file.write(c+'\n')
        classes.add(c)
    file.close()
    return classes

def select_files(data, output):
    ''' Keep only the unique filenames from a dataset file.

    Parameters
    __________

    data : str, A dataset file to select filenames from (in 'Reformatted' format).
    output : str, Filenames from 'data' are saved here, one on line.

    Returns
    _______

    files : set[str], Set of the selected filenames.
    '''

    files = set()
    file = open(data, 'r')
    for line in file:
        f = line.split('\t')[0]
        if f == 'filename': continue
        files.add(f)
    output = open(output, 'w')
    for f in files:
        output.write(f"{f}\n")
    file.close()
    output.close()
    return files
    

if __name__ == '__main__':
    # Initialize all paths
    #   a - audioset (common prefix)
    #   s/w - strong/weak
    #   e/t/tb/tu - eval/train/train balanced/train unbalanced
    #   t - top classes
    #   d - downloaded
    l_path = os.path.join('src','class_labels.tsv')
    ase_path = os.path.join('src','audioset_strong_eval.tsv')
    aset_path = 'audioset_strong_eval_top110classes.tsv'
    asetd_path = 'audioset_strong_eval_top110classes_downloaded.tsv'
    ased_path = 'audioset_strong_eval_downloaded.tsv'
    ast_path = os.path.join('src','audioset_strong_train.tsv')
    astt_path = 'audioset_strong_train_top110classes.tsv'
    asttd_path = 'audioset_strong_train_top110classes_downloaded.tsv'
    astd_path = 'audioset_strong_train_downloaded.tsv'
    awtb_path = os.path.join('src','audioset_weak_train_balanced.tsv')
    awtu_path = os.path.join('src','audioset_weak_train_unbalanced.tsv')
    awe_path = os.path.join('src','audioset_weak_eval.tsv')
    asetd_path = 'audioset_strong_eval_top110classes_downloaded.tsv'

    # Load labels and map all datasets
    labels = load_labels(l_path)
    se_ftl, se_ltf = map_file_and_label(ase_path)
    st_ftl, st_ltf = map_file_and_label(ast_path)
    setd_ftl, setd_ltf = map_file_and_label(asetd_path)
    sttd_ftl, sttd_ltf = map_file_and_label(asttd_path)
    we_ftl, we_ltf = map_file_and_label(awe_path)
    wtb_ftl, wtb_ltf = map_file_and_label(awtb_path)
    wtu_ftl, wtu_ltf = map_file_and_label(awtu_path)

    # Counts files per labels in datasets
    st_ltf_counter = dict_to_counter(st_ltf)
    se_ltf_counter = dict_to_counter(se_ltf)
    setd_ltf_counter = dict_to_counter(setd_ltf)
    sttd_ltf_counter = dict_to_counter(sttd_ltf)
    we_ec = dict_to_counter(we_ltf)
    wtb_ec = dict_to_counter(wtb_ltf)
    wtu_ec = dict_to_counter(wtu_ltf)

    # Count events in strong dataset
    se_ec = count_events(ase_path)
    st_ec = count_events(ast_path)
    setd_ec = count_events(asetd_path)
    sttd_ec = count_events(asttd_path)

    # Select top-110 classes by strong train event count
    select_classes(st_ec, 110, 'selected_classes.txt')

    # Filter strong dataset by top classes, downloaded files, and both
    filter_by_file('selected_classes.txt', ast_path, astt_path, 1)
    filter_by_file('selected_classes.txt', ase_path, aset_path, 1)
    filter_by_file('train_list.txt', ast_path, astd_path, 0)
    filter_by_file('eval_list.txt', ase_path, ased_path, 0)
    filter_by_file('selected_classes.txt', astd_path, asttd_path, 1)
    filter_by_file('selected_classes.txt', ased_path, asetd_path, 1)

    # List all the files in top-110 to be downloaded
    select_files(astt_path, "selected_files_train.txt")
    select_files(aset_path, 'selected_files_eval.txt')

    # Make counts tables of original dataset, top-110 classes, and top-100 vs downloaded
    make_counts_table('AudioSetClassCounts.tsv', labels, st_ltf_counter, se_ltf_counter, st_ec, se_ec,
                      wtb_ec, wtu_ec, we_ec)
    make_top_counts_table('AudioSetTop110ClassesSortedCounts.tsv', 110, st_ltf_counter, se_ltf_counter, st_ec, se_ec,
                      wtb_ec, wtu_ec, we_ec)
    make_downloaded_counts_table('AudioSetDownloadedCounts.tsv', 110, st_ltf_counter, se_ltf_counter, st_ec, se_ec,
                                 sttd_ltf_counter, setd_ltf_counter, sttd_ec, setd_ec)
