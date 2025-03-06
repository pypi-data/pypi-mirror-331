import numpy as np
import sys
import argparse
import yaml
import DSSHandler
from numpy import genfromtxt

#Argparsing for running this through the commandline 
if __name__ == "__main__":
    parser  = argparse.ArgumentParser(
        description="This command line program will take an input CSV file and apply DSS analysis "
        )
    parser.add_argument('-d','--data',required=True, help='Data file to analyze')
    parser.add_argument('-m','--model',required=True, help='Model YAML file for data predicition')
    parser.add_argument('-o','--output',required=True, help='Output folder name')
    args = parser.parse_args(sys.argv[1:])
    my_data = genfromtxt(args.data, delimiter =',',skip_header=1)
    with open(args.model,'r') as f:
        inputs = yaml.safe_load(f)

_splitdata = np.array_split(my_data,2,1)
_time = np.concatenate(_splitdata[0])
_rawdata = np.concatenate(_splitdata[1])


#First I calculate all experimental data parameters
dataBetas = DSSHandler.data_normalizer(_rawdata,inputs)
dataOmegas = DSSHandler.time_derivative(dataBetas,_time)
dataOmegaPrimes = DSSHandler.time_derivative(dataOmegas,_time)
dataTaus = DSSHandler.process_time_generator(dataBetas,dataOmegas)
dataD = DSSHandler.temporal_displacement_generator(dataBetas,dataOmegas,dataOmegaPrimes)
dataProcessAction = DSSHandler.process_action_solver(_time,dataD)
effectMetricExperiment,normalizedReferenceTimeExperiment,normalziedProcesstimeExperiment = DSSHandler.normalized_coordinates(dataOmegas,_time,dataTaus,dataProcessAction)
dataEffectParameter = DSSHandler.effect_parameter_solver(effectMetricExperiment)

#Then my model DSS parameters
modelData = DSSHandler.model_data_generator(_time,inputs)
modelBetas = DSSHandler.data_normalizer(modelData,inputs)
modelOmegas = DSSHandler.time_derivative(modelBetas,_time)
modelOmegaPrimes = DSSHandler.time_derivative(modelOmegas,_time)
modelTaus = DSSHandler.process_time_generator(modelBetas,modelOmegas)
modelD = DSSHandler.temporal_displacement_generator(modelBetas,modelOmegas,modelOmegaPrimes)
modelProcessAction = DSSHandler.process_action_solver(_time,modelD)
effectMetricModel,normalizedReferenceTimeModel,normalizedProcesstimeModel = DSSHandler.normalized_coordinates(modelOmegas,_time,modelTaus,modelProcessAction)
modelEffectParameter = DSSHandler.effect_parameter_solver(effectMetricModel)

#This will calculate the distortion between my model and prototype 
localseparation,totalseparation = DSSHandler.geodesic_separation(dataBetas,dataD,effectMetricModel,effectMetricExperiment)
standardErrorEstimate = DSSHandler.standard_error(localseparation)

# Now I make my outlet folder which will concatenate my 
#########
#Data (beta omega D tau...) Model (...) Distortion Values
#########
#my header array with the order of
__ModelHeader = np.array(["Model Beta","Model Omega","Model Omega Prime","Model Process time","Model Temporal Displacement","Model Effect Metric","Model Normalized Process Time","Model Normalized Reference Time","Model Process Action","Model Effect Parameter"])
__ExperimentHeader = np.array(["Data Beta","Data Omega","Data Omega Prime","Data Process time","Data Temporal Displacement","Data Effect Metric","Data Normalized Process Time","Data Normalized Reference Time","Data Process Action","Data Effect Parameter"])

#i do this inorder for np.savetxt to work, need to convery my floats to an array same size as the rest of my values.
__processActionModel = DSSHandler.value_to_array(modelBetas.shape,modelProcessAction)
__effectParameterModel = DSSHandler.value_to_array(modelBetas.shape,modelEffectParameter)

#now for Experiment
__processActionExperiment = DSSHandler.value_to_array(modelBetas.shape,dataProcessAction)
__effectParameterExperiment = DSSHandler.value_to_array(modelBetas.shape,dataEffectParameter)

#Now to print Seperation Values
__seperationHeader = np.array(["Local Seperation","Total Seperation","Standard Error Estimate"])
__TotalSepeartion = DSSHandler.value_to_array(modelBetas.shape,totalseparation)
__StandardErrorEstimate = DSSHandler.value_to_array(modelBetas.shape,standardErrorEstimate)



#Assemble Arrays

DataModel = np.vstack((modelBetas,modelOmegas,modelOmegaPrimes,modelTaus,modelD,effectMetricModel,normalizedProcesstimeModel,normalizedReferenceTimeModel,__processActionModel,__effectParameterModel)).T
outputModel = np.vstack((__ModelHeader,DataModel))

DataExperiment = np.vstack((dataBetas,dataOmegas,dataOmegaPrimes,dataTaus,dataD,effectMetricExperiment,normalziedProcesstimeExperiment,normalizedReferenceTimeExperiment,__processActionExperiment,__effectParameterExperiment)).T
outputExperiment = np.vstack((__ExperimentHeader,DataExperiment))

dataSeperation = np.vstack((localseparation,__TotalSepeartion,__StandardErrorEstimate)).T
outputSeperation = np.vstack((__seperationHeader,dataSeperation))

outputFile = np.hstack((outputExperiment,outputModel,outputSeperation))
np.savetxt(args.output,outputFile,delimiter=', ',fmt="%s")
