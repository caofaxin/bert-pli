import os
import csv
import argparse
import xml.etree.ElementTree as ET
import random
random.seed(42)

#
# config
#
parser = argparse.ArgumentParser()

parser.add_argument('--train-dir', action='store', dest='train_dir',
                    help='training file directory location', required=True)

parser.add_argument('--output-dir', action='store', dest='output_dir',
                    help='training output file location for test.tsv', required=True)

parser.add_argument('--test-gold-labels', action='store', dest='test_gold_labels',
                    help='location and name of the gold labels xml-file to create a training set from the test data', required=True)

args = parser.parse_args()

#train_dir = '/mnt/c/Users/sophi/Documents/phd/data/coliee2019/task2/task2_test'
#output_dir = '/mnt/c/Users/sophi/Documents/phd/data/coliee2019/task2'
#test_gold_labels = '/mnt/c/Users/sophi/Documents/phd/data/coliee2019/task2/task2_test_golden-labels.xml'

#
# load directory structure
#

list_dir = [x for x in os.walk(args.train_dir)]

#
# load gold labels as dictionary
#

tree = ET.parse(args.test_gold_labels)
root = tree.getroot()

gold_labels = {}
for child in root:
    rank = child.find('entailing_paragraphs').text
    rank = rank.split(',')
    gold_labels.update({child.attrib['id']: rank})

#
# Write test.tsv file with query_id \t doc_id \t query_text \t doc_relevant_text
#

with open(os.path.join(args.output_dir, 'test.tsv'), 'wt') as out_file:
    tsv_writer = csv.writer(out_file, delimiter='\t')
    for sub_dir in list_dir[0][1]:
        # read in query text
        with open(os.path.join(args.train_dir, sub_dir, 'entailed_fragment.txt'), 'r') as entailed_fragment:
            query_text_lines = entailed_fragment.read().splitlines()
            query_text = ' '.join([text.strip().replace('\n', '') for text in query_text_lines])

        # read in all paragraphs with their names and then choose the relevant ones and sample irrelevant ones!
        list_sub_dir_paragraphs = [x for x in os.walk(os.path.join(args.train_dir, sub_dir, 'paragraphs'))]
        paragraphs_text = {}
        for paragraph in list_sub_dir_paragraphs[0][2]:
            with open(os.path.join(args.train_dir, sub_dir, 'paragraphs', paragraph), 'r') as paragraph_file:
                para_text = paragraph_file.read().splitlines()[1:]
                paragraphs_text.update({paragraph.split('.')[0]: ' '.join([text.strip().replace('\n', '') for text in para_text])})

        doc_rel_id = gold_labels.get(sub_dir)

        # write text in test.tsv file
        for id in doc_rel_id:
            doc_rel_text = paragraphs_text.get(id)
            tsv_writer.writerow([sub_dir, '{}_{}'.format(sub_dir,id), query_text, doc_rel_text])