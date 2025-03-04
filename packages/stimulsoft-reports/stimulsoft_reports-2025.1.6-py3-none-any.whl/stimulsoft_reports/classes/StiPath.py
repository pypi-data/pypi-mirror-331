import os

class StiPath:

### Fields

    filePath: str = None
    directoryPath: str = None
    fileName: str = None
    fileNameOnly: str = None
    fileExtension: str = None


### Helpers

    def normalize(path: str) -> str:
        return os.path.normpath(path.split('?')[0]).rstrip('/\\')
    
    def __getMissingFileName(filePath: str) -> str:
        filePath = StiPath.normalize(filePath)
        return os.path.basename(filePath)
    
    def __getRealFilePath(filePath: str) -> str:
        filePath = StiPath.normalize(filePath)
        if os.path.isfile(filePath):
            return filePath
        
        workingDir = os.getcwd()
        filePath = StiPath.normalize(f'{workingDir}/{filePath}')
        if os.path.isfile(filePath):
            return filePath
        
        return None
    
    def __getRealDirectoryPath(directoryPath: str) -> str:
        filePath = StiPath.normalize(directoryPath)
        
        directoryPath = filePath
        if os.path.isdir(directoryPath):
            return directoryPath

        workingDir = os.getcwd()
        directoryPath = StiPath.normalize(f'{workingDir}/{directoryPath}')
        if os.path.isdir(directoryPath):
            return directoryPath
        
        directoryPath = os.path.dirname(filePath)
        if os.path.isdir(directoryPath):
            return directoryPath

        directoryPath = StiPath.normalize(f'{workingDir}/{directoryPath}')
        if os.path.isdir(directoryPath):
            return directoryPath
        
        return None


### Constructor

    def __init__(self, filePath):
        self.filePath = StiPath.__getRealFilePath(filePath)
        self.directoryPath = StiPath.__getRealDirectoryPath(filePath)
        
        self.fileName = os.path.basename(self.filePath) if self.filePath != None else StiPath.__getMissingFileName(filePath)
        if self.filePath == None and (self.directoryPath or '').endswith(self.fileName):
            self.fileName = None

        if self.fileName != None:
            self.fileNameOnly, self.fileExtension = os.path.splitext(self.fileName)
            self.fileExtension = self.fileExtension[1:].lower() if len(self.fileExtension or '') > 1 else ''