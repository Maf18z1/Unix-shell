import tarfile
import os
import tkinter as tk
import argparse

class VShell:
    def __init__(self, filesystem_archive: str, username: str, hostname: str):
        self.username = username
        self.hostname = hostname
        self.currentpath = ""
        self.filesystem = tarfile.open(filesystem_archive)
        self.filesystemlist = self.filesystem.getmembers()
        print(self.filesystemlist)

    def start_gui(self):
        self.root = tk.Tk()
        self.root.title(f"Shell Emulator")
        
        self.text_area = tk.Text(self.root)
        self.text_area.pack(expand=True, fill=tk.BOTH)

        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(fill=tk.X)

        self.prompt_label = tk.Label(self.input_frame, text=f"{self.username}@{self.hostname}$ ", anchor="w")
        self.prompt_label.pack(side=tk.LEFT)

        self.entry = tk.Entry(self.input_frame)
        self.entry.pack(fill=tk.X)
        self.entry.bind("<Return>", self.process_command)

        self.entry.focus()

        self.root.mainloop()

    def process_command(self, event):
        cmd = self.entry.get().split(" ")
        self.entry.delete(0, tk.END)

        command = cmd[0].lower()

        if command == "ls":
            self.ls(cmd[1] if len(cmd) > 1 else "")
        elif command == "cd":
            self.cd(cmd[1] if len(cmd) > 1 else "")
        elif command == "cat":
            self.cat(cmd[1] if len(cmd) > 1 else "")
        elif command == "mv":
            self.mv(cmd[1], cmd[2] if len(cmd) > 2 else "")
        elif command == "rev":
            self.rev(cmd[1] if len(cmd) > 1 else "")
        elif command == "exit":
            self.root.quit()
        else:
            self.display_text(f"Unknown command: {command}")

    def display_text(self, text):
        self.text_area.insert(tk.END, text + "\n")
        self.text_area.see(tk.END)

    def ls(self, newpath=""):
        path = self.currentpath if not newpath else os.path.join(self.currentpath, newpath).replace('\\', '/')

        path_with_slash = path if path.endswith('/') else path + '/'
        
        files = [file for file in self.filesystemlist 
             if file.name.startswith(path_with_slash) 
             and '/' not in file.name[len(path_with_slash):].strip('/')]
        print(files)
        if files:
            file_names = [os.path.basename(file.name) for file in files]
            self.display_text("  ".join(file_names))
        else:
            self.display_text(f"Directory '{newpath}' does not exist or is empty.")


    def cd(self, newpath=""):
        if newpath == "..":
            self.currentpath = os.path.dirname(self.currentpath)
        elif newpath == "~" or newpath == "/":
            self.currentpath = ""
        elif newpath == "":
            self.currentpath = ""
        else:
            dirs=[dir.name for dir in self.filesystemlist if dir.isdir()]
            if newpath.startswith('..'):
                potential_path = os.path.normpath(os.path.join(self.currentpath, newpath)).replace('\\', '/')
            elif os.path.join(self.currentpath, newpath).replace('\\','/') in dirs:
                potential_path = os.path.join(self.currentpath, newpath).replace('\\', '/')
            else:
                potential_path = newpath.replace('\\', '/')
            if any(file.name == potential_path and file.isdir() for file in self.filesystemlist):
                self.currentpath = potential_path
            else:
                self.display_text(f"Directory '{newpath}' does not exist.")


    def cat(self, filename):
        if filename.startswith('/'):
            path = filename
        else:
            path = os.path.join(self.currentpath, filename).replace('\\', '/')

        try:
            file = next(file for file in self.filesystemlist if file.name == path)
            with self.filesystem.extractfile(file) as f:
                content = f.read().decode('utf-8')
                self.display_text(content)
        except StopIteration:
            self.display_text(f"Error: File '{filename}' not found.")
        except KeyError:
            self.display_text(f"Error while opening {filename}.")

    def mv(self, src, dest):
        if src.startswith('/'):
            src_path = src
        else:
            src_path = os.path.join(self.currentpath, src).replace('\\', '/')

        if dest.startswith('/'):
            dest_path = dest
        else:
            dest_path = dest.replace('\\', '/')

        try:
            file = next(file for file in self.filesystemlist if file.name == src_path)
            dest_directory = os.path.dirname(dest_path)
            new_file_name = os.path.basename(dest_path)

            if dest_directory and not any(dir.name == dest_directory for dir in self.filesystemlist if dir.isfile() or dir.isdir()):
                self.display_text(f"Error: Destination directory '{dest_directory}' does not exist.")
                return
        
            if dest_directory == "":
                dest_directory = self.currentpath

            file.name = os.path.join(dest_directory, new_file_name).replace('\\', '/')
            self.display_text(f"Moved '{src}' to '{dest}.")
        
        except StopIteration:
            self.display_text(f"Error: File '{src}' not found.")
        except Exception as e:
            self.display_text(f"Error while moving '{src}': {str(e)}")

    def rev(self, filename):
        if filename.startswith('/'):
            path = filename
        else:
            path = os.path.join(self.currentpath, filename).replace('\\', '/')

        try:
            file = next(file for file in self.filesystemlist if file.name == path)
            with self.filesystem.extractfile(file) as f:
                content = f.read().decode('utf-8')
                reversed_content = content[::-1]
                self.display_text(reversed_content)
        except StopIteration:
            self.display_text(f"Error: File '{filename}' not found.")
        except KeyError:
            self.display_text(f"Error while opening {filename}.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="VShell Emulator")
    parser.add_argument('--username', required=True, help="Username for shell prompt.")
    parser.add_argument('--hostname', required=True, help="Hostname for shell prompt.")
    parser.add_argument('--filesystem', required=True, help="Path to the tar filesystem archive.")

    args = parser.parse_args()

    vshell = VShell(args.filesystem, args.username, args.hostname)
    vshell.start_gui()
