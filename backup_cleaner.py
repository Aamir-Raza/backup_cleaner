"""
Used to clear backup directory of files not present anymore in source directory. Also removes empty directories.
Log file argument optional. Tested for Windows 10.

Usage: clean_backup.py <source directory> <target directory> <log_file>
Example usage: clean_backup.py C:/source_dir D:/backup_dir C:/log_file.txt


"""

import os
import filecmp
from datetime import datetime
import shutil
import sys

def compare():
    """Analyse source(argv[1]) and target(argv[2]) directories, find directories
    and files present only in target, or empty target directories.
    Write out to a log file(argv[3] - optional)
    """

    log_file = ''
    path_src = str(sys.argv[1])
    path_backup = str(sys.argv[2])
    src_drive,_ = os.path.splitdrive(path_src)
    backup_drive,_ = os.path.splitdrive(path_backup)
    #print("Source Drive: {}".format(src_drive))
    #print("Backup Drive: {}".format(backup_drive))
    if len(sys.argv) == 4:
        log_file = str(sys.argv[3])
    else:
        log_file = ''

    print("\nSource Dir, Drive:          {}, {}\nTarget/Backup Dir, Drive:   {}, {}\nLog_file: {}\n".format(path_src,src_drive,path_backup,backup_drive,log_file))

    print ("Searching files: ...\n")
    dir_compare = filecmp.dircmp(path_src,path_backup)
    #dir_compare.report_partial_closure()

    print ("Diff files: \n {}\n".format(dir_compare.diff_files))

    file_rm_list = dir_compare.right_only
    empty_dir_rm_list = []
    dir_rm_list = []

    print ("Files/dirs present in right only: {}\n".format(file_rm_list))

    for f in list(file_rm_list):

        full_path = os.path.join(path_backup,f)

        if os.path.isdir(full_path):

            if os.listdir(full_path):
                dir_rm_list.append(full_path)
                #print ("Directory not found in source path (added to dir removal list): {}".format(f))
            else:
                empty_dir_rm_list.append(full_path)
                #print ("Empty directory Found (added to empty dir removal list):        {}".format(f))

            #print("Removing {} entry from list: {}\n".format(f,file_rm_list))
            file_rm_list.remove(f)

        else:
            file_rm_list[file_rm_list.index(f)] = full_path

    common_dirs = dir_compare.common_dirs
    #print ("\nCommon directories: \n {}\n".format(common_dirs))
    print ("\n")

    for dir in common_dirs:
        if '%APPDATA%' not in dir:
            dir_path = os.path.join(path_backup,dir)
            for root, dirs, files in os.walk(dir_path):
                src_path = root.replace(backup_drive, src_drive)

                ### There's files in the directory, and it exists in source
                if files and os.path.isdir(src_path):
                    for file in files:
                        src_filepath = os.path.join(src_path,file)

                        if not os.path.isfile(src_filepath):
                            file_rm_list.append(os.path.join(root,file))
                            #print ("File not found in source path (added to file removal list): {}".format(os.path.join(src_path,file)))
                            #print ("Added to removal list: {}\n".format(os.path.join(root,file)))

                ### The directory is empty
                elif not os.listdir(root):
                    empty_dir_rm_list.append(root)
                    #print ("Empty directory Found (added to empty dir removal list): {}".format(root))

                ### The directory was not found in source path
                elif files and not os.path.isdir(src_path):
                    dir_rm_list.append(root)
                    #print ("Directory not found in source path (added to dir removal list): {}".format(root))

    print("\nEmpty target (backup) directories to be removed:\n{}\n".format('\n'.join(empty_dir_rm_list)))
    print("Target-only (backup) directories to be removed: \n{}\n".format('\n'.join(dir_rm_list)))
    print ("Files/directories only in backup: \n{}\n".format('\n'.join(file_rm_list)))

    if (len(file_rm_list) >= 1 or len(dir_rm_list) >=1 or len(empty_dir_rm_list) >=1):
        removal(file_rm_list, dir_rm_list, empty_dir_rm_list, log_file,path_src, path_backup)
    else:
        sys.exit()

def removal(file_rm_list, dir_rm_list, empty_dir_rm_list, log_file, path_src, path_backup):
    """Remove files, directories, empty directories passed to this function
    and write out to log file
    """

    files,dirs,empty_dirs,log_file = file_rm_list, dir_rm_list, empty_dir_rm_list, log_file
    removed_files = []
    removed_dirs = []

    if len(files)>=1:

        print ("\n--------------------------------")
        print ("-------  Removing Files  -------")
        print ("--------------------------------\n")

        for file in file_rm_list:
            full_path = os.path.join(path_backup,file)
            print("Attempting to Removing file: {}".format(full_path))
            try:
                os.remove(full_path)
                print("File Deleted: {}".format(full_path))
                removed_files.append(file)
            except:
                print("Could not delete")

            print("\n")

    if len(dirs) >= 1:

        print ("\n--------------------------------")
        print ("-----  Removing Directories  -----")
        print ("--------------------------------\n")

        for every_dir in dirs:
            try:
                shutil.rmtree(every_dir)
                print("Directory Removed: {}\n".format(every_dir))
                removed_dirs.append(every_dir)
            except OSError as e:  ## if failed, report it back to the user ##
                print ("Error: {} - {}.\n".format(e.filename, e.strerror))

    if len(empty_dirs) >= 1:

        for empty_d in empty_dirs:
            try:
                os.rmdir(empty_d)
                print("Empty Directory Removed: {}\n".format(empty_d))
                removed_dirs.append(empty_d)
            except:
                print("Could not remove directory: {}\n".format(empty_d))

    print ("--------------------------------")
    print ("-------  Writing Log  ----------")
    print ("--------------------------------\n")

    if log_file != '' and (os.path.isdir(os.path.dirname(log_file))):

        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')

        with open(log_file, 'a') as output_file:
            if len(removed_files) >=1:
                output_file.write('-- Files deleted on: {} --\n'.format(current_time))
                for every_file in removed_files:
                    output_file.write(every_file + '\n')
                output_file.write('-------------------------------- \n')
            if len(removed_dirs) >=1:
                output_file.write('-- Directories deleted on: {} --\n'.format(current_time))
                for every_dir in removed_dirs:
                    output_file.write(every_dir + '\n')
                output_file.write('-------------------------------- \n')

        print ("---- Log Written to {} -- at {} ----".format(log_file, current_time))
        print ("\n")
    
    sys.exit()

if __name__ == "__main__":
    if 5 > len(sys.argv) >=3:
        compare()
    else:
        print("Incorrect number of arguments. syntax: script src_dir target_dir log_file(optional)")
