from src.file_storing import read_json
from src.config import Config
from src.print_help import Main_Plot_Paredo, Print_Help_Visitor
from src.remove_files import delete_files
import matplotlib.pyplot as plt
import sys
import re
import json
from copy import deepcopy
from math import ceil

num_points = 10
min_dense = 10
max_dense = 1000
min_sparse = 1
max_sparse = 500
size = 8

colors = ["#2C497F", "#995FA3", "#FAFF7F", "#FF5154", "#2C497F", "#FFD166", "#5F5449", "#3A5A40", "#28AFB0", "#37392E", "#DB324D", "#A29C9B"]

def next_color(iteration):
  return colors[iteration % len(colors)]


def get_time_complexity(test_input:dict, time_expr:dict):
  tot_complexity = 0
  for mult_expr in time_expr["r"]:
    expr_multiplied = 1
    for key in mult_expr.keys():
      expr_multiplied *= int(test_input[key])
    tot_complexity += expr_multiplied
  
  for mult_expr in time_expr["a"]:
    expr_multiplied = 1
    for key in mult_expr.keys():
      expr_multiplied *= int(test_input[key])
    tot_complexity += expr_multiplied
    
  return tot_complexity

def get_memory_complexity(test_input: dict, memory_expr: list):
  tot_complexity = 0
  for mult_expr in memory_expr:
    expr_multiplied = 1
    for key in mult_expr:
      expr_multiplied *= int(test_input[key])
    tot_complexity += expr_multiplied
  
  return tot_complexity

def get_file_name(file_name:str, num:int) -> str:
  return re.sub("\*", str(num), file_name)

def plot_varying_pareto_curves(config_list:list, test_inputs:list, test_name:str, file:str):
  for i, test_input in enumerate(test_inputs):  
    # time_complexity = []
    # memory_complexity = []
    
    
    for index in test_input.keys():
      # color = 0
      incr_val = ceil((max_dense - min_dense) / num_points)
      start_val = min_dense
      end_val = max_dense
      if re.match(".+pos", index) != None: 
        incr_val = ceil((max_sparse - min_sparse) / num_points)
        start_val = min_sparse
        end_val = max_sparse
        
      for iteration, config in enumerate(config_list):
        time_complexity = []
        memory_complexity = []
        for j in range(start_val, end_val, incr_val):
          test_input_copy = deepcopy(test_input)
          test_input_copy[index] = j
          time_complexity.append(get_time_complexity(test_input_copy, config.time_complexity))
          memory_complexity.append(get_memory_complexity(test_input_copy, config.memory_complexity))
        plt.scatter(time_complexity, memory_complexity, color=next_color(iteration), s=size)
      plt.xlabel("Time Complexity")
      plt.ylabel("Memory Complexity")
      plt.title(f'{test_name} with varying {index}')
      plt.ylim(bottom=0)

      plt.savefig(index + "_" + get_file_name(file, i + 1))
      plt.close()

      
    
    # plt.scatter(time_complexity, memory_complexity)
    # plt.xlabel("Time Complexity")
    # plt.ylabel("Memory Complexity")
    # plt.title(test_name)
    # plt.ylim(bottom=0)
    
    # plt.savefig(get_file_name(file, i + 1))
    # print(f'time_complexity: {time_complexity}')
    # print(f'memory_complexity: {memory_complexity}')

# TODO normalize graphs
def plot_pareto_curve(config_list:list, test_inputs:list, test_name:str, file:str):
  for i, test_input in enumerate(test_inputs):  
    time_complexity = []
    memory_complexity = []
    for config in config_list:
      time_complexity.append(get_time_complexity(test_input, config.time_complexity))
      memory_complexity.append(get_memory_complexity(test_input, config.memory_complexity))
    
    plt.scatter(time_complexity, memory_complexity, s=size)
    plt.xlabel("Time Complexity")
    plt.ylabel("Memory Complexity")
    plt.title(test_name)
    plt.ylim(bottom=0)
    
    plt.savefig(get_file_name(file, i + 1))
    # print(f'time_complexity: {time_complexity}')
    # print(f'memory_complexity: {memory_complexity}')

if __name__ == "__main__":
  main_plot_pareto = Main_Plot_Paredo(sys.argv)
  print_visitor = Print_Help_Visitor()
  main_plot_pareto.accept(print_visitor)
  # print(sys.argv)
  
  # read in json inputs file
  try:
    fileptr = open(sys.argv[4], "r")
  except OSError:
    print("Invalid JSON file for reading", file=sys.stderr)
    sys.exit()
    
  delete_files(r'.*\.png')

  test_inputs = json.load(fileptr)
  fileptr.close()
  
  # gets configs
  config_list = read_json(sys.argv[3])
  
  # plot_pareto_curve(config_list, test_inputs["inputs"], sys.argv[2], sys.argv[1])
  plot_varying_pareto_curves(config_list, test_inputs["inputs"], sys.argv[2], sys.argv[1])
  plot_pareto_curve(config_list, test_inputs["inputs"], sys.argv[2], sys.argv[1])
  
  # for config in config_list:
  #   print(config)

  




