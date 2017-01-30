import operator



class Node:
    def __init__(self, name, value, parentNode):
            self.name = name
            self.value = value
            self.parent = parentNode
            self.sibling = None
            self.children = {}
    def disp(self, level=1):
        print '_' * level, self.name, self.value
        for child in self.children.values():
            child.disp(level + 1)


class FP_tree():


    def __init__(self, database, sigma,frequent_items={}, base_path=None):
        self.database = database
        self.sigma = sigma
        self.unique_items = frequent_items
        self.sorted_unique_items = {}
        self.sorted_items = []
        self.header_table = {}
        self.ordered_transaction = []
        self.rootNode = Node("Null", 1, None)
        self.base_path = base_path


    def extract_unique_items(self):
        unique_items={}
        for row in self.database:
            row = list(set(row))
            for item in row:
                self.unique_items[item]=self.unique_items.get(item,0)+1


    def remove_items_less_than_sigma(self, sigma):
        for key, value in self.unique_items.items():
            if value < sigma:
                del self.unique_items[key]

    def create_ordered_dataset(self, database, frequent_item, base_path = None):
        for database_entry in database:
            output=[]
            for each in frequent_item:
                if base_path!=None:
                    if each in database_entry and set(base_path).issubset(set(database_entry)):
                        output.append(each)
                else:
                    if each in database_entry:
                        output.append(each)

            self.ordered_transaction.append(output)


    def sort_frequent_itemlist(self):
        sorted_list = sorted(self.unique_items.items(), reverse=True, key=operator.itemgetter(1))
        self.sorted_unique_items=sorted_list
        for each in sorted_list:
            self.header_table[each[0]] = self.header_table.get(each[0], [each[1], None])

        self.sorted_items = [x[0] for x in sorted_list]

    def addNodes(self, item, node):
        if len(item) > 0:
            if item[0] not in node.children.keys():
                new_node = Node(item[0], 1, node)
                node.children[item[0]] = new_node
                if self.header_table[item[0]][1] == None:
                    self.header_table[item[0]][1] = new_node
                else:
                    self.updateHeader(self.header_table[item[0]][1], new_node)
            else:
                node.children[item[0]].value+=1

            if len(item) > 1:
                self.addNodes(item[1:], node.children[item[0]])

    def updateHeader(self, nodeToTest, targetNode):  # this version does not use recursion
        while (nodeToTest.sibling != None):  # Do not use recursion to traverse a linked list!
            nodeToTest = nodeToTest.sibling
        nodeToTest.sibling = targetNode

    def create_tree(self):
        if len(self.unique_items.keys())==0 and self.base_path==None:
            self.extract_unique_items()
            self.remove_items_less_than_sigma(sigma=self.sigma)
            self.sort_frequent_itemlist()
        else:
            self.remove_items_less_than_sigma(sigma=self.sigma)
            self.sort_frequent_itemlist()
        self.create_ordered_dataset(database=database, frequent_item=self.sorted_items, base_path = self.base_path)
        for each_item in self.ordered_transaction:
            self.addNodes(each_item, self.rootNode)




class FP_growth():


    def __init__(self, database, sigma):
        self.database = database
        self.sigma = sigma
        self.unique_items = {}
        self.sorted_unique_items = {}
        self.sorted_items = []
        self.header_table = {}
        self.ordered_transaction = []
        self.rootNode = Node("Null", 1, None)


    def extract_unique_items(self):
        unique_items={}
        for row in self.database:
            row = list(set(row))
            for item in row:
                self.unique_items[item]=self.unique_items.get(item,0)+1


    def remove_items_less_than_sigma(self, sigma):
        for key, value in self.unique_items.items():
            if value < sigma:
                del self.unique_items[key]

    def sort_frequent_itemlist(self):
        sorted_list = sorted(self.unique_items.items(), reverse=True, key=operator.itemgetter(1))
        self.sorted_unique_items=sorted_list
        for each in sorted_list:
            self.header_table[each[0]] = self.header_table.get(each[0], [each[1], None])

        self.sorted_items = [x[0] for x in sorted_list]


    def get_patterns(self):
        self.extract_unique_items()
        self.remove_items_less_than_sigma(sigma=self.sigma)
        self.sort_frequent_itemlist()




def read_database(input_file):
    database = []
    with open(input_file) as f:
        for line in f:
            l= map(int, line.strip().split(" "))
            database.append(l)
    return database


#{32: 4309, 38: 4165, 39: 13509, 41: 6837, 48: 11114, 65: 1139}

database = read_database("./retail_25k.dat")
#database=[['a','b'],['b','c','d'],['a','c','d','e'],['a','d','e'],['a','b','c'],['a','b','c','d'],['a'],['a','b','c'],['a','b','d'],['b','c','e']]
#database=[[1,2],[2,3,4],[1,3,4,5],[1,4,5],[1,2,3],[1,2,3,4],[1],[1,2,3],[1,2,4],[2,3,5]]
#database = [['E','A','D','B'],['D','A','C','E','B'],['C','A','B','E'],['B','A','D'],['D'],['D','B'],['A','D','E'],['B','C']]




# tree.rootNode.disp()

base = []
from itertools import combinations
def is_single_branch(rootnode):

    while(len(rootnode.children.keys())!=0):
        if len(rootnode.children.keys())>1:
            return False
        else:
            rootnode=rootnode.children[rootnode.children.keys()[0]]
    return True




def fp_growth( tree,sigma, base=[('1',2)],pat={}, itemset_size = 3):
    if is_single_branch(tree.rootNode):
        pat[str(base[0][0])]=base[0][1]
        items_keys = tree.unique_items.keys()
        for i in range(1, len(items_keys)+1):
            for pattern in combinations(items_keys, i):
                if len(pattern)>0:
                    candidate_pattern = list(pattern)+[base[0][0]]
                    string_pattern = "|".join(map(str,candidate_pattern))
                    pat[string_pattern]=min([tree.unique_items[item] for item in pattern])

        return pat

    else:
        for each in [a for a in reversed(tree.sorted_items)]:
            leaf = tree.header_table[each][1]
            output = []
            while leaf!=None:
                temp = leaf.parent
                path = []
                while(temp.name!='Null'):
                    path.append(temp.name)
                    temp=temp.parent
                output.append((leaf.value,[a for a in reversed(path)]))
                leaf=leaf.sibling

            db = []
            for every in output:
                for i in range(0, every[0]):
                    db.append(every[1])
            fp_growth_obj = FP_growth(db, sigma)
            fp_growth_obj.get_patterns()
            conditional_tree = FP_tree(database=database,sigma=sigma,frequent_items=fp_growth_obj.unique_items, base_path = [each])
            conditional_tree.create_tree()
            # print "\n\n-----------TREE for %s"%each
            # conditional_tree.rootNode.disp()
            if len(base)>0:
                patterns = fp_growth(conditional_tree,sigma,[(str(each)+'|'+str(base[0][0]), tree.unique_items[each])], pat=pat)

            else:
                pat[str(each)]=tree.unique_items[each]
                patterns = fp_growth(conditional_tree, sigma, [(each, tree.unique_items[each])], pat=pat)

        return patterns

import time

for sigma in reversed([4,10,50,100,200,300,400,500,1000]):
    min_length=2
    start_time = time.time()
    tree = FP_tree(database, sigma)
    tree.create_tree()
    d = fp_growth(tree,sigma,[])
    print("%s--- %s seconds ---" % (sigma, time.time() - start_time))
    sorted_list = sorted(d.items(), reverse=True, key=operator.itemgetter(1))
    for each in sorted_list:
        if len(each[0].strip().split("|"))>min_length:
            print "Item : %s ----- Count : %d"%("("+", ".join(each[0].strip().split("|"))+")", each[1])


