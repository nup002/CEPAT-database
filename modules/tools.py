from pathlib import Path
from uuid import uuid4
import numpy as np
import matplotlib.pyplot as pyp

WEIGHTS = {
        'recovered':{'age':0.7,
                    'sex':0.5,
                    'comorbidity':0.5,
                    'symptoms':0.5,
                    'oxygen_requirement':0.8,
                    'medicine':0.3},
         'days_to_recovery':{'age':0.8,
                        'sex':0,
                        'comorbidity':0.3,
                        'symptoms':0.6,
                        'oxygen_requirement':0.7,
                        'medicine':0.5},
         'days_of_ventilation':{'age':0.7,
                        'sex':0.2,
                        'comorbidity':0.2,
                        'symptoms':0.2,
                        'oxygen_requirement':1.5,
                        'medicine':0.3},
         'days_of_icu':{'age':0.7,
                        'sex':0.3,
                        'comorbidity':0.1,
                        'symptoms':0.1,
                        'oxygen_requirement':2,
                        'medicine':0.1}
}

def estimateOutcome(_entry):
    #print(f"Estimating outcome of {_entry}")
    entry = list(_entry)
    entry[0] = _entry['age']/80
    entry[1] = 0.6 if _entry['sex'] == 1 else 0.4
    entry[2] = 0.7 if _entry['comorbidity'] > 0 else 0.3
    entry[4] = _entry['oxygen_requirement']/10
    #symptom
    if _entry['symptoms'] == 0:
        entry[3] = 0.2
    elif _entry['symptoms']%2 == 0:
        entry[3] = 2
    else:
        entry[3] = 1
    #medicine
    if entry[3] == 0:
        entry[5] = 0.2
    elif entry[3] < 1.5:
        entry[5] = -1 if _entry['medicine']>0 else 0.5
    else:
        entry[5] = -0.5 if _entry['medicine']>0 else 1.5
    #print(f"Parsed entry: {entry}")
    days_of_icu = calcDaysOfIcu(WEIGHTS['days_of_icu'],entry)
    days_of_ventilation = calcDaysOfVentilation(WEIGHTS['days_of_ventilation'],entry,days_of_icu)
    recovered = calcRecovery(WEIGHTS['recovered'],entry)
    if recovered:
        days_to_recovery = calcDaysToRecovery(WEIGHTS['days_to_recovery'],entry)
    else:
        days_to_recovery = None
    
    ret = {'recovered':recovered, 
           'days_to_recovery':days_to_recovery,
           'days_of_ventilation':days_of_ventilation, 
           'days_of_icu':days_of_icu}
    #print(f"\tResult:{ret}")
    return ret

def calcDaysOfIcu(weights,entry):
    weighted = [entry[0]**2*weights['age'],
                entry[1]*weights['sex'],
                entry[2]*weights['comorbidity'],
                entry[3]*weights['symptoms'],
                entry[4]**2*weights['oxygen_requirement'],
                entry[5]*weights['medicine']]
    sm = sum(weighted)**2*10
    if sm >3:
        return int(sm)
    else:
        return 0

def calcDaysOfVentilation(weights,entry,days_of_icu):
    weighted = [entry[0]**2*weights['age'],
                entry[1]*weights['sex'],
                entry[2]**2*weights['comorbidity'],
                entry[3]*weights['symptoms'],
                entry[4]**2*weights['oxygen_requirement'],
                entry[5]*weights['medicine']]
    sm =  days_of_icu - sum(weighted)*3
    if sm < 0:
        return 0
    else:
        return int(sm)

def calcRecovery(weights,entry):
    weighted = [entry[0]**2*weights['age'],
                entry[1]*weights['sex'],
                entry[2]*weights['comorbidity'],
                entry[3]*weights['symptoms'],
                entry[4]**2*weights['oxygen_requirement'],
                entry[5]*weights['medicine']]
    return sum(weighted)<2.7

def calcDaysToRecovery(weights,entry):
    weighted = [entry[0]**2*weights['age'],
                entry[1]*weights['sex'],
                entry[2]*weights['comorbidity'],
                entry[3]*weights['symptoms'],
                entry[4]*weights['oxygen_requirement'],
                entry[5]*weights['medicine']]
    return int(sum(weighted)*15)

def analyze(search_result):
    relpath = Path("./plots") / Path(str(uuid4())[-8:]+ ".png") 
    save_path = relpath.absolute()
    print(f"Saving plot to {save_path}")
    arr = np.array(search_result)
    print(arr)
    if len(arr) != 0:
        survival = arr[:,0].astype(int)
        days_to_recovery = [i for i in arr[:,1] if i]
        days_of_ventilation = [i for i in arr[:,2] if i]
        days_of_icu = [i for i in arr[:,3] if i]
    else:
        survival = []
        days_to_recovery = []
        days_of_ventilation = []
        days_of_icu = []
        
    fig, ((ax1, ax2), (ax3, ax4)) = pyp.subplots(nrows=2, ncols=2)
    pyp.tight_layout()
    ax1.hist(survival,bins=[-0.5, 0.5, 1.5], edgecolor='black', linewidth=1)
    ax2.hist(days_to_recovery, edgecolor='black', linewidth=1)
    ax3.hist(days_of_ventilation, edgecolor='black', linewidth=1)
    ax4.hist(days_of_icu, edgecolor='black', linewidth=1)
    
    ax1.set_title('Survival')
    pyp.sca(ax1)
    pyp.xticks(ticks=[0,1], labels=["Death", "Recovery"])
    ax2.set_title('Days to recovery')
    ax3.set_title('# of days on ventilator')
    ax4.set_title('# of days in ICU')
    
    fig.savefig(save_path, dpi=300)
    return save_path
    