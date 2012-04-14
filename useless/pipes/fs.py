from pipes import producer, worker, consumer
import os as _os

@producer
def listdir(path):
    for entry in _os.listdir(path):
        yield entry
        
def listdir_abs(path):
    return listdir(path) | join_path(path)

@worker
def filter_only_dirs(entries):        
    for entry in entries:
        if _os.path.isdir(entry):
            yield entry
filter_only_dirs = filter_only_dirs()

@worker
def filter_only_files(entries): 
    for entry in entries:
        if _os.path.isfile(entry):
            yield entry
filter_only_files = filter_only_files()

@worker
def filter_by_ext(files, extensions):
    for file in files:
        _, ext = _os.path.splitext(file)
        if ext.lower() in extensions:
            yield file

@worker
def join_path(names, root):
    for name in names:
        yield _os.path.join(root, name)
        
@worker
def exists(paths):
    for path in paths:
        yield _os.path.exists(path)
exists = exists()        

@worker
def get_ext(filenames):
    for filename in filenames:
        _, ext = _os.path.splitext(filename)
        yield ext
get_ext = get_ext()


