import sys
import os
import re
import pprint

# The following code for regex pattern is modified by 'Rizu Jain'

# Regex patterns to match email addresses
my_first_pat_email = '([\w\.\-\+]+)([\s]*)(@|\sat\s|\sWHERE\s|&#x40;)([\s]*)(([a-zA-Z0-9\-]+(\.|\sdot\s|\sDOM\s|\;))+)([\w\-]+)'
my_obfuscate_pat_email = '(obfuscate)\(\'(\w+).edu\'\,\'(\w+)\'\)'

# Regex patterns to match phone numbers
my_first_pat_phone = '\(?(\d{3})\)?[- ]?(\d{3})[- ](\d{4})\D+'
my_second_pat_phone = '(\d{3})&thinsp;(\d{3})&thinsp;(\d{4})\D+'


# The following code to parse the regex pattern is modified by 'Rizu Jain'

""" 
TODO
This function takes in a filename along with the file object (actually
a StringIO object) and
scans its contents against regex patterns. It returns a list of
(filename, type, value) tuples where type is either an 'e' or a 'p'
for e-mail or phone, and value is the formatted phone number or e-mail.
The canonical formats are:
     (name, 'p', '###-###-#####')
     (name, 'e', 'someone@something')
If the numbers you submit are formatted differently they will not
match the gold answers

NOTE: ***don't change this interface***

NOTE: You shouldn't need to worry about this, but just so you know, the
'f' parameter below will be of type StringIO. So, make
sure you check the StringIO interface if you do anything really tricky,
though StringIO should support most everything.
"""


def process_file(name, f):
    # note that debug info should be printed to stderr
    # sys.stderr.write('[process_file]\tprocessing file: %s\n' % (path))
    res = []
    for line in f:
        # Match regex for Email Addresses
        matches = re.findall(my_first_pat_email, line)
        matches.extend(re.findall(my_obfuscate_pat_email, line))
        for m in matches:

            # To handle the special case where obfuscate functions are used.
            # If the line matches this string, give inputs from the inverted
            # colons inside the brackets for email first part and the domain.
            if (m[0] == 'obfuscate'):
                email = '%s@%s.edu' % (m[2], m[1])
            else:
                # General Case to parse the email IDs.
                email = '%s@%s%s' % (m[0].replace('-',
                                                  ''),
                                     m[4].replace('-',
                                                  '').replace(';',
                                                              '.').replace(' dot ',
                                                                           '.').replace(' DOM ',
                                                                                        '.'),
                                     m[-1].replace('-',
                                                   ''))

            res.append((name, 'e', email))

        # Match regex for phone numbers
        matches = re.findall(my_first_pat_phone, line)
        matches.extend(re.findall(my_second_pat_phone, line))
        for m in matches:
            # Only print in xxx-xxx-xxxx format.
            phone = '%s-%s-%s' % m
            res.append((name, 'p', phone))

    return res

"""
You should not need to edit this function, nor should you alter
its interface
"""
def process_dir(data_path):
    # get candidates
    guess_list = []
    for fname in os.listdir(data_path):
        if fname[0] == '.':
            continue
        path = os.path.join(data_path,fname)
        f = open(path,'r')
        f_guesses = process_file(fname, f)
        guess_list.extend(f_guesses)
    return guess_list

"""
You should not need to edit this function.
Given a path to a tsv file of gold e-mails and phone numbers
this function returns a list of tuples of the canonical form:
(filename, type, value)
"""
def get_gold(gold_path):
    # get gold answers
    gold_list = []
    f_gold = open(gold_path,'r')
    for line in f_gold:
        gold_list.append(tuple(line.strip().split('\t')))
    return gold_list

"""
You should not need to edit this function.
Given a list of guessed contacts and gold contacts, this function
computes the intersection and set differences, to compute the true
positives, false positives and false negatives.  Importantly, it
converts all of the values to lower case before comparing
"""
def score(guess_list, gold_list):
    guess_list = [(fname, _type, value.lower()) for (fname, _type, value) in guess_list]
    gold_list = [(fname, _type, value.lower()) for (fname, _type, value) in gold_list]
    guess_set = set(guess_list)
    gold_set = set(gold_list)

    tp = guess_set.intersection(gold_set)
    fp = guess_set - gold_set
    fn = gold_set - guess_set

    pp = pprint.PrettyPrinter()
    #print 'Guesses (%d): ' % len(guess_set)
    #pp.pprint(guess_set)
    #print 'Gold (%d): ' % len(gold_set)
    #pp.pprint(gold_set)
    print 'True Positives (%d): ' % len(tp)
    pp.pprint(tp)
    print 'False Positives (%d): ' % len(fp)
    pp.pprint(fp)
    print 'False Negatives (%d): ' % len(fn)
    pp.pprint(fn)
    print 'Summary: tp=%d, fp=%d, fn=%d' % (len(tp),len(fp),len(fn))

"""
You should not need to edit this function.
It takes in the string path to the data directory and the
gold file
"""
def main(data_path, gold_path):
    guess_list = process_dir(data_path)
    gold_list =  get_gold(gold_path)
    score(guess_list, gold_list)

"""
commandline interface takes a directory name and gold file.
It then processes each file within that directory and extracts any
matching e-mails or phone numbers and compares them to the gold file
"""
if __name__ == '__main__':
    if (len(sys.argv) != 3):
        print 'usage:\tSpamLord.py <data_dir> <gold_file>'
        sys.exit(0)
    main(sys.argv[1],sys.argv[2])
