from numpy import dtype

FIELDS_SEARCH = {'age':{
                    'min':0,
                    'max':120,
                    'step':5,
                    'enum':0
                    },
                'sex':{
                    'min':1,
                    'max':3,
                    'enum':1
                    },
                'comorbidity':{
                    'min':1,
                    'max':10,
                    'enum':2
                    },
                'symptoms':{
                    'min':1,
                    'max':20,
                    'enum':3
                    },
                'oxygen_requirement':{
                    'min':1,
                    'max':10,
                    'enum':4
                    },
                'medicine':{
                    'min':1,
                    'max':10,
                    'enum':5
                    }
                }


FIELDS_RESULT = {'recovered':{
                    'dtype':bool,
                    },
                'days_to_recovery':{
                    'dtype':dtype('u1'),
                    },
                'days_of_ventilation':{
                    'dtype':dtype('u1'),
                    },
                'days_of_icu':{
                    'dtype':dtype('u1'),
                    }}
                
