import sys
import re

class print_colors:
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKCYAN = '\033[96m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'
    
def print_error(text: str, file=""):
  if file == "": print(print_colors.FAIL + text + print_colors.ENDC)
  else: print(print_colors.FAIL + text + print_colors.ENDC, file=file)
  
def print_header(text: str, file=""):
  if file == "": print(print_colors.HEADER + text + print_colors.ENDC)
  else: print(print_colors.HEADER + text + print_colors.ENDC, file=file)
  
def print_bold(text: str, file=""):
  if file == "": print(print_colors.BOLD + text + print_colors.ENDC)
  else: print(print_colors.BOLD + text + print_colors.ENDC, file=file)

def is_valid_file_type(file_name, file_type):
  if re.match(".*\." + file_type + "$", file_name) != None: return True
  else: return False
  



class Main_Tester:
  def __init__(self, file:str, argv:list, usage:str, example:str, extra="") -> None:
    self.argv = argv
    self.usage = usage
    self.example = example
    self.extra = extra
    self.file = file
  
  def __str__(self):
    return self.__class__.__name__
  
  def is_help(self) -> bool:
    """returns whether help is argument

    Args:
        None

    Returns:
        bool: validity of arguments
    """
    if len(self.argv) == 2 and self.argv[1] == "help": return True
    else: return False
  
  def accept(self, visitor):
    visitor.visit(self)

class Main_Run_Test(Main_Tester):
  def __init__(self, argv) -> None:
    super().__init__(
      file="main_run_test",
      argv=argv,
      usage="[test_file] [json file(s)] [test name(s)]",
      example="tests-workspaces.cpp test1.json test2.json test3.json test1 test2 test3"
    )
  def is_valid_args(self) -> bool:
    """returns whether arguments are valid or not 
    
    Args:
        None
    Returns:
        bool: validity of arguments
    """
    if super().is_help(): return False
    elif len(self.argv) < 4:
      print_error("Too few arguments\n", file=sys.stderr)
      return False
    elif len(self.argv) % 2:
        print_error("Invalid arguments given.  Give file name(s) and test number(s) as command line arguments\n", file=sys.stderr)
        return False

    # make sure input files are JSON files
    for arg in self.argv[2:int((len(self.argv) + 2) / 2)]:
      if re.match(".*\.json", arg) == None:
        print_error("All file inputs must be json files", file=sys.stderr)
        return False
    
    return True
    
class Main_Store_JSON(Main_Tester):
  def __init__(self, argv) -> None:
    super().__init__(
      file="main_store_json",
      argv=argv,
      usage="[json file(s)] [test number(s)]",
      example="test1.json test2.json test3.json 1 2 3",
      extra="\tThis runs tests 1, 2 and 3 and stores them in the respective json files"
    ) 
    
  def is_valid_args(self) -> bool:
    """returns whether arguments are valid or not 
    
    Args:
        None
    Returns:
        bool: validity of arguments
    """
    if super().is_help(): return False
    elif len(self.argv) < 3:
      print_error("Invalid arguments given.  Give file name(s) and test number(s) as command line arguments\n", file=sys.stderr)
      return False
    elif (len(sys.argv) + 1) % 2:
        print_error("Invalid arguments given.  Give file name(s) and test number(s) as command line arguments\n", file=sys.stderr)
        return False

    # make sure input files are JSON files
    for arg in self.argv[1:int((len(self.argv) + 1) / 2)]:
      if re.match(".*\.json", arg) == None: 
        print_error("All file inputs must be json files", file=sys.stderr)
        return False
    for arg in self.argv[int((len(self.argv) + 1) / 2):]:
        if re.match("[0-9]+", arg) == None:
          print_error("All test inputs must be integers", file=sys.stderr)
          return False
    
    return True

class Main_Plot_Paredo(Main_Tester):
  def __init__(self, argv) -> None:
    super().__init__(
      file="plot_paredo",
      argv=argv,
      usage="[output file] [test name] [json config file] [json inputs file]",
      example="tensor_contraction*.png \"Tensor Contraction\" test0.json test0_inputs.json",
      extra="\tThe * will be replaced by a number for each test in test0_inputs.json"
    )
    
  def is_valid_args(self) -> bool:
    """returns whether arguments are valid or not 
    
    Args:
        None
    Returns:
        bool: validity of arguments
    """
    if super().is_help(): return False
    elif len(self.argv) < 5:
      print_error("Too few arguments to function")
      return False
    elif len(self.argv) > 5:
      print_error("Too many arguments to function")
      return False
    elif re.match(".*\.png", self.argv[1]) == None:
      print_error("File output must be in png format", file=sys.stderr)
      return False
    elif re.match(".*\.json", self.argv[3]) == None:
      print_error("Config file must be in json format", file=sys.stderr)
      return False
    elif re.match(".*\.json", self.argv[4]) == None:
      print_error("Inputs file must be in json format", file=sys.stderr)
      return False
    
    return True
    


class Print_Help_Visitor:
  def __init__(self) -> None:
    pass
  
  def __str__(self):
    return self.__class__.__name__
  
  def visit(self, help_type):
    if help_type.is_valid_args(): return
    
    print_header("Proper Usage:")
    print_bold("\t" + "python3 -m src." + help_type.file + " " + help_type.usage)
    print("")
    print_header("Example Execution:")
    print_bold("\t" + "python3 -m src." + help_type.file + " " + help_type.example)
    if help_type.extra != "": print(help_type.extra)
    print("")
    sys.exit()
      
