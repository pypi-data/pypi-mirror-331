import numpy as np
from src.PythonDSSAnalysis import DSSHandler as DSS    
# this is my test file which will run with pytest to test simple cases of my function 
# Ran with pytest test.py -vv for each specific test.
def test_data_normalzier_first():
    quad_dict = {
        "normalize": "first"
    }
    data = np.array([1,2,3,4,5])
    obs = DSS.data_normalizer(data, quad_dict)
    exp = np.array([1,2,3,4,5])
    assert exp.all() == obs.all()

def test_data_normalzier_last():
    quad_dict = {
        "normalize": "last"
    }
    data = np.array([1,2,3,4,5])
    obs = DSS.data_normalizer(data, quad_dict)
    exp = np.array([0.2,.4,.6,.8,1])
    assert np.allclose(exp,obs)

def test_time_derivative():
    #Trivial Solution no change with time
    data =np.array([1,1,1])
    time =np.array([1,2,3])
    exp = np.array([0,0,0])
    obs = DSS.time_derivative(data,time)
    assert np.allclose(exp,obs)

def test_time_derivative_linear():
    #Linear time change
    data = np.array([1,2,3])
    time = np.array([1,2,3])
    exp = np.array([1,1,1])
    obs = DSS.time_derivative(data,time)
    assert np.allclose(exp,obs)

def test_model_data_generator_quad():
    quad_dict = {
        "A" : "1",
        "B" : "1",
        "C" : "1",
        "model":"quad"
    }
    time = np.array([0,1,2])
    obs = DSS.model_data_generator(time,quad_dict)
    exp = np.array([1,3,7])
    assert np.allclose(exp,obs)

def test_model_data_generator_exp():
    quad_dict = {
        "A" : "1",
        "B" : "1",
        "C" : "1",
        "model":"exp"
    }
    time = np.array([-100,0,1])
    obs = DSS.model_data_generator(time,quad_dict)
    exp = np.array([1,2,3.71828])
    assert np.allclose(exp,obs)

def test_process_time_generator():
    beta = np.array([2,4,6,8])
    omega = np.array([1,2,3,4])
    obs = DSS.process_time_generator(beta,omega)
    exp =np.array([2,2,2,2])
    assert np.allclose(exp,obs)

def test_temporal_displacement_generator():
    beta = np.array([4,4,4])
    omega = np.array([1,2,3])
    omegaprime = np.array([1,2,3])
    obs = DSS.temporal_displacement_generator(beta,omega,omegaprime)
    exp = np.array([-4,-2,-(4/3)])
    assert np.allclose(exp,obs)

def test_process_action_solver():
    time =np.array([1,2,3])
    D = np.array([1,1,1])
    obs = DSS.process_action_solver(time,D)
    exp = 4
    assert np.allclose(obs,exp)

def test_normalized_coordinates():
    omega = np.array([1,2,3])
    reftime = np.array([1,2,3])
    proctime = np.array([1,2,3])
    processaction = 0.5
    obs1,obs2,obs3 = DSS.normalized_coordinates(omega,reftime,proctime,processaction)
    exp1 = np.array([0.5,1,1.5])
    exp2 = np.array([2,4,6])
    exp3 = np.array([2,4,6])
    assert np.allclose(obs1,exp1)
    assert np.allclose(obs2,exp2)
    assert np.allclose(obs3,exp3)

def test_effect_parameter_solver():
    effectmetric = np.array([1,2,3,4])
    obs = DSS.effect_parameter_solver(effectmetric)
    exp = 10
    assert np.allclose(obs,exp)

def test_geodesic_separation():
    beta = np.array([1,2,3])
    D = np.array([1,1,1])
    modelEffectMetric = np.array([2,3,4])
    dataEffectMetric = np.array([1,2,3])
    obs1,obs2 = DSS.geodesic_separation(beta,D,modelEffectMetric,dataEffectMetric)
    exp1 = np.array([0.5,(1/3),(1/4)])
    exp2 = np.sum(exp1)
    assert np.allclose(exp1,obs1)
    assert np.allclose(exp2,obs2)

def test_standard_error():
    localsep = np.array([2,3,4])
    obs = DSS.standard_error(localsep)
    exp = (np.sqrt(29/3))
    assert np.allclose(obs,exp)

def test_value_to_array():
    value = 5
    size = 3
    obs = DSS.value_to_array(size,value)
    exp = np.array([5,np.nan,np.nan])
    assert np.allclose(obs,exp,equal_nan=True)