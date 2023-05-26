
from src.file_storing import read_json
from src.config import Config
from src.print_help import Main_Plot_Paredo, Print_Help_Visitor
import matplotlib.pyplot as plt
import sys
import re


def get_test_name(test_name:str, num:int) -> str:
  return re.sub("\*", str(num), test_name)

def plot_paredo_curve(config_list:list, test_inputs:list, test_name, file:str):
  for i, test_input in enumerate(test_inputs):
    for config in config_list
    

if __name__ == "__main__":
  main_plot_paredo = Main_Plot_Paredo(sys.argv)
  print_visitor = Print_Help_Visitor()
  main_plot_paredo.accept(print_visitor)

  




