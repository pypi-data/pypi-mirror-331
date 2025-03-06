import numpy as np

def data_normalizer(data, inputs=0):
    """Normalizes Data to Users Input, Creates conserved quantity for DSS analysis

    Parameters
    ----------
    data : numpy.ndarray
        Data set to be normalized
    inputs : dictionary
        Input file with corresponding model and data settings
    
    Returns
    -------
    Betas : numpy.ndarray
        Array with normalized data (array of Beta's in DSS terminology)
    """
    if inputs["normalize"] == "first":
        return (data / data[0])
    elif inputs["normalize"] == "last":
        return (data / data[-1])
    else:
        # default normalization is first
        return (data / data[0])

def time_derivative(data, time):
    """Gets timed derivative using finite differences (can calculate omega or omega prime, first and second time derivative of beta respectively)

    Parameters
    ----------
    data : numpy.ndarray
        Data set to be normalized
    time : numpy.ndarray
        Reference time value of datasets
    
    Returns
    -------
    timederivative : numpy.ndarray
        Array with normalized data (array of omegas's in DSS terminology)
    """
    return np.gradient(data,time)

def model_data_generator(time,inputs):
    """Generates the model dataset for comparison to experimental data

    Parameters
    ----------
    data : inputs
        Input file with model values specified 
    time : numpy.ndarray
        Reference time value of datasets
    
    Returns
    -------
    ModelData
        Array with non-normalized data generated from model
    """
     
    if inputs["model"] == "quad":
        data  = (float(inputs["A"])*time**2)+(float(inputs["B"])*time)+float(inputs["C"])
        return data

    elif inputs["model"] == "exp":
        data = (float(inputs["A"])*np.exp(float(inputs["B"])*time))+float(inputs["C"])
        return data
    else:
        raise ValueError(
            "Incorrect Model Selection"
        )
          
def process_time_generator(beta,omega):

    """Generates process time from an input of beta and omega values

    Parameters
    ----------
    beta : numpy.ndarray
        Array with normalized conserved quantity of interest (Betas)
    omega : numpy.ndarray
        Array with normalized agents of change (Omegas)
    
    Returns
    -------
    Tau : numpy.ndarray
        Array with process time values
    """
    return beta/omega

def temporal_displacement_generator(beta,omega,omegaprimes):
    """Generates the Temporal Displacement value.

    Parameters
    ----------
    beta : numpy.ndarray
        Array with normalized conserved quantity of interest (Betas)
    omega : numpy.ndarray
        Array with normalized agents of change (Omegas)
    omegaprimes : numpy.ndarray
        Array with time derivative of Omegas
    
    Returns
    -------
    D : numpy.ndarray
        Array with Temporal Displacement Values
    """
    return (-(beta*omegaprimes)/(omega**2))

def process_action_solver(time,temporalDisplacement):
    """Finds the process action (tau_s) using numerical integration. Eq 12

    Parameters
    ----------
    time : numpy.ndarray
        Array with reference time values
    temporalDisplacement : numpy.ndarray
        Array with Temporal Displacement Values (D)
    
    Returns
    -------
    process action: float
        Value of Process time
    """
    integrand = 1+temporalDisplacement
    _sum = np.trapezoid(integrand, time)
    return _sum

def normalized_coordinates(omega,referencetime,processtime,processaction):
    """Returns the normalized coordinates and parameters to assess scale distortion. EQ 14a-d

    Parameters
    ----------
    omega : numpy.ndarray
        Array with omega values
    referencetime : numpy.ndarray
        Array with reference time values
    processtime : numpy.ndarray
        Array with process time values
    processaction : float
        Float value of process action
    
    Returns
    -------
    effectmetric : numpy.ndarray
        Array of effect metric values
    normalizedreferencetime :numpy.ndarray
        Array of normalized reference time values
    normalized reference time :numpy.ndarray
        Array of normalzied process time values
        
    """
    
    return (omega*processaction),(referencetime/processaction),(processtime/processaction)

def effect_parameter_solver(effectmetric):
    """Returns the effect parameter. EQ 20

    Parameters
    ----------
    effectmetric : numpy.ndarray
        Array with effect metric values
    
    Returns
    -------
    effectparameter : float
        Float value of effect parameter.
    """

    return (np.sum(effectmetric))

def geodesic_separation(dataBeta,dataD,modelEffectMetric,dataEffectMetric):
    """Returns the geodesic separation at each process time step. Eq 45 in DSS bubble applications

    Parameters
    ----------
    dataBeta : numpy.ndarray
        Array with normalized conserved quantity of interest of the experiment
    modelEffectMetric : numpy.ndarray
        Array with model's effect metric values
    dataEffectMetric : numpy.ndarray
        Array with experiment's effect metric values
    dataD : numpy.ndarray
        Array with temporal displacement rate values of the experiment
    Returns
    -------
    Local separation : numpy.ndarray
        Array with geodesic separation values at each process timestep between model and prototype.
    Total separation : float
        float value of total geodesic separation
    """
    localseparation = (dataBeta*np.sqrt(abs(dataD))*((1/dataEffectMetric)-(1/modelEffectMetric)))
    totalseparation = np.sum(abs(localseparation))
    return localseparation,totalseparation

def standard_error(localseparation):
    """Returns an estimate of the standard error. 95% of values fall within +- 2sigma_est values. EQ 47 in DSS Bubble Dynamics Applications.

    Parameters
    ----------
    localseparation : numpy.ndarray
        Array with normalized conserved quantity of interest of the data local separation between model and prototype at each process time point
    
    Returns
    -------
    sigmaest : float
        Float value of estimate of standard error (total distortion) 
    """
    return np.sqrt(((np.sum(localseparation**2))/len(localseparation)))

def value_to_array(size,value):
    """Returns an array with the first value being the value of interest while the rest are numpy.nan data type, this is for data saving purposes

    Parameters
    ----------
    size : int
        Int value with size of array
    value : float
        float value of interest
    Returns
    -------
    productArray : numpy.ndarray
        Array with value of interest in first element while rest is numpy.nan
    """
    __fillerarray = np.full((size),np.nan)
    __fillerarray[0] = value
    return __fillerarray