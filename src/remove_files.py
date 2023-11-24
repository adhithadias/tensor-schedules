import re
import os
import glob

def delete_file(file_name):
  if file_name in os.listdir():
    os.remove(file_name)
    return True
  else: return False
    
def delete_files(pattern):
  files = []
  for file in os.listdir():
    if re.match(pattern, file): files.append(file)
  # files = glob.glob(pattern)
  print(files)
  if len(files) > 0:
    for file in files:
      delete_file(file)
    return True
  else: return False