#!/usr/bin/env python3

# Get out-of-vocabulary rate for word vectors on text.

import sys
import os

from collections import Counter
from heapq import nlargest
from logging import warning


DEFAULT_ENCODING = 'UTF-8'


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser()
    ap.add_argument('-e', '--encoding', default=DEFAULT_ENCODING,
                    help='text enconding (default {})'.format(DEFAULT_ENCODING))
    ap.add_argument('-f', '--field', metavar='N', default=None, type=int,
                    help='words found in TSV field N (default: plain text)')
    ap.add_argument('-l', '--lowercase', default=False, action='store_true',
                    help='lowercase input text')
    ap.add_argument('-m', '--max-words', default=None, type=int,
                    help='maximum number of words to read from wordvecs')
    ap.add_argument('-n', '--oov-number', metavar='N', default=10, type=int,
                    help='print out most frequent N OOV words')
    ap.add_argument('wordvecs')
    ap.add_argument('text', nargs='+')
    return ap


def load_word_vector_vocabulary(path, options):
    vocab = set()
    with open(path, 'rb') as f:
        dim_line = f.readline().rstrip(b'\n')
        for ln, l in enumerate(f, start=2):
            word, rest = l.split(b' ', 1)
            try:
                word = word.decode(options.encoding)
            except:
                warning('Failed to decode word on line {} in {} as {}'.format(
                    ln, path, options.encoding))
                continue
            if word in vocab:
                warning('duplicate word in {}: {}'.format(word, path))
            vocab.add(word)
            if (options.max_words is not None and
                len(vocab) >= options.max_words):
                break
    print('Read {} words from {}'.format(len(vocab), path))
    return vocab


def process(path, vocab, options):
    total, oov_total, oov_count = 0, 0, Counter()
    with open(path, encoding=options.encoding) as f:
        for ln, l in enumerate(f, start=1):
            l = l.rstrip('\n')
            if not l or l.isspace():
                continue
            if not options.field:
                words = l.split()
            else:
                words = [l.split('\t')[options.field-1]]    # 1-based
            if options.lowercase:
                words = [w.lower() for w in words]
            for w in words:
                if w not in vocab:
                    oov_count[w] += 1
                    oov_total += 1
            total += len(words)
    for w in nlargest(options.oov_number, oov_count,
                      key=lambda w: oov_count[w]):
        c = oov_count[w]
        print('{}\t{:.2%} ({}/{})'.format(w, c/total, c, total))
    print('OOV rate {:.2%} ({}/{})'.format(oov_total/total, oov_total, total))


def main(argv):
    args = argparser().parse_args(argv[1:])
    vocab = load_word_vector_vocabulary(args.wordvecs, args)
    for fn in args.text:
        process(fn, vocab, args)
    return 0
    

if __name__ == '__main__':
    sys.exit(main(sys.argv))
