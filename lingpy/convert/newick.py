# author   : Johann-Mattis List
# email    : mattis.list@gmail.com
# created  : 2013-04-02 07:01
# modified : 2013-07-10 12:10
"""
Functions for tree calculations and working with Newick files.
"""

__author__="Johann-Mattis List"
__date__="2013-07-10"

# external
import xml.dom.minidom as minidom
import codecs
from collections import deque

# internal
from ..settings import rcParams
from ..thirdparty import cogent as cg
try:
    from ..algorithm.cython import cluster
except:
    from ..algorithm.cython import _cluster as cluster

def xml2nwk(
        infile,
        filename = ''
        ):
    """
    Convert xml-based MultiTree format to Newick-format.
    """
    
    # parse the xml-file
    document = {}

    # get the document
    document['document'] = minidom.parse(infile)
    
    # get the hash
    document['hash'] = document['document'].getElementsByTagName('hash')[0]
    
    # get the tree
    document['tree'] = document['hash'].getElementsByTagName('tree')[0]
    
    # get the root
    document['root'] = document['tree'].getElementsByTagName('root')[0]
    

    # now start iteration
    nwk = {0:[]}
    queue = [(document['root'],0)]
    taxa = []
    while queue:
        
        root,idx = queue.pop()
        
        max_idx = max([k for k in nwk if type(k) == int])
    
        try:
            nwk[idx]
        except:
            nwk[idx] = []
    
        # get the children
        children = [c for c in root.childNodes if c.nodeName == 'children']
    
        # get the childs
        childs = [c for c in children[0].childNodes if c.nodeName == 'child'] 
    
        #print("Idx {0} has {1} childs".format(idx,len(childs)))
        
        if childs:
            # iterate over childs
            for i,child in enumerate(childs):
                
                queue += [(child,max_idx+i+1)]
                nwk[idx] += [max_idx+i+1]
                #print("\tAdded {1} to {0}.".format(idx,max_idx+i+1))
    
        else:
            name = [c for c in root.childNodes if c.nodeName == 'pri-name'][0]
            name = name.childNodes[0].data
            
            nwk[idx] = [name]
            taxa.append(name)
    
    # now that a dictionary representation of the tree has been created,
    # convert everything to newick

    # first, create a specific newick-dictionary
    newick = {}

    for i in range(len(nwk)):
        
        #create format-string for children
        children = ['{{x_{0}}}'.format(c) for c in nwk[i]]
    
        # create dictionary to replace previous format string
        if len(children) > 1:
            newick['x_'+str(i)] = '('+','.join(children)+')'
        else:
            newick['x_'+str(i)] = children[0]
    
    # add the taxa
    for taxon in taxa:
        newick['x_'+str(taxon)] = taxon
    
    # create the newick-string
    newick_string = "{x_0};"
    newick_check = newick_string
    
    # start conversion
    i = 0
    while True:
        
        newick_string = newick_string.format(**newick)
        if newick_check == newick_string:
            break
        else:
            newick_check = newick_string
    
    if not filename:
        return newick_string
    else:
        f = codecs.open(filename+'.nwk','w','utf-8')
        f.write(newick_string)
        f.close()
        if rcParams['verbose']: print(rcParams['M_file_written'].format(filename,'nwk'))
        return

def matrix2tree(
        matrix,
        taxa,
        tree_calc = "neighbor",
        distances = True,
        filename = ''
        ):
    """
    Calculate a tree of a given distance matrix.
    """
    
    if tree_calc == 'upgma':
        algorithm = cluster.upgma
    elif tree_calc == 'neighbor':
        algorithm = cluster.neighbor

    newick = algorithm(matrix,taxa,distances)

    tree = cg.LoadTree(treestring=newick)
    
    if not filename:
        return tree
    else:
        out = codecs.open(filename+'.nwk','w','utf-8')
        out.write(str(tree))
        out.close()
        if rcParams['verbose']: print(rcParams['M_file_written'].format(filename,'nwk'))

def nwk2guidetree(
                  newick
                  ):
    """
    Build a tree matrix for a guide tree given in Newick format.
    Input is a binary tree with zero-based integer names at the leaves.
    """
    #assumption: a binary tree with integer names starting with 0 at the leaves
    tree = cg.LoadTree(treestring=newick)
    nodeIndex = {}
    nextIdx = len(tree.tips())
    #generate virtual cluster IDs for the tree nodes, store them in nodeIndex
    for node in tree.postorder():
        if not node.isTip():
            nodeIndex[node] = nextIdx
            nextIdx += 1
        else:
            nodeIndex[node] = int(node.Name)
    #construct tree matrix by another postorder traversal
    tree_matrix = []
    queue = deque(tree.postorder())
    while len(queue) > 0:
        curNode = queue.popleft()
        if not curNode.isTip():
            leftChild = curNode.Children[0]
            rightChild = curNode.Children[1]
            tree_matrix.append([nodeIndex[leftChild],nodeIndex[rightChild],0.5,0.5])
    return tree_matrix

def selectNodes(tree, selIndices):
    selNodes = []
    for leaf in tree.tips():
        if int(leaf.Name) in selIndices:
            selNodes.append(leaf)
    return selNodes

def treePath(node):
    path = [node]
    while not node.isRoot():
        node = node.Parent
        path.insert(0,node)
    return path

def constructSubtree(paths,index,curNode,indexMap):
    #create a map [node -> all paths containing that node at index position]
    partition = {}
    for node in {path[index] for path in paths}:
        partition[node] = [path for path in paths if path[index] == node]
    #partition = {(node,[path for path in paths if path[index] == node]) for node in {path[index] for path in paths}}
    if len(partition) == 1:
        #no split, we simply go on to the next index in paths
        constructSubtree(paths,index + 1,curNode,indexMap)
    else:
        #split according to the partition, creating a new node where necessary
        for node in partition.keys():
            if len(partition[node]) == 1:
                #we have arrived at a leaf (or a unary branch above it), copy the leaf
                newLeafName = str(indexMap[int(partition[node][0][-1].Name)]) 
                newLeaf = cg.tree.TreeNode(Name=newLeafName)
                newLeaf.orig = partition[node][0][-1]
                curNode.Children.append(newLeaf)
                newLeaf.Parent = curNode
            else:               
                newNode = cg.tree.TreeNode()
                newNode.orig = node
                curNode.Children.append(newNode)
                newNode.Parent = curNode
                constructSubtree(partition[node],index + 1,newNode,indexMap)         

def subGuideTree(tree,selIndices):
    selNodes = selectNodes(tree,selIndices)
    indexMap = dict(zip(selIndices,range(0,len(selIndices))))
    paths = [treePath(node) for node in selNodes]
    #print str(paths)
    subtree = cg.tree.TreeNode()
    subtree.orig = tree.root()
    constructSubtree(paths,1,subtree,indexMap)
    return subtree