from functools import cache
from zuu.appext_scoop import Scoop, ScoopPkg, ScoopSelf
import os
from zuu.util_dict import set_deep, get_deep
from zuu.util_file import save, load, touch
import subprocess

class MaaMgr:
    @staticmethod
    def init(auto_update : bool = True):
        
        if auto_update:
            if "maa" not in Scoop.bucketList():
                Scoop.bucketAdd("maa", "https://github.com/cel-ti/maa-bucket.git")

            for pkg in Scoop.list():
                if pkg.bucket == "maa":
                        pkg.update()

    def __init__(self, name : str):
        if not Scoop.pkgIsInstalled(name):
            Scoop.pkgInstall(f"maa/{name}")

        for pkg in Scoop.list():
            pkg : ScoopPkg
            if pkg.bucket == "maa" and pkg.name == name:
                self.pkg = pkg
                break
        if not self.pkg:
            raise Exception(f"Failed to get package {name}")
        
        w = ScoopSelf.path()
        self.path = pkg.path
        if name == "maa":
            self.keywords = {
                "BASE" : self.path,
                "CONFIG" : os.path.join(self.path, "config"),
                "RESOURCE" : os.path.join(self.path, "resource"),
                "TASK" : os.path.join(self.path, "config", "gui.json"),
                "SETUP" : os.path.join(self.path, "config", "gui.new.json"),

            }
        else:
            self.keywords = {
                "BASE" : self.path,
                "CONFIG" : os.path.join(self.path, "config"),
                "RESOURCE" : os.path.join(self.path, "resource"),
                "TASK" : os.path.join(self.path, "config", "config.json"),
                "SETUP" : os.path.join(self.path, "config", "maa_option.json"),
            }

    @cache
    def _parsePath(self, string : str) -> str:
        """
        parse {{var}} based on self.keywords
        """
        for key, value in self.keywords.items():
            string = string.replace("{{" + key + "}}", value)
        return string

    def patchfile(self, *args):
        """
        Patches and saves data between files using path-based operations.

        This function allows copying data from one file to another, with support for
        nested key paths and variable substitution using {{var}} syntax.

        Args:
            *args: Variable number of strings in the format 'source->destination'
                  where source and destination can include:
                  - File paths with optional key paths (e.g., 'path/to/file:key1/key2')
                  - Variable substitution using {{var}} syntax (e.g., '{{CONFIG}}/file.json')

        Examples:
            >>> mgr.patchfile('source.json:data->{{CONFIG}}/dest.json:new_data')
            >>> mgr.patchfile('file1.json->file2.json') 
            >>> mgr.patchfile('file1.json:key1/key2->file2.json:new_key')

        The function supports:
        - Deep key paths using '/' separator
        - Variable substitution using {{var}} syntax
        - Multiple file operations in a single call
        - Cumulative saves (multiple operations on same destination file)
        """
        cumulative_load = {}
        def cached_file(path : str, touch_ : bool = False):
            if path in cumulative_load:
                return cumulative_load[path]
            try:
                res = load(path)
                cumulative_load[path] = res
                return res
            except FileNotFoundError:
                if touch_:
                    touch(path)
                else:
                    raise FileNotFoundError(f"File {path} not found")
                cumulative_load[path] = {}
                return {}

        cumulative_save = {}
        for arg in args:
            leftpart, rightpart = arg.split("->")
            leftraw = leftpart.split(":")
            leftpath, leftkey = leftraw[0], leftraw[1] if len(leftraw) > 1 else None
            leftkey = leftkey.split("/") if leftkey else None

            leftdata = cached_file(leftpath, touch_=False)
            if leftkey:
                leftdata = get_deep(leftdata, *leftkey)
                
            rightraw = rightpart.split(":")
            rightpath, rightkey = rightraw[0], rightraw[1] if len(rightraw) > 1 else None
            rightpath = self._parsePath(rightpath)
            rightkey = rightkey.split("/") if rightkey else None

            if not rightkey:
                cumulative_save[rightpath] = leftdata
            else:
                if rightpath not in cumulative_save:
                    cumulative_save[rightpath] = cached_file(rightpath)
                set_deep(cumulative_save[rightpath], *rightkey, value=leftdata)
    
        for path, data in cumulative_save.items():
            save(data, path)


    def patchValue(self, path : str, key : str, value : any):
        path = self._parsePath(path)
        data = load(path)
        key = key.split("/") if "/" in key else [key]
        set_deep(data, *key, value=value)
        save(data, path)

    def call(self, path : str, *args):
        path = self._parsePath(path)
        curr_dir = os.getcwd()
        os.chdir(os.path.dirname(path))
        subprocess.run([path, *args])
        os.chdir(curr_dir)




