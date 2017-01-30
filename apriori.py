temsets of size k given the item list
from itertools import combinations
from copy import deepcopy
from fp_growth import find_frequent_itemsets

def read_database(input_file):
    database = []
    counter = 0
    with open(input_file) as f:
        for line in f:
            database.append(map(int, line.strip().split(" ")))
    return database

def total_unique():
    database = []
    counter = 0
    with open("./retail_25k.dat") as f:
        for line in f:
            database.append(map(int, line.strip().split(" ")))
    flat = [item for sublist in database for item in sublist]
    print len(flat)
    items = list(set(flat))
    for i in combinations(items, 3):
        print i


def remove_non_frequent(candidate, sup):
    frequent_candidate = deepcopy(candidate)
    for key, value in frequent_candidate.items():
        if value < sup:
            del frequent_candidate[key]
    return frequent_candidate


def get_k_combinations(items, k):
    if len(items) > 0 and type(items[0]) == type([]):
        flat = [item for sublist in items for item in sublist]
    items = list(set(flat))

    output = []
    print len(items)
    for i in combinations(items, k):
        output.append(list(i))
    print len(output)
    if len(output) == 0:
        return []
    else:
        return output


def search_in_database(output):
    current_candidate = {}
    for row in output:
        row = set(row)
        for item in output:
            if set(item).issubset(row):
                item_key = "|".join(map(str, item))
                if item_key not in current_candidate.keys():
                    current_candidate[item_key] = 1
                else:
                    current_candidate[item_key] += 1

    return current_candidate


def get_items_from_current_frequent(current_frequent):
    itemlist = []
    for each in current_frequent.keys():
        itemlist.append(each.split("|"))
    return [[int(float(j)) for j in i] for i in itemlist]


def prune_list(current_itemlist, previous_itemlist):
    final_itemlist = deepcopy(current_itemlist)
    for each in final_itemlist:
        out = get_k_combinations(each, len(each) - 1)
        for every in out:
            if every not in previous_itemlist:
                final_itemlist.remove(each)
                break
    return final_itemlist

def main():
    sup = 4
    print "reading database"
    step0 = read_database("./retail_25k.dat")
    frequent_items = []
    item_set_size = 3
    counter = item_set_size
    print "starting processing for counter = %f" % counter

    while (counter == item_set_size or (len(step2.keys()) > 0 and len(step3.keys()) > 0)):
        step1 = get_k_combinations(step0, counter)
        step2 = search_in_database(step1)
        step3 = remove_non_frequent(step2, sup)
        step4 = get_items_from_current_frequent(step3)
        frequent_items.append(step4)
        print " Processed iteration %d found total %d itemsets"%(counter, len(step4))
        step5 = get_k_combinations(step4, counter + 1)
        step0 = prune_list(step5, step4)
        counter += 1

    for each in [k for sublist in frequent_items for k in sublist]:
        print each

if __name__ == '__main__':
    main()
