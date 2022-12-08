from pyvis.network import Network
from src.config import Config
from src.autosched import sched_enum
from src.graph_config import (graph_constants, node_colors)
from copy import deepcopy
from math import (cos, sin, pi)
import json
import re

"""
Since I can't directly modify how a node is represented structurally, I instead create this dictionary with 2 configurations, one which allows you to simply access the node via its ID and another which allows you to access all nodes based upon the number of fusions present in the given schedule.

Node associativity dictionary:
{
  ID: {
    [_ID0_]: {
      num_fusions: int,
      input_idx_order: []
    },
    [_ID1_]: {
      num_fusions: int,
      input_idx_order: []
    },
    ...
  }
  num_fusions: {
    0: [{
      ID: [_ID0_],
      input_idx_order: []
    },
    {
      ID: [_ID1_],
      input_idx_order: []
    },
    ...],
    1: [{...}],
    ...
  }
}
"""

class Graph(Network):
  def __init__(self, schedules=[Config], accesses={}, *args, **kwargs):
    # initialize Network class
    super().__init__(*args, **kwargs)
    
    # removes unfused schedules
    fused_scheds = []
    for sched in schedules:
      if self._is_fused(sched):
        fused_scheds.append(sched)
    
    schedules = fused_scheds
    
    # access via node ID, has various important things to store about node
    self.node_associativity_dict = {"ID": {}, "num_fusions": {}}
    
    # initilizes number of schedules to plot and number plotted
    if graph_constants["SCHEDULES_TO_PLOT"] == "all":
      self.scheds_to_plot = len(schedules)
    elif graph_constants["SCHEDULES_TO_PLOT"] < 1.0 and graph_constants["SCHEDULES_TO_PLOT"] > 0.0:
      self.scheds_to_plot = int(graph_constants["SCHEDULES_TO_PLOT"] * len(schedules))
    else:
      self.scheds_to_plot = int(graph_constants["SCHEDULES_TO_PLOT"])
    self.scheds_plotted = 0
    
    # get all indexes
    all_accesses = set()
    for value in accesses.values():
      for index in value:
        all_accesses.add(index)

    # build traversal matrix from all indexes
    self.trav_mat = self._build_traversal_matrix(list(all_accesses))
    
    # adjust scaling (aka position along circle) for different "rings"
    current_scaling_per_ring = [0]
    
    # if including root element
    root = None
    for schedule in schedules:   
      # check if we've put all elements in
      if self.scheds_to_plot <= self.scheds_plotted:
        break
      
      if schedule.prod == None and schedule.cons == None:   # if no fusion occurring, only node added, no edges
        if graph_constants["INCLUDE_ROOT"] and root == None:
          root = self.add_schedule(schedule, x=0, y=0)
          continue
        
        # sets starting coordinates
        x = ((1 + int(current_scaling_per_ring[0] / graph_constants["NUM_NODES_PER_PERIOD"])) * cos((2 * pi / graph_constants["NUM_NODES_PER_PERIOD"]) * current_scaling_per_ring[0]))
        y = (1 + int(current_scaling_per_ring[0] / graph_constants["NUM_NODES_PER_PERIOD"])) * sin((2 * pi / graph_constants["NUM_NODES_PER_PERIOD"]) * current_scaling_per_ring[0])
        
        # adds schedule
        permutation = self.add_schedule(schedule, x=x, y=y)           
        if graph_constants["INCLUDE_ROOT"]:
          self.add_edge(root, permutation, color="#09F68E")
        
        # updates scaling
        current_scaling_per_ring[0] += 1
      else:       # with fusion, add node and edge(s)
        # get number of fusions present in node
        num_fusions = self._count_fusions(schedule)
        
        # adds elements to current_scaling_per_ring to account for first element of a ring
        if len(current_scaling_per_ring) <= num_fusions:
          current_scaling_per_ring.extend([0] * (1 + num_fusions - len(current_scaling_per_ring)))
        
        # set color of node
        node_color = node_colors[num_fusions % len(node_colors)]
        
        # get starting coordinates
        x = (graph_constants["OFFSET_PER_RING"] * num_fusions + int(current_scaling_per_ring[num_fusions] / graph_constants["NUM_NODES_PER_PERIOD"])) * cos((2 * pi / graph_constants["NUM_NODES_PER_PERIOD"]) * current_scaling_per_ring[num_fusions])
        
        y = (graph_constants["OFFSET_PER_RING"] * num_fusions + int(current_scaling_per_ring[num_fusions] / graph_constants["NUM_NODES_PER_PERIOD"])) * sin((2 * pi / graph_constants["NUM_NODES_PER_PERIOD"]) * current_scaling_per_ring[num_fusions])
        
        # adds schedule
        self.add_schedule(config=schedule, x=x, y=y, color=node_color)
        
        # updates scaling
        current_scaling_per_ring[num_fusions] += 1
        
    for fusion_num, all_nodes in self.node_associativity_dict["num_fusions"].items():
      if fusion_num == 0:
        continue
      for individ_node in all_nodes:
        # gets index orderings for topological sorting
        idx_order = self.get_index_orders_from_idx_order(individ_node["input_idx_order"])
        
        # gets actual valid orderings based on topological sorting
        valid_parent_orderings = self.get_index_orders(self.trav_mat, idx_order)
        
        # connects node to parent nodes
        if fusion_num == 1:
          self.get_ancestors(individ_node["ID"], valid_parent_orderings, fusion_num)
        else:
          self.get_ancestors(individ_node["ID"], self._unfuse_one_layer(individ_node["input_idx_order"]), fusion_num)
        
  def _count_fusions(self, schedule=Config) -> int:
    """Counts total number of fusions present in a given schedule"""
    if(schedule.prod == None or schedule.prod == None):
      return 0
    else:
      return 1 + self._count_fusions(schedule.prod) + self._count_fusions(schedule.cons)
  
  def _updateTotals(self, trav_mat={}):
    """Updates totals of traversal matrix"""
    trav_mat = deepcopy(trav_mat)
    new_total = trav_mat["Total"]
    for key in new_total.keys():
      new_total[key] = 0
    for key, value in trav_mat.items():
      if(key == "Total"):
        continue
      else:
        for key2, value2 in value.items():
          new_total[key2] += value2
    trav_mat["Total"] = new_total
    return trav_mat
    
  def get_index_orders(self, trav_mat, orderings=[[]]):
    """Returns all possible orderings of indexes

    Args:
        trav_mat (dict[dict]): traversal matrix
        *orderings (tuple[list]): sets of orderings to initialize traversal matrix

    Returns:
        list[list]: all orderings based upon traversal matrix
    """
    trav_mat = deepcopy(trav_mat)
    # sets matrix up
    for ordering in orderings:
      pairs = list(zip(ordering, ordering[1:] + ordering[:1]))
      pairs.pop()   # remove because this would wrap back around
      for pair in pairs:
        if(trav_mat[pair[0]][pair[1]] == 0):
          trav_mat[pair[0]][pair[1]] = 1
          trav_mat["Total"][pair[1]] += 1
    
    tot_index_orders = []
    def get_indexes(trav_mat={}, index_order=[]):
      # base case
      if len(trav_mat) == 1:
        tot_index_orders.append(index_order)
        return
      
      # if impossible ordering, return
      if 0 not in trav_mat["Total"].values():
        return
      
      # get all next possible indices in ordering
      zero_columns = []
      for key, val in trav_mat["Total"].items():
        if val == 0 and key not in index_order:
          zero_columns.append(key)
      
      # if there becomes branch in possible indexes
      for index in zero_columns:
        index_cpy = deepcopy(index_order)
        trav_cpy = deepcopy(trav_mat)
        index_cpy.append(index)
        for value in trav_cpy.values():
          del value[index]
        del trav_cpy[index]
        trav_cpy = self._updateTotals(trav_cpy)
        get_indexes(trav_cpy, index_cpy)
    
    get_indexes(trav_mat, [])
    
    return tot_index_orders
    
  def get_index_orders_from_idx_order(self, input_idx_order=[]):
    """Returns all orderings as a list of lists\n
    Example:\n
    ['m', ['l', [], ['j', 'k']], ['i', 'j']] -> [['m', 'l', 'j', 'k'], ['m', 'i', 'j']]"""
    shared_order = []
    producer = []
    consumer = []
    prod_read = False
    for input_idx in input_idx_order:
      if type(input_idx) == list:
        if not prod_read:
          prod_read = True
          producer = self.get_index_orders_from_idx_order(input_idx)
        else:
          consumer = self.get_index_orders_from_idx_order(input_idx)
      else:
        shared_order.append(input_idx)
    if not prod_read:
      return [shared_order]

    prod_ordering = []
    for ordering in producer:
      prod_ordering.append(shared_order + ordering)
    cons_ordering = []
    for ordering in consumer:
      cons_ordering.append(shared_order + ordering)

    return prod_ordering + cons_ordering
    
  def _build_traversal_matrix(self, indexes=list):
    """Builds matrix of 0's where Mat['i']['j'] == 1 means i -> j ordering\n
    Example: (t represents Total)\n
    _ i j k l m\n
    i 0 0 0 0 0\n
    j 0 0 0 0 0\n
    k 0 0 0 0 0\n
    l 0 0 0 0 0\n
    m 0 0 0 0 0\n
    t 0 0 0 0 0"""
    mat = {}
    row_indexes = deepcopy(indexes)
    indexes.append('Total')
    for index1 in indexes: 
      mat[index1] = {}
      for index2 in row_indexes:
        mat[index1][index2] = 0
    
    return mat
  
  def _is_fused(self, schedule=Config) -> bool:
    """Checks if a given schedule contains any fusion"""
    if schedule.fused == False:
      return False
    if schedule.prod != None and schedule.cons != None:
      return (self._is_fused(schedule.prod) and self._is_fused(schedule.cons))
    else:
      return True
  
  def _delete_elements_trav_mat(self, trav_mat={}, els_to_del=[]):
    """Deletes indexes in list from all parts of traversal matrix"""
    trav_mat = deepcopy(trav_mat)
    for el in els_to_del:
      del trav_mat[el]
      for value in trav_mat.values():
        del value[el]
      
    return trav_mat
  
  def _get_name(self, config=Config)->list:
    """Returns node name with each detail as element of list"""
    # TODO add example
    name = []
    name.append("Tensors: " + ",".join(config.expr))
    name.append("Fused: " + str(config.fused))
    name.append("Output Index Order: " + ",".join(config.output_idx_order))
    name.append("Input Index Order: " + ",".join([str(x).replace("'", "").replace(" ", "") for x in config.input_idx_order]))
    if config.prod != None and config.cons != None:
      prod = self._get_name(config=config.prod)
      cons = self._get_name(config=config.cons)
      name.append("Producer of " + ",".join(config.expr) + ":")
      name.extend(prod)
      name.append("Consumer of " + ",".join(config.expr) + ":")
      name.extend(cons)
    return name
  
  def _unfuse_one_layer(self, indexes=[]):
    """Unfuse a single layer and returns list of lists of possible unfused schedules"""
    if len(indexes) == 0:
      return [[]]
    curr_index_list = []  # effectively a copy of unfused indexes
    orderings = []
    for index in indexes:
      if type(index) != list:
        curr_index_list.append(index)
      else:
        unfused = True
        lower_index_list = []         # effectively a copy of inner list
        for low_index in index:
          lower_index_list.append(index)
          if type(low_index) == list:
            unfused = False
          
        if unfused:
          orderings.append(None)
        else:
          orderings.append(self._unfuse_one_layer(index))
    
    if len(orderings) != 2:
      return [[]]
    elif orderings[0] == None and orderings[1] == None:
      index_orders = self.get_index_orders_from_idx_order(indexes)
      all_subindexes = set([item for sublist in index_orders for item in sublist])
      all_indexes = set(self.trav_mat.keys())
      all_indexes.remove("Total")
      cpy_trav_mat = self._delete_elements_trav_mat(self.trav_mat, list(all_indexes.difference(all_subindexes)))
      
      return self.get_index_orders(cpy_trav_mat, index_orders)
    
    else:
      total_order = []
      if orderings[0] != None:
        order_0 = orderings[0]
        for order in order_0:
          new_order = deepcopy(curr_index_list)
          if len(order) > 0 and len(indexes[-1]) > 0 and indexes[-1][0] == order[0]:
            indexes_to_separate = []
            for i in range(min([len(order), len(indexes[-1])])):
              if order[i] == indexes[-1][i]:
                indexes_to_separate.append(order[i])
              else:
                break
            for ind in indexes_to_separate:
              order.remove(ind)
              indexes[-1].remove(ind)
            new_order += indexes_to_separate
          new_order.append(order)
          new_order.append(indexes[-1])
          total_order.append(new_order)
      if orderings[1] != None:
        order_1 = orderings[1]
        for order in order_1:
          new_order = deepcopy(curr_index_list)
          if len(order) > 0 and len(indexes[-2]) > 0 and indexes[-2][0] == order[0]:
            indexes_to_separate = []
            for i in range(min([len(order), len(indexes[-2])])):
              if order[i] == indexes[-2][i]:
                indexes_to_separate.append(order[i])
                order.remove(order[i])
                indexes[-2].remove(indexes[-2][i])
              else: 
                break
            for ind in indexes_to_separate:
              order.remove(ind)
              indexes[-2].remove(ind)
            new_order += indexes_to_separate
          new_order.append(indexes[-2])
          new_order.append(order)
          total_order.append(new_order)
      return total_order
      
  def add_schedule(self, config=Config, shape=graph_constants["NODE_SHAPE"], color=node_colors[0], x=0.0, y=0.0):
    """Adds a node that represents the given schedule and returns associated ID"""
    self.scheds_plotted += 1
    name = self._get_name(config)
    # if producer / consumer graphs exist, add _'s to separate
    if len(name) > 4:
      maxLen = max([len(x) for x in name])
      for i in range(int((len(name) + 1) / 5) - 1):
        name.insert((i + 1) * 4 + 2 * i, "_" * int(graph_constants["UNDERSCORE_SCALING"] * maxLen))
    weight = self._count_fusions(config)
    
    # calculate extra spaces to include
    extra_spaces = (1.0 / len(name)) * graph_constants["EXTRA_LINES_SCALING"]
    label = "\n" * int(extra_spaces / 2) + "\n".join(name) + ("\n" * int((extra_spaces + 1) / 2)) + " "
    super().add_node(n_id=" ".join(name), label=label, shape=shape, color=color, x=(x * graph_constants["X_DISTANCE"]), y=(y * graph_constants["Y_DISTANCE"]), mass=10 ** (weight * .6), value=50)
    
    # add node to associativity dictionary by ID
    self.node_associativity_dict["ID"][" ".join(name)] = {
      "num_fusions": weight,
      "input_idx_order": config.input_idx_order
    }
    if weight not in self.node_associativity_dict["num_fusions"]:
      self.node_associativity_dict["num_fusions"][weight] = []
    
    # add node to associativity dictionary by number of fusions
    self.node_associativity_dict["num_fusions"][weight].append({
      "ID": " ".join(name),
      "input_idx_order": config.input_idx_order
    })
    
    return " ".join(name)
    
  def get_ancestors(self, node_id="", index_orders=[[]], num_fusions=1):
    """Returns all parent nodes of a given node id"""
    all_nodes = self.node_associativity_dict["num_fusions"][num_fusions - 1]
    
    if num_fusions == 1:
      for ordering in index_orders:
        str_ordering = str(ordering)[1:-1].replace("'", "").replace(" ", "")
        for node in all_nodes:
          match = re.search(str_ordering, str(node["input_idx_order"])[1:-1].replace("'", "").replace(" ", ""))
          if match != None:
            super().add_edge(node["ID"], node_id, value=12)
            # TODO add scheduling command along edge
    else:
      for ordering in index_orders:
        str_ordering = str(ordering).replace("'", "").replace(" ", "")[1:-1].replace("[", "\[").replace("]", "\]")
        for node in all_nodes:
          match = re.search(str_ordering, str(node["input_idx_order"]).replace("'", "").replace(" ", "")[1:-1])
          if match != None:
            super().add_edge(node["ID"], node_id, value=25)