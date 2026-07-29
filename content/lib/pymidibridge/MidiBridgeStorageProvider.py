import json
from os import stat, rename, listdir

# Access to storage (used by the bridge). Note that the storage must be mounted with write privileges
# if the write functionality should work, else an exception is raised.
class MidiBridgeStorageProvider:

    # File handle for writing
    class _FileHandleWrite:
        def __init__(self, temp_path, final_path):
            self._temp_path = temp_path
            self._final_path = final_path
            
            # Clear before appending
            open(self._temp_path, "w").close()
            
            # Data is first stored into a temporary file path, then copied to the destination when finished.
            self._handle = open(self._temp_path, "a")

        # Must read from the file handle
        def read(self, amount_bytes):
            raise Exception()

        # Must append data to the passed file handle
        def write(self, data):
            self._handle.write(data)

        # Must close the file handle
        def close(self):
            self._handle.close()
            self._handle = None

            # Copy temp file to its destination
            rename(self._temp_path, self._final_path)


    #####################################################################################


    # File handle for reading
    class _FileHandleRead:
        def __init__(self, path):
            self._handle = open(path, "r")

        # Must read from the file handle
        def read(self, amount_bytes):
            return self._handle.read(amount_bytes)

        # Must append data to the passed file handle
        def write(self, data):
            raise Exception()

        # Must close the file handle
        def close(self):
            self._handle.close()
            self._handle = None


    #####################################################################################


    # File handle for folder listing (used whenever the path is a directory)
    class _FileHandleListDir:
        def __init__(self, content):
            self._listing = content

        # Must read from the file handle
        def read(self, amount_bytes):
            ret = self._listing[:amount_bytes]
            self._listing = self._listing[amount_bytes:]
            return ret

        # Must append data to the passed file handle
        def write(self, data):
            raise Exception()

        # Must close the file handle
        def close(self):
            pass


    #####################################################################################


    # You have to provide a path for a temporary file, used to buffer contents before transmission finished.
    def __init__(self, temp_file_path):
        self._temp_file_path = temp_file_path
        

    # Must return file size. In case of directories, we return the size of the string to be sent.
    def size(self, path):
        try:
            if self._is_dir(path):
                return len(self._get_folder_listing(path))
            
            return stat(path)[6]
        
        except OSError as e:
            if e.errno == 2:
                return -1
            raise e
    

    # Must return an opened file handle
    def open(self, path, mode):
        if mode == "a":
            # Write a file
            return self._FileHandleWrite(
                temp_path = self._temp_file_path,
                final_path = path
            )
        elif mode == "r":
            if self._is_dir(path):
                # Return a folder listing
                return self._FileHandleListDir(
                    content = self._get_folder_listing(path)
                )
            else:
                # Read a file
                return self._FileHandleRead(
                    path = path
                )


    # Is path a folder?
    def _is_dir(self, path):
        return stat(path)[0] == 16384
    
    
    # Returns the string for folder listings.
    def _get_folder_listing(self, path):
        if not path[-1] == "/":
            path += "/"

        data = []
        for file in listdir(path):
            stats = stat(path + file)

            data.append([
                file,
                stats[0] == 16384,
                stats[6]
            ])
            
        return json.dumps(data)

