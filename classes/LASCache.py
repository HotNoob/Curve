
import copy
import io
import os
import threading
from time import sleep, time
from zipfile import ZipFile

import cython
import lasio

import global_vars


class LASDataSet:
    def __init__(self, file):
        self.data : lasio.LASFile = None
        self.file  : str = file
        self.fileTime : float = os.path.getmtime(self.file)
        self.accessTime : float = None
        self.fileName, self.fileExtension = os.path.splitext(self.file)

class LASCache:
    def __init__(self, cacheSize = 100):
        if cython.compiled:
            print("LASData Yep, I'm compiled.")
        else:
            print("LASData Just a lowly interpreted script...")
        self.cacheSize = cacheSize #max number of LAS files to cache
        self.__cache : dict[str, LASDataSet] = {} #cache, this is private
        self.__cacheLock = threading.Lock()
        self.__isPreloading = False
        self.__headerCache : dict[str, LASDataSet] = {} #cache, for header data only, this is private
        self.__preLoadThread : threading.Thread = None
        self.__closing = False

    def __readLASFile(self, filename : str) -> LASDataSet | None:
        print('LasData.__readLASFile -> ' + filename)
        lasDataSet = LASDataSet(filename)
        lasDataSet.accessTime = time()

        if(lasDataSet.fileExtension == ".zip"):
            with ZipFile(filename, 'r') as zipFile:
                for zipFileName in zipFile.namelist():
                    with zipFile.open(zipFileName, 'r') as file:
                        with io.StringIO(file.read().decode("utf-8")) as stream:
                            lasDataSet.data = lasio.read(stream)
                    print('from zip: ' + zipFileName)
                    break #read only first file
        else:
            try:
                with open(filename, 'r', encoding=global_vars.fileEncoding) as f:
                    lasDataSet.data = lasio.read(f.read())
            except Exception as e:
                print('Failed to load file LasData.__readLASFile : ' + str(e))
                return None

        return lasDataSet

    def __readLASFileHeaders(self, filename : str) -> LASDataSet | None:
        '''
            only gets the header section of the file to reduce ios. only read first few lines!!!
            probably not worth it to add zip support
        '''


        lasDataSet = LASDataSet(filename)
        lasDataSet.accessTime = time()

        memoryStream : io.StringIO = io.StringIO()
        with open(filename, 'r', encoding=global_vars.fileEncoding) as fileStream:
            for line in fileStream:
                if(str.startswith(line, '~ASCII ')):
                    break   #read file until ASCII section
                memoryStream.write(line)
            try:
                lasDataSet.data = lasio.read(memoryStream)
            except Exception as e:
                print("Failed to load LasHeaders for " + str(filename))
                return None

        return lasDataSet
    def Close(self):
        ''' call when closing '''
        self.__closing = True
        print("Las Cache CLose")

    def SaveCacheList(self, file : str = 'LasCache'):
        with self.__cacheLock:
            if self.__isPreloading: #do not save if is preloading. cache is incomplete. only save is preloading has been completed to avoid corrupting cachelist
                return
            with open(file,'w', encoding=global_vars.fileEncoding) as f:
                for value in (sorted(self.__cache.values(), key = lambda d: d.accessTime, reverse=True)): #descending
                    f.write(str(value.accessTime) +','+value.file + '\n') #write time first, because we know its a float

        return
    def startPreLoading(self, file : str = 'LasCache'):
        self.__preLoadThread = threading.Thread(target=self.PreLoadCache, args=[os.path.abspath(file)])
        self.__preLoadThread.daemon = True
        self.__preLoadThread.start()

    def PreLoadCache(self, file : str = 'LasCache'):
        print('LasData.PreLoadCache : ' + file)
        global_vars.perfTest.Start('LasData.PreLoadCache')

        if not os.path.exists(file):
            print('LasCache does not exist')
            return

        with self.__cacheLock:
            self.__isPreloading = True

        preLoadFiles : dict[str, float] = {}

        with open(file, "r", encoding=global_vars.fileEncoding) as fileHandler:
            for line in fileHandler:
                lineParts =line.strip().split(',', 1)
                if(len(lineParts) == 2): # 0 = accessTime, 1 = filename
                    if os.path.exists(lineParts[1]):
                        preLoadFiles[lineParts[1]] = float(lineParts[0])



        #make list, close file, and then start preloading in a new thread
        for filename, value in preLoadFiles.items():
            with self.__cacheLock:
                if self.__closing or not global_vars.running: #stop loading, program is closing
                    return 
                
                if filename not in self.__cache:
                    data =  self.__readLASFile(filename)
                    if data: #if data is None, failed to load
                        self.__cache[filename] = self.__readLASFile(filename)
                        self.__cache[filename].accessTime = value #set the time to the old time, to not disrupt cache behaviour
                        self.PruneCache()
            sleep(0.01)

        with self.__cacheLock:
            self.__isPreloading = False

        print('LasData.PreLoadCache : Done')
        global_vars.perfTest.Stop('LasData.PreLoadCache')
        return
    def PruneCache(self):
        if (len(self.__cache) > self.cacheSize):
            oldestFile = ''
            oldestTime = time()
            for file in self.__cache:
                if (self.__cache[file].accessTime < oldestTime):
                    oldestTime = self.__cache[file].accessTime
                    oldestFile = file

            if (oldestFile != ''):
                del self.__cache[oldestFile]
        return
    def PruneHeaderCache(self):
        if (len(self.__headerCache) > self.cacheSize):
            oldestFile = ''
            oldestTime = time()
            for file in self.__headerCache:
                if (self.__headerCache[file].accessTime < oldestTime):
                    oldestTime = self.__headerCache[file].accessTime
                    oldestFile = file

            if (oldestFile != ''):
                del self.__headerCache[oldestFile]
        return
                                          
    def GetLASHeaders(self, filename : str)  -> lasio.LASFile | None:
        ''' if file is not cached, will read only the headers, use GetLasData if you need more than just the headers'''
        filename = os.path.abspath(filename) #make sure we are using absolute paths
        print('GetLASHeaders -> ' + filename)

        with self.__cacheLock:
            if( (filename not in self.__cache or self.__cache[filename].fileTime != os.path.getmtime(self.__cache[filename].file))
                or
                (filename not in self.__headerCache or self.__headerCache[filename].fileTime != os.path.getmtime(self.__headerCache[filename].file))):

                headers = self.__readLASFileHeaders(filename)
                if not headers: #failed to load
                    return None 
        
                self.__headerCache[filename] = headers
                self.PruneHeaderCache()
                return self.__headerCache[filename].data
                
            else: #read from cache
                print("from cache")
                if filename in self.__cache:
                    return copy.deepcopy(self.__cache[filename].data)
                else:
                    return copy.deepcopy(self.__headerCache[filename].data)

    def GetLASHeadersCopy(self, filename : str)  -> lasio.LASFile:
        lasHeaders = self.GetLASHeaders(filename)
        return copy.deepcopy(lasHeaders)

    def GetLASData(self, filename : str)  -> lasio.LASFile:
        filename = os.path.abspath(filename) #make sure we are using absolute paths
        print('GetLasData -> ' + filename)

        with self.__cacheLock:
            if(filename not in self.__cache or self.__cache[filename].fileTime != os.path.getmtime(self.__cache[filename].file)):
                self.__cache[filename] = self.__readLASFile(filename)
                self.PruneCache()
                return copy.deepcopy(self.__cache[filename].data)
            else: #read from cache
                print("from cache")
                return copy.deepcopy(self.__cache[filename].data)

    def GetLASDataCopy(self, filename : str)  -> lasio.LASFile:
        lasFile = self.GetLASData(filename)
        return copy.deepcopy(lasFile)
