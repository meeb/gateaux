#!/usr/bin/env python3
'''
    This is the example application taken from the FoundationDB documentation here:
    https://apple.github.io/foundationdb/class-scheduling.html
    and re-made using gateaux structures.

    This is functionally exactly the same, the only difference being the strucutres are
    obvious and explicit with all types being strictly enforced.
'''


import itertools
import traceback
import fdb
import fdb.tuple
import gateaux


fdb.api_version(620)


####################################
##         Structures             ##
####################################


class ClassAvailability(gateaux.Structure):
    '''Stores the number of available seats for a class'''
    key = (
        gateaux.StringField(name='name', help_text='Name of the class'),
    )
    value = (
        gateaux.IntegerField(name='seats', help_text='Number of available seats'),
    )


class Attending(gateaux.Structure):
    '''Stores which student is attending which class'''
    key = (
        gateaux.StringField(name='student', help_text='Name of the student'),
        gateaux.StringField(name='class', help_text='Class the student is attending')
    )
    value = ()


####################################
##        Initialization          ##
####################################


db = fdb.open()
db.options.set_transaction_timeout(60000)  # 60,000 ms = 1 minute
availability_dir = fdb.directory.create_or_open(db, ('scheduling', 'availability'))
attending_dir = fdb.directory.create_or_open(db, ('scheduling', 'attending'))
availability = ClassAvailability(availability_dir)
attending = Attending(attending_dir)


@fdb.transactional
def add_class(tr, c):
    tr[availability.pack_key((c,))] = availability.pack_value((100,))


# Generate 1,620 classes like '9:00 chem for dummies'
levels = ['intro', 'for dummies', 'remedial', '101',
          '201', '301', 'mastery', 'lab', 'seminar']
types = ['chem', 'bio', 'cs', 'geometry', 'calc',
         'alg', 'film', 'music', 'art', 'dance']
times = [str(h) + ':00' for h in range(2, 20)]
class_combos = itertools.product(times, types, levels)
class_names = [' '.join(tup) for tup in class_combos]


@fdb.transactional
def init(tr):
    # Clear the directories
    del tr[availability_dir.range(())]
    del tr[attending_dir.range(())]
    # Create classes
    for class_name in class_names:
        add_class(tr, class_name)


####################################
##  Class Scheduling Functions    ##
####################################


@fdb.transactional
def available_classes(tr):
    return [availability.unpack_key(k)[0] for k, v in tr[availability_dir.range(())]
            if availability.unpack_value(v)[0]]


@fdb.transactional
def signup(tr, s, c):
    key = attending.pack_key((s, c))
    if tr[key].present():
        return  # already signed up
    seats_left = tr[availability.pack_key((c,))][0]
    if not seats_left:
        raise Exception('No remaining seats')
    student_classes = tr[attending_dir.range((s,))]
    if len(list(student_classes)) == 5:
        raise Exception('Too many classes')
    tr[availability.pack_key((c,))] = availability.pack_value((seats_left - 1,))
    tr[key] = b''


@fdb.transactional
def drop(tr, s, c):
    key = attending.pack_key((s, c))
    if not tr[key].present():
        return  # not taking this class
    seats_left = tr[availability.pack_key((c,))][0]
    tr[availability.pack_key((c,))] = availability.pack_value((seats_left + 1,))
    del tr[key]


@fdb.transactional
def switch(tr, s, old_c, new_c):
    drop(tr, s, old_c)
    signup(tr, s, new_c)


####################################
##           Testing              ##
####################################


import random
import threading


def indecisive_student(i, ops):
    student_ID = 's{:d}'.format(i)
    all_classes = class_names
    my_classes = []

    for i in range(ops):
        class_count = len(my_classes)
        moods = []
        if class_count: moods.extend(['drop', 'switch'])
        if class_count < 5: moods.append('add')
        mood = random.choice(moods)

        try:
            if not all_classes:
                all_classes = available_classes(db)
            if mood == 'add':
                c = random.choice(all_classes)
                signup(db, student_ID, c)
                my_classes.append(c)
            elif mood == 'drop':
                c = random.choice(my_classes)
                drop(db, student_ID, c)
                my_classes.remove(c)
            elif mood == 'switch':
                old_c = random.choice(my_classes)
                new_c = random.choice(all_classes)
                switch(db, student_ID, old_c, new_c)
                my_classes.remove(old_c)
                my_classes.append(new_c)
        except Exception as e:
            traceback.print_exc()
            print('Need to recheck available classes.')
            all_classes = []


def run(students, ops_per_student):
    threads = [
        threading.Thread(target=indecisive_student, args=(i, ops_per_student))
        for i in range(students)]
    for thr in threads: thr.start()
    for thr in threads: thr.join()
    print('Ran {} transactions'.format(students * ops_per_student))


if __name__ == '__main__':
    init(db)
    print('initialized')
    run(10, 100)
