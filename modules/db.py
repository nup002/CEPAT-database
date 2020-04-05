import numpy as np
from pathlib import Path
import pickle
import progressbar
from .definitions import FIELDS_SEARCH, FIELDS_RESULT
from .tools import *
from functools import lru_cache

class DB(object):
    def __init__(self):
        self.fields_dict = {}
        self.calcDtype()
        self.db_path = Path("./db/database.bin")
        self.createFieldsDict()
        self.createOrFindDB()
        
    def addEntry(self, entry_vector, entry_data):
        vector = []
        for key, val in entry_vector.items():
            if val:
                map_arr = self.fields_dict[key]
                if val<map_arr[0] or val>map_arr[-1]:
                    raise ValueError(f"The value of the \"{key}\" parameter is "
                                     f"outside the valid limits : {map_arr[0]} to "
                                     f"{map_arr[-1]}.")
                array_map_val = self.fields_dict[key].index(val)
            else:
                array_map_val = 0
            vector.append(array_map_val)
        vector = tuple(vector)
        self.insert(vector, entry_data)
        
    def insert(self, vector, entry_data):
        data = tuple(entry_data.values())
        if self._db[vector] is not None:
            self._db[vector].append(data)
        else:
            self._db[vector] = [data]
     
    def getEntries(self, search_vector):
        slicer = []
        for key, val in search_vector.items():
            if val is not None:
                map_arr = self.fields_dict[key]
                if val<map_arr[0] or val>map_arr[-1]:
                    raise ValueError(f"The value of the \"{key}\" parameter is "
                                     f"outside the valid limits : {map_arr[0]} to "
                                     f"{map_arr[-1]}.")
                array_map_val = self.fields_dict[key].index(val)
            else:
                print(f"Searching for all {key} since val is {val}")
                array_map_val = slice(None)
            slicer.append(array_map_val)
        subarray = self._db[tuple(slicer)]
        flat = subarray.flatten()
        ret = [item for sublist in flat if sublist for item in sublist]
        return ret
        
    def createOrFindDB(self):
        if not self.db_path.exists():
            self.createDb()
            
        self.loadDb()
    
    def createFieldsDict(self):
        dim_tuple = []
        for key,d in FIELDS_SEARCH.items():
            min = d.get('min')
            max = d.get('max')
            step = d.get('step', 1)
            rnge = list(range(min,max+step,step))
            self.fields_dict[key] = rnge
            dim_tuple.append(len(rnge))
        return dim_tuple
    
    def calcDtype(self):
        dtypes = []
        for key,d in FIELDS_RESULT.items():
            dtypes.append((key,d['dtype']))
        self.dtype = dtypes
        
    def createDb(self):
        dim_tuple = tuple(len(arr) for arr in self.fields_dict.values())
        print(f"Creating database of dimensions {dim_tuple}")

        self._db = np.full(dim_tuple,None)
        self.saveDb()
        
    def getAdmittanceProb(self,age_arr):
        #god of programming forgive me
        probs = {'<19':0.01,
                 '20-44':0.19,
                 '45-64':0.3,
                 '>65':0.5}
        probs_scaled = probs
        probs_scaled['<19'] = probs['<19'] / sum([1 for age in age_arr if age < 19 ]) 
        probs_scaled['20-44'] = probs['20-44'] / sum([1 for age in age_arr if age < 44 and age >= 20])
        probs_scaled['45-64'] = probs['45-64'] / sum([1 for age in age_arr if age < 65 and age >= 45]) 
        probs_scaled['>65'] = probs['>65'] / sum([1 for age in age_arr if age >= 65]) 
        
        probs_arr = []
        for age in age_arr:
            if age < 19:
                probs_arr.append(probs_scaled['<19'])
            elif age < 44 and age >= 20:
                probs_arr.append(probs_scaled['20-44'])
            elif age < 65 and age >= 45:
                probs_arr.append(probs_scaled['45-64'])
            else:
                probs_arr.append(probs_scaled['>65'])
        return probs_arr
    
    def getSymptom(self,age,sex):
        """
        Mild Symptoms	<19 and 20 - 44
        Severe Symptoms	45 - 64 and >65
        	
        Mild Symptoms	Female 80 %
        Severe Symptoms	Male 80 % """
        
        if age < 19:
            choices_mild = [1,3,5,13,17,19]
            choices_severe = [2,4,6]
        elif age < 44 and age >= 20:
            choices_mild = [1,3,5,11,13,17,19]
            choices_severe = [2,4,6,12,18,20]
        elif age < 65 and age >= 45:
            choices_severe = [2,4,6,12,14,16,18,20]
            choices_mild = [1,3,5,11,13,15,17,19]
        else:
            choices_severe = list(range(2,22,2))
            choices_mild = list(range(1,21,2))
            
        if age < 44:
            if sex == 1:
                probs = [0.5,0.15,0.35]
            else:
                probs = [0.5,0.35,0.15]
        else:
            if sex == 1:
                probs = [0,0.15,0.85]
            else:
                probs = [0,0.25,0.75]
        choices = [0,1,2]
        rn = np.random.choice(choices,p=probs)
        if rn != 0:
            if rn == 1:
                rn = np.random.choice(choices_mild)
            else:
                rn = np.random.choice(choices_severe)
        return rn
    
    def getSex(self):
        probs = [0.01,0.4,0.59] 
        return np.random.choice([0,1,2],p=probs)
    
    def getComorbidity(self, age):
        if age < 19:
            prob = [0.9,0.1]
            choices = [5]
        elif age < 44 and age >= 20:
            prob = [0.6,0.4]
            choices = [4,5,9]
        elif age < 65 and age >= 45:
            prob = [0.3,0.7]
            choices = [2,4,5,6,7,8,9]
        else:
            prob = [0,1]
            choices = self.fields_dict['comorbidity']
            
        has_comorb_options = [False,True]
        has_comorb = np.random.choice(has_comorb_options,p=prob)
        if has_comorb:
            return np.random.choice(choices)
        else:
            return 0
            
    def getOxygenReq(self,symptom):
        if symptom == 0:
            return 0
        if symptom%2 == 1:
            res = int(np.random.normal(3,1.5))
        if symptom%2 == 0:
            res = int(np.random.normal(6,3))
        return min(max(0, res), 10)
    
    def fillDummyData(self):
        entries = 100000
        ages = self.fields_dict['age']
        age_probs_arr = self.getAdmittanceProb(ages)

        for i in progressbar.progressbar(range(entries)):
            #Build vector
            age = np.random.choice(ages,p=age_probs_arr)
            sex = self.getSex()
            symptom = self.getSymptom(age,sex)
            comorbidity = self.getComorbidity(age)
            oxygen = self.getOxygenReq(symptom)
            rand_vector = {'age':age,
                           'sex':sex,
                           'comorbidity':comorbidity,
                           'symptoms':symptom,
                           'oxygen_requirement':oxygen,
                           'medicine':np.random.choice(self.fields_dict['medicine'])}      
            rand_data = estimateOutcome(rand_vector)
            self.addEntry(rand_vector, rand_data)
        self.saveDb()
        self.loadDb()
        
    def saveDb(self):
        print(f"Writing database to {self.db_path.absolute()}")
        with open(self.db_path.absolute(), 'w+b') as f:
            pickle.dump(self._db,f)
            
    def loadDb(self):
        with open(self.db_path, 'rb') as f:
            self._db = pickle.load(f)

    