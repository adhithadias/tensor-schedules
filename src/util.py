import itertools

# ['j', ['k'], ['m', 'l', 'k']]
def get_idxes_in_config(input_idx_order):
    indices = set()
    for elem in input_idx_order:
        if type(elem) == list:
            indices |= get_idxes_in_config(elem)
        else:
            indices.add(elem)
    return indices

def get_input_idx_list(expr: list, tensor_accesses: dict):
    """
    Arguments:
        expr: list of tensor accesses
        tensor_accesses: dictionary of tensors with corresponding tensor accesses
    """
    idx_set = set()
    for tensor in expr:
        assert type(tensor) == str
        idxes = tensor_accesses[tensor]
        assert type(idxes) == list
        for idx in idxes:
            assert type(idx) == str
            idx_set.add(idx)
         # print(idxes)
    # print('indices set:', idx_set)
    idx_set = list(idx_set)
    # print('indices list:', idx_set)
    return idx_set

def append_list_to_list_of_lists(l1: list, l2: list):
    for l in l1:
        assert type(l) == list
        l.extend(l2)
    return l1

def copy_and_insert(l: list, pos: int, new_obj):
    nl = []
    nl.extend(l)
    nl.insert(pos, new_obj)
    return nl

def get_all_combinations(l1: list, l2: list):
    queue = [l2]
    for idx in l1:
        new_queue = []
        while (len(queue) != 0):
            # print(queue)
            elem = queue.pop(0)
            # print(elem)
            for i in range(len(elem)+1):
                ln = copy_and_insert(elem, i, idx)
                # print(ln)
                new_queue.append(ln)
        queue = new_queue
    return queue

def get_permutations_of_idx_list(idx_list: list):
    return list(itertools.permutations(idx_list))

def get_all_permutations(l1: list, l2: list):
    """
    Arguments:
        l1: list to be permuted and inserted preserving l2 index order
        l2: list of indices with preserved index ordering
    Returns:
        a list of (list of indices) with all possible permutations
    """
    idx_perms = get_permutations_of_idx_list(l1)
    results = []
    for idx_perm in idx_perms:
        results.extend(get_all_combinations(idx_perm, l2))

    return results


# list(set(set_output_and_pre) | set(set_pre_and_post))
# ordered list union
def union_list(list1, list2):
    """
    Arguments:
        list1: a list
        list2: a list
    Returns:
        ordered list union of the input lists
    """
    d1 = dict( zip(list1, range(len(list1))) )
    d2 = dict( zip(list2, range(len(list2))) )
    d1.update(d2)
    return list(d1.keys())


def define_data_layout(output_idx_order, pre_expr, post_expr, tensor_accesses):
    """
    returns a tuple of indices in the output of the pre expression and post expression.
    ex: consider the example X(i,m) = A(i,j) * B(j,k) * C(k,l) * D(l,m)
    Arguments:
        output_idx_order: string list of indices. ex: ['i', 'm']
        pre_expr: string list of tensor accesses. ex: ['A']
        post_expr = string list of tensor accesses. ex: ['B','C','D']
        tensor_accesses = dictionary of indices accessed by all the tensors. ex: {
            'X': ['i', 'm'],
            'A': ['i', 'j'],
            'B': ['j', 'k'],
            'C': ['k', 'l'],
            'D': ['l', 'm']
        }
    Returns:
        indexes relating to T1(i,j) = A(i,j) & T2(j,m) = B(j,k) * C(k,l) * D(l,m)
        1 --> { (i,m) intersection (i,j) } union { (i,j) intersection (j,k,l,m) }
        == {i} union {j} == {i,j}
        2 --> { (i,j) intersection (j,k,l,m) } union { (i,m) intersection (j,k,l,m) }
        == {j} union {m} == {j,m}
    """
    # 1 - intersection of output_idx_order and pre_expr
    # 2 - intersection of pre_expr and post_expr
    # union of 1 and 2
    pre_expr_indices = []
    for t in pre_expr:
        indices = tensor_accesses[t]
        for idx in indices:
            if idx not in pre_expr_indices:
                pre_expr_indices.append(idx)
    
    post_expr_indices = []
    for t in post_expr:
        indices = tensor_accesses[t]
        for idx in indices:
            if idx not in post_expr_indices:
                post_expr_indices.append(idx)

    set_output_and_pre = [idx for idx in output_idx_order if idx in pre_expr_indices]
    set_output_and_post = [idx for idx in output_idx_order if idx in post_expr_indices]
    set_pre_and_post = [idx for idx in pre_expr_indices if idx in post_expr_indices]

    print(set_output_and_pre)
    print(set_pre_and_post)
    print(set_output_and_post)
    # TODO - different data layouts can be considerd here
    pre_inds = union_list(set_output_and_pre, set_pre_and_post) # 
    post_inds = union_list(set_pre_and_post, set_output_and_post) # list(set(set_pre_and_post) | set(set_output_and_post))

    # tuple of pre and post indices
    return (pre_inds, post_inds)


