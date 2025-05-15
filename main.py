import os 
import numpy as np
# Imports the Windows COM client library, enables Python to communicate with COM-compatible applications like Aspen Plus
import win32com.client as win32  
# Imports the Latin Hypercube Sampling method
from smt.sampling_methods import LHS
#  Creates a COM object for Aspen Plus,
aspen = win32.Dispatch('Apwn.Document')
#  Opens an Aspen file
aspen.InitFromArchive2(os.path.abspath('Simulation.bkp'))

S2 = [50,90]
xlimits=np.array([S1,S2])
sampling = LHS(xlimits=xlimits) # Initializes Latin Hypercube Sampling with the defined parameter boundaries.
num = 100 # Generates  sample points distributed across the parameter space.
x = sampling(num)
moleflow_S1_inputs = []
moleflow_S2_inputs = []
T_out=[]
for i in range(0,num-1):
# Change input parameters, to find the path, the user should explore from Variable Explorer
    aspen.Tree.FindNode('\Data\Streams\S1\Input\TOTFLOW\MIXED').Value = x[i,0] 
    aspen.Tree.FindNode('\Data\Streams\S2\Input\TOTFLOW\MIXED').Value = x[i,1]
    moleflow_S1_inputs.append(x[i,0])
    moleflow_S2_inputs.append(x[i,1])
# Executes the Aspen Plus simulation with the current parameter values.
    aspen.Engine.Run2()
# Extracts and stores the output paramters  
    T_out.append(aspen.Tree.FindNode('\Data\Streams\S3\Output\TEMP_OUT\MIXED').value)
#         aspen.Close()

a = np.array([moleflow_S1_inputs,moleflow_S2_inputs,T_out])      
b = np.transpose(a)     
np.savetxt('sample.csv',b,delimiter=',')


print (T_out)
print (moleflow_S1_inputs)
print (moleflow_S2_inputs)
