import collections.abc
import gzip


class TreebankNode(object):
    """Base class for all nodes in the treebank."""

    pass


class InternalTreebankNode(TreebankNode):
    """
    Represents an internal node in the treebank.

    Args:
        label (str): The label associated with the internal node.
        children (collections.abc.Sequence): A sequence of child nodes.

    Attributes:
        label (str): The label associated with the internal node.
        children (tuple): A tuple containing the child nodes.
    """

    def __init__(self, label, children):
        assert isinstance(label, str)
        self.label = label

        assert isinstance(children, collections.abc.Sequence)
        assert all(isinstance(child, TreebankNode) for child in children)
        assert children
        self.children = tuple(children)

    # Linearize the internal node and its children
    def linearize(self):
        return "({} {})".format(
            self.label, " ".join(child.linearize() for child in self.children)
        )

    # Generate leaves under the internal node
    def leaves(self):
        for child in self.children:
            yield from child.leaves()

    # Convert the internal node to InternalParseNode
    def convert(self, index=0, nocache=False):
        tree = self
        sublabels = [self.label]

        while len(tree.children) == 1 and isinstance(
            tree.children[0], InternalTreebankNode
        ):
            tree = tree.children[0]
            sublabels.append(tree.label)

        children = []
        for child in tree.children:
            children.append(child.convert(index=index))
            index = children[-1].right

        return InternalParseNode(tuple(sublabels), children, nocache=nocache)


class LeafTreebankNode(TreebankNode):
    """Represents a leaf node in the treebank."""

    def __init__(self, tag, word):
        assert isinstance(tag, str)
        self.tag = tag

        assert isinstance(word, str)
        self.word = word

    # Linearize the leaf node
    def linearize(self):
        return "({} {})".format(self.tag, self.word)

    # Generate the leaf node itself
    def leaves(self):
        yield self

    # Convert the leaf node to LeafParseNode
    def convert(self, index=0):
        return LeafParseNode(index, self.tag, self.word)


class ParseNode(object):
    """Base class for all parse nodes."""

    pass


class InternalParseNode(ParseNode):
    """
    Represents an internal node in the parse tree.

    Args:
        label (tuple): A tuple of labels associated with the internal node.
        children (collections.abc.Sequence): A sequence of child nodes.
        nocache (bool, optional): Whether to enable caching.

    Attributes:
        label (tuple): A tuple of labels associated with the internal node.
        children (tuple): A tuple containing the child nodes.
        left (int): Index of the leftmost leaf under the internal node.
        right (int): Index of the rightmost leaf under the internal node.
        nocache (bool): Whether caching is enabled.
    """

    def __init__(self, label, children, nocache=False):
        assert isinstance(label, tuple)
        assert all(isinstance(sublabel, str) for sublabel in label)
        assert label
        self.label = label

        assert isinstance(children, collections.abc.Sequence)
        assert all(isinstance(child, ParseNode) for child in children)
        assert children
        assert len(children) > 1 or isinstance(children[0], LeafParseNode)
        assert all(
            left.right == right.left for left, right in zip(children, children[1:])
        )
        self.children = tuple(children)

        self.left = children[0].left
        self.right = children[-1].right

        self.nocache = nocache

    # Generate leaves under the internal node
    def leaves(self):
        for child in self.children:
            yield from child.leaves()

    # Convert the internal parse node to InternalTreebankNode
    def convert(self):
        children = [child.convert() for child in self.children]
        tree = InternalTreebankNode(self.label[-1], children)
        for sublabel in reversed(self.label[:-1]):
            tree = InternalTreebankNode(sublabel, [tree])
        return tree

    # Find the smallest enclosing node for a given span
    def enclosing(self, left, right):
        assert self.left <= left < right <= self.right
        for child in self.children:
            if isinstance(child, LeafParseNode):
                continue
            if child.left <= left < right <= child.right:
                return child.enclosing(left, right)
        return self

    # Find the oracle label for a given span
    def oracle_label(self, left, right):
        enclosing = self.enclosing(left, right)
        if enclosing.left == left and enclosing.right == right:
            return enclosing.label
        return ()

    # Find the oracle splits for a given span
    def oracle_splits(self, left, right):
        return [
            child.left
            for child in self.enclosing(left, right).children
            if left < child.left < right
        ]


class LeafParseNode(ParseNode):
    """Represents a leaf node in the parse tree."""

    def __init__(self, index, tag, word):
        assert isinstance(index, int)
        assert index >= 0
        self.left = index
        self.right = index + 1

        assert isinstance(tag, str)
        self.tag = tag

        assert isinstance(word, str)
        self.word = word

    # Generate the leaf node itself
    def leaves(self):
        yield self

    # Convert the leaf parse node to LeafTreebankNode
    def convert(self):
        return LeafTreebankNode(self.tag, self.word)


def tree_from_str(treebank, strip_top=True, strip_spmrl_features=True):
    """
    Convert a treebank string to a tree.

    Args:
        treebank (str): The treebank string to be converted.
        strip_top (bool, optional): Whether to strip the top-level node.
        strip_spmrl_features (bool, optional): Whether to strip spmrl features.

    Returns:
        TreebankNode: The root node of the resulting tree.
    """
    if strip_spmrl_features:
        treebank = "".join(treebank.split("##")[::2])

    tokens = treebank.replace("(", " ( ").replace(")", " ) ").split()

    def helper(index):
        trees = []

        while index < len(tokens) and tokens[index] == "(":
            paren_count = 0
            while tokens[index] == "(":
                index += 1
                paren_count += 1

            label = tokens[index]
            index += 1

            if tokens[index] == "(":
                children, index = helper(index)
                trees.append(InternalTreebankNode(label, children))
            else:
                word = tokens[index]
                index += 1
                trees.append(LeafTreebankNode(label, word))

            while paren_count > 0:
                assert tokens[index] == ")"
                index += 1
                paren_count -= 1

        return trees, index

    trees, index = helper(0)
    assert index == len(tokens)

    if strip_top:
        for i, tree in enumerate(trees):
            if tree.label in ("TOP", "ROOT"):
                assert len(tree.children) == 1
                trees[i] = tree.children[0]

    assert len(trees) == 1

    return trees[0]


def load_trees(path, strip_top=True):
    """
    Load trees from a file.

    Args:
        path (str): The path to the file containing treebank data.
        strip_top (bool, optional): Whether to strip the top-level node.

    Returns:
        list: A list of tree root nodes.
    """

    # Read the content of the file
    with open(path) as infile:
        treebank = infile.read()

    # Tokenize the treebank content
    tokens = treebank.replace("(", " ( ").replace(")", " ) ").split()

    def helper(index):
        trees = []

        # Process each token until the end of input or closing parentheses
        while index < len(tokens) and tokens[index] == "(":
            paren_count = 0
            while tokens[index] == "(":
                index += 1
                paren_count += 1

            label = tokens[index]
            index += 1

            if tokens[index] == "(":
                # If next token is '(', recursively process children
                children, index = helper(index)
                trees.append(InternalTreebankNode(label, children))
            else:
                # If next token is a word, create a LeafTreebankNode
                word = tokens[index]
                index += 1
                trees.append(LeafTreebankNode(label, word))

            # Process closing parentheses
            while paren_count > 0:
                try:
                    assert tokens[index] == ")"
                except IndexError:
                    print(
                        tokens[index - 1],
                        tokens[index - 2],
                        tokens[index - 3],
                        tokens[index - 4],
                        tokens[index - 5],
                        tokens[index - 6],
                        tokens[index - 7],
                        tokens[index - 8],
                        tokens[index - 9],
                        tokens[index - 10],
                    )
                    raise KeyError
                except AssertionError:
                    print(
                        tokens[index - 1],
                        tokens[index - 2],
                        tokens[index - 3],
                        tokens[index - 4],
                        tokens[index - 5],
                        tokens[index - 6],
                        tokens[index - 7],
                        tokens[index - 8],
                        tokens[index - 9],
                        tokens[index - 10],
                    )
                    raise KeyError
                index += 1
                paren_count -= 1

        return trees, index

    # Use the helper function to parse the tokens into tree nodes
    trees, index = helper(0)
    assert index == len(tokens)

    # If strip_top is True, remove top-level nodes with 'TOP' or 'ROOT' labels
    if strip_top:
        for i, tree in enumerate(trees):
            if tree.label in ("TOP", "ROOT"):
                assert len(tree.children) == 1
                trees[i] = tree.children[0]

    return trees


def load_silver_trees_single(path):
    """
    Load silver trees from a file, one tree at a time.

    Args:
        path (str): The path to the file containing silver tree data.

    Yields:
        TreebankNode: A tree root node.
    """
    with gzip.open(path, mode="rt") as f:
        linenum = 0
        for line in f:
            linenum += 1
            tokens = line.replace("(", " ( ").replace(")", " ) ").split()

            def helper(index):
                trees = []

                while index < len(tokens) and tokens[index] == "(":
                    paren_count = 0
                    while tokens[index] == "(":
                        index += 1
                        paren_count += 1

                    label = tokens[index]
                    index += 1

                    if tokens[index] == "(":
                        children, index = helper(index)
                        trees.append(InternalTreebankNode(label, children))
                    else:
                        word = tokens[index]
                        index += 1
                        trees.append(LeafTreebankNode(label, word))

                    while paren_count > 0:
                        assert tokens[index] == ")"
                        index += 1
                        paren_count -= 1

                return trees, index

            trees, index = helper(0)
            assert index == len(tokens)

            assert len(trees) == 1
            tree = trees[0]

            # Strip the root S1 node
            assert tree.label == "S1"
            assert len(tree.children) == 1
            tree = tree.children[0]

            yield tree


def load_silver_trees(path, batch_size):
    """
    Load silver trees from a file in batches.

    Args:
        path (str): The path to the file containing silver tree data.
        batch_size (int): The size of each batch.

    Yields:
        list: A batch of tree root nodes.
    """
    batch = []
    for tree in load_silver_trees_single(path):
        batch.append(tree)
        if len(batch) == batch_size:
            yield batch
            batch = []
