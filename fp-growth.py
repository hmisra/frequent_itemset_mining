import operator
from copy import deepcopy
from itertools import combinations
import time

###################################################################
#This class represents a node in a FP-Tree
###################################################################

class Node:

    ###################################################################
    #__init__: constructor
    #@name: name of the node
    #@value: Value of the node
    #@parent: Parent node of the current node
    #@sibling: Sibling node of the current node
    #@children: Childrent nodes of the current node
    ###################################################################

    def __init__(self, name, value, parentNode):
            self.name = name
            self.value = value
            self.parent = parentNode
            self.sibling = None
            self.children = {}

    #####################################
    #disp:function to display the tree
    #####################################

    def disp(self, level=1):
        print '_' * level, self.name, self.value
        for child in self.children.values():
            child.disp(level + 1)




###################################################################
#
#FP_tree: class representing an FP_tree
#
###################################################################

class FP_tree():

    #####################################################################################################
    #__init__: constructor
    #@database: The database used to generate the FP tree
    #@sigma: the minimum count of items
    #@frequent_items: a dictionary of frequent items and their counts, used when generating
    #                 conditional FP_tree from conditional patterns
    #@base_path: suffix path before the conditional FP_tree
    #####################################################################################################


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

    #####################################################################################################
    #extract_unique_items: gets unique items and their counts from database
    #####################################################################################################

    def extract_unique_items(self):
        unique_items={}
        for row in self.database:
            row = list(set(row))
            for item in row:
                self.unique_items[item]=self.unique_items.get(item,0)+1


    ###################################################################
    #remove_items_less_than_sigma: removes items less than sigma
    ###################################################################


    def remove_items_less_than_sigma(self, sigma):
        for key, value in self.unique_items.items():
            if value < sigma:
                del self.unique_items[key]



    #####################################################################################################
    #create_ordered_dataset: transform database in order of items in frequent item list
    #####################################################################################################

    def create_ordered_dataset(self, database, frequent_item, base_path = None):
        for database_entry in database:
            output=[]
            for each in frequent_item:
                # do not consider rows in database which are in basepath
                if base_path!=None:
                    if each in database_entry and set(base_path).issubset(set(database_entry)):
                        output.append(each)
                else:
                    if each in database_entry:
                        output.append(each)

            self.ordered_transaction.append(output)



    #####################################################################################################
    #sort_frequent_itemlist: sort the frequent item list by order of decreasing counts
    #####################################################################################################

    def sort_frequent_itemlist(self):
        sorted_list = sorted(self.unique_items.items(), reverse=True, key=operator.itemgetter(1))
        self.sorted_unique_items=sorted_list
        for each in sorted_list:
            self.header_table[each[0]] = self.header_table.get(each[0], [each[1], None])

        self.sorted_items = [x[0] for x in sorted_list]



    ###################################################################
    #addNodes: Add a node to the tree
    #          If required update the header table
    ###################################################################

    def addNodes(self, item, node):
        if len(item) > 0:
            # check if current item is not in the children
            if item[0] not in node.children.keys():
                new_node = Node(item[0], 1, node)

                #add it to childrent
                node.children[item[0]] = new_node

                #if required create/update the header table
                if self.header_table[item[0]][1] == None:
                    self.header_table[item[0]][1] = new_node
                else:
                    self.updateHeader(self.header_table[item[0]][1], new_node)
            #if it is present in childrens of current node, increment the count
            else:
                node.children[item[0]].value+=1
            #recursively add the nodes
            if len(item) > 1:
                self.addNodes(item[1:], node.children[item[0]])



    #####################################################################################################
    #updateHeader: this table maintains the header table
    #              to keep track of each item in the tree by maintaining
    #              a linked list.
    #####################################################################################################

    def updateHeader(self, nodeToTest, targetNode):  # this version does not use recursion
        while (nodeToTest.sibling != None):  # Do not use recursion to traverse a linked list!
            nodeToTest = nodeToTest.sibling
        nodeToTest.sibling = targetNode




    #####################################################################################################
    #create_tree: this function creates the FP_tree with help of all the functions above
    #####################################################################################################

    def create_tree(self):
        # If this is the inital tree
        #  - extract unique items
        #  - remove unique items
        #  - sort frequent items

        if len(self.unique_items.keys())==0 and self.base_path==None:
            self.extract_unique_items()
            self.remove_items_less_than_sigma(sigma=self.sigma)
            self.sort_frequent_itemlist()

        # else do not extract unique items because the purpose is just to create conditional FP tree from the given priority list
        #  - remove unique items
        #  - sort frequent items

        else:
            self.remove_items_less_than_sigma(sigma=self.sigma)
            self.sort_frequent_itemlist()

        #create ordered dataset

        self.create_ordered_dataset(database=deepcopy(self.database), frequent_item=self.sorted_items, base_path = self.base_path)

        # iterate over each transaction in database and construct tree from items in the transaction

        for each_item in self.ordered_transaction:
            self.addNodes(each_item, self.rootNode)





###################################################################
#This class contains functions to create conditional patterns
###################################################################

class F_list():

    ###################################################################
    #__init__: constructor
    #@database: The database used to generate the FP tree
    #@sigma: the minimum count of items
    ###################################################################


    def __init__(self, database, sigma):
        self.database = database
        self.sigma = sigma
        self.unique_items = {}
        self.sorted_unique_items = {}
        self.sorted_items = []
        self.header_table = {}
        self.ordered_transaction = []
        self.rootNode = Node("Null", 1, None)



    #####################################################################################################
    # extract_unique_items: gets unique items and their counts from database
    #####################################################################################################

    def extract_unique_items(self):
        unique_items={}
        for row in self.database:
            row = list(set(row))
            for item in row:
                self.unique_items[item]=self.unique_items.get(item,0)+1



    ###################################################################
    # remove_items_less_than_sigma: removes items less than sigma
    ###################################################################

    def remove_items_less_than_sigma(self, sigma):
        for key, value in self.unique_items.items():
            if value < sigma:
                del self.unique_items[key]



    #####################################################################################################
    # sort_frequent_itemlist: sort the frequent item list by order of decreasing counts
    #####################################################################################################

    def sort_frequent_itemlist(self):
        sorted_list = sorted(self.unique_items.items(), reverse=True, key=operator.itemgetter(1))
        self.sorted_unique_items=sorted_list
        for each in sorted_list:
            self.header_table[each[0]] = self.header_table.get(each[0], [each[1], None])

        self.sorted_items = [x[0] for x in sorted_list]



    ##########################################################################
    #get_patterns: this function gets the conditional patterns from the F-List
    #               - extract unique items from the database
    #               - remove unique items with count less than sigma
    #               - sort the unique items list by order of their count
    ###########################################################################

    def get_f_list(self):
        self.extract_unique_items()
        self.remove_items_less_than_sigma(sigma=self.sigma)
        self.sort_frequent_itemlist()




###########################################################################
# is_single_branch: function to check if the tree is a single branch tree
###########################################################################

def is_single_branch(rootnode):
    while(len(rootnode.children.keys())!=0):
        if len(rootnode.children.keys())>1:
            return False
        else:
            rootnode=rootnode.children[rootnode.children.keys()[0]]
    return True




##################################################################
# fp_growth: function to mine patterns from FP-tree
##################################################################

def fp_growth( database, tree,sigma, base,pat={}):
    # Check if the tree is single branch tree
    if is_single_branch(tree.rootNode):
        #if yes store combinations of patterns in a dictionary
        pat[str(base[0][0])]=base[0][1]
        items_keys = tree.unique_items.keys()
        # for each item in the branch of the tree generate patterns of lengths 1 to total number of items.
        for i in range(1, len(items_keys)+1):
            for pattern in combinations(items_keys, i):
                if len(pattern)>0:
                    #append base pattern to the current pattern
                    candidate_pattern = list(pattern)+[base[0][0]]
                    string_pattern = "|".join(map(str,candidate_pattern))
                    # add minimum count for this item as count of pattern+base pattern
                    pat[string_pattern]=min([tree.unique_items[item] for item in pattern])
        # return the patterns
        return pat
    #if the tree is not a single branch tree
    else:
        # start from all the unique items the current tree has
        for each in [a for a in reversed(tree.sorted_items)]:
            leaf = tree.header_table[each][1]
            output = []
            # construct a prefix base FP - tree, i.e a tree that ends in the item in consideration, using the details in header table


            # create conditional patterns
            while leaf!=None:
                temp = leaf.parent
                path = []
                while(temp.name!='Null'):
                    path.append(temp.name)
                    temp=temp.parent
                output.append((leaf.value,[a for a in reversed(path)]))
                leaf=leaf.sibling

            db = []
            # add conditional patterns in database for each count of item in consideration
            for every in output:
                for i in range(0, every[0]):
                    db.append(every[1])


            # get the F-list from the conditional pattern
            fp_growth_obj = F_list(db, sigma)
            fp_growth_obj.get_f_list()


            # create a conditional FP-tree
            conditional_tree = FP_tree(database=deepcopy(database),sigma=sigma,frequent_items=fp_growth_obj.unique_items, base_path = [each])
            conditional_tree.create_tree()


            # print "\n\n-----------TREE for %s"%each
            # conditional_tree.rootNode.disp()



            #recursively call the FP - growth on conditional FP- tree
            if len(base)>0:
                patterns = fp_growth(deepcopy(database), conditional_tree,sigma,[(str(each)+'|'+str(base[0][0]), tree.unique_items[each])], pat=pat)
            else:
                pat[str(each)]=tree.unique_items[each]
                patterns = fp_growth(deepcopy(database), conditional_tree, sigma, [(each, tree.unique_items[each])], pat=pat)

        return patterns



##################################################################
# read_database: function to read the database file
##################################################################
def read_database(input_file):

    database = []
    with open(input_file) as f:
        for line in f:
            l= map(int, line.strip().split(" "))
            database.append(l)
    return database



##################################################################
# main: main function
##################################################################
def main():
    #database = [['E','A','D','B'],['D','A','C','E','B'],['C','A','B','E'],['B','A','D'],['D'],['D','B'],['A','D','E'],['B','C']]
    #database=[['a','b'],['b','c','d'],['a','c','d','e'],['a','d','e'],['a','b','c'],['a','b','c','d'],['a'],['a','b','c'],['a','b','d'],['b','c','e']]
    #database=[[1,2],[2,3,4],[1,3,4,5],[1,4,5],[1,2,3],[1,2,3,4],[1],[1,2,3],[1,2,4],[2,3,5]]
    # read the database
    database = read_database("./retail_25k.dat")
    # minimum count of items in frequent item set
    sigma=4
    # minimum length of items in frequent item set
    min_length=3

    start_time = time.time()
    # create a FP-tree
    tree = FP_tree(deepcopy(database), sigma)
    tree.create_tree()
    # execute FP growth on FP-tree
    d = fp_growth(deepcopy(database),tree,sigma,[])
    # sort the resulting patterns base on occurrence of each pattern in decreasing order
    sorted_list = sorted(d.items(), reverse=True, key=operator.itemgetter(1))
    # print the results if the pattern is at-least of minimum length
    for each in sorted_list:
        if len(each[0].strip().split("|"))>=min_length:
            print str(len(each[0].strip().split("|")))+", "+str(each[1])+", "+", ".join(each[0].strip().split("|"))



if __name__ == '__main__':
    main()
