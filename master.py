import os
import sys
import json
from utils.general_utils import load_config,str_to_bool,params_to_tune,generate_pars_dict
from pythia_space.pythia_functions import get_objective_func
from skopt.space import Real
from skopt.optimizer import Optimizer
from skopt import expected_minimum
import numpy as np
from genetic_algorithm import GA

def main(config_file, preprocess=False, genetic=True, bayesian=False):
    iterations = 10
    generations = iterations
    populationSize = 100
    
    
    print config_file
    config = load_config(config_file) 
    WorkHOME = os.environ['WorkHOME']

    generate_pars_dict()    

    print 'WorkHOME = {}'.format(WorkHOME)

    blocks = []
    for i in range(1,4):
        blocks.append(str_to_bool(config['block{}'.format(i)]))

    paramNames = params_to_tune(blocks)
    
    ranges = {'probStoUD': Real(low=0, high=1, prior='uniform', transform='identity'), 'probQQtoQ': Real(low=0, high=1, prior='uniform', transform='identity'), 'probSQtoQQ': Real(low=0, high=1, prior='uniform', transform='identity'), 'probQQ1toQQ0': Real(low=0, high=1, prior='uniform', transform='identity'), 'mesonUDvector': Real(low=0, high=3, prior='uniform', transform='identity'), 'mesonSvector': Real(low=0, high=3, prior='uniform', transform='identity'), 'mesonCvector': Real(low=0, high=3, prior='uniform', transform='identity'), 'mesonBvector': Real(low=0, high=3, prior='uniform', transform='identity'), 'etaSup': Real(low=0, high=1, prior='uniform', transform='identity'), 'etaPrimeSup': Real(low=0, high=1, prior='uniform', transform='identity'), 'popcornSpair': Real(low=0.9, high=1, prior='uniform', transform='identity'), 'popcornSmeson': Real(low=0.5, high=1, prior='uniform', transform='identity'), 'aLund': Real(low=0.2, high=2, prior='uniform', transform='identity'), 'bLund': Real(low=0.2, high=2, prior='uniform', transform='identity'), 'aExtraSquark': Real(low=0, high=2, prior='uniform', transform='identity'), 'aExtraDiquark': Real(low=0, high=2, prior='uniform', transform='identity'), 'rFactC': Real(low=0, high=2, prior='uniform', transform='identity'), 'rFactB': Real(low=0, high=2, prior='uniform', transform='identity'), 'sigma': Real(low=0, high=1, prior='uniform', transform='identity'), 'enhancedFraction': Real(low=0.01, high=1, prior='uniform', transform='identity'), 'enhancedWidth': Real(low=1, high=10, prior='uniform', transform='identity'), 'alphaSvalue': Real(low=0.06, high=0.25, prior='uniform', transform='identity'), 'pTmin': Real(low=0.1, high=2, prior='uniform', transform='identity'), 'pTminChgQ': Real(low=0.1, high=2, prior='uniform', transform='identity')}
    
    monashParams = {'probStoUD': 0.217, 'probQQtoQ': 0.081, 'probSQtoQQ': 0.915, 'probQQ1toQQ0': 0.0275, 'mesonUDvector': 0.50, 'mesonSvector': 0.55, 'mesonCvector': 0.88, 'mesonBvector': 2.20, 'etaSup': 0.60, 'etaPrimeSup': 0.12, 'popcornSpair': 0.90, 'popcornSmeson': 0.50, 'aLund': 0.68, 'bLund': 0.98, 'aExtraSquark': 0.00, 'aExtraDiquark': 0.97, 'rFactC': 1.32, 'rFactB': 0.855, 'sigma': 0.335, 'enhancedFraction': 0.01, 'enhancedWidth': 2.0, 'alphaSvalue': 0.1365, 'pTmin': 0.5, 'pTminChgQ': 0.5}
    professorParams = {'probStoUD': 0.19, 'probQQtoQ': 0.09, 'probSQtoQQ': 1.00, 'probQQ1toQQ0': 0.027, 'mesonUDvector': 0.62, 'mesonSvector': 0.725, 'mesonCvector': 1.06, 'mesonBvector': 3.0, 'etaSup': 0.63, 'etaPrimeSup': 0.12, 'popcornSpair': 0.50, 'popcornSmeson': 0.50, 'aLund': 0.3, 'bLund': 0.8, 'aExtraSquark': 0.00, 'aExtraDiquark': 0.50, 'rFactC': 1.00, 'rFactB': 0.67, 'sigma': 0.304, 'enhancedFraction': 0.01, 'enhancedWidth': 2.0, 'alphaSvalue': 0.1383, 'pTmin': 0.4, 'pTminChgQ': 0.4}
    monashParamValues = []
    professorParamValues = []
    for p in paramNames:
        monashParamValues.append(monashParams[p])
        professorParamValues.append(professorParams[p])
    
    paramRanges = []
    for p in paramNames:
        paramRanges.append(ranges[p])
    
    avgFitnessHistory = []
    fitnessHistory = []
    bestParams = []
    paramHistory = []
    metrics = ['chi2', 'wasserstein', 'ks_2samp', 'entropy', 'mod-log-likelihood']
    metric = metrics[3]
    prefix = metric + '_'
    
    if preprocess:
        trueFitness = get_objective_func(monashParams, metric)
        print 'distance with true params: {}'.format(trueFitness)
        
#         for p in monashParams.keys():
#             params = dict(monashParams)
#             randomFitness = 0
#             for i in range(2):
#                 params[p] = ranges[p].rvs()[0]
#                 randomFitness += get_objective_func(params, metric)
#             randomFitness /= 2
#             print 'distance after randomizing {}: {}'.format(p, randomFitness)
    
    if genetic:
        initialPopulation = [monashParamValues, professorParamValues]
        opt = GA(paramRanges, populationSize, generations, initialPopulation=initialPopulation)
        for g in range(generations):
            population = opt.ask()
            fitnesses = []
            for paramValues in population:
                params = {}
                i = 0
                for p in paramNames:
                    params[p] = paramValues[i]
                    i += 1
                fitness = get_objective_func(params, metric)
                fitnesses.append(fitness)
            print 'finished GENERATION {} out of {}'.format(g+1, generations)
            bestFit = opt.tell(population, 1/np.array(fitnesses), g)
            bestParams = bestFit[0]
            paramHistory.append(np.array(bestFit[0]))
            fitnessHistory.append(1/bestFit[1])
            avgFitnessHistory.append(1/(sum(fitnesses)/len(fitnesses)))

        np.savetxt(prefix + 'gaParamHistory.txt', np.array(paramHistory))
        np.savetxt(prefix + 'gaAvgHistory.txt', np.array(avgFitnessHistory))
        np.savetxt(prefix + 'gaMaxHistory.txt', np.array(fitnessHistory))
    
    if bayesian:
        opt = Optimizer(paramRanges, n_initial_points=populationSize)
        for g in range(iterations*populationSize):
            paramValues = opt.ask()
            params = {}
            i = 0
            for p in paramNames:
                params[p] = paramValues[i]
                i += 1
            fitness = get_objective_func(params, metric)
            print 'finished ITERATION {} out of {}'.format(g+1, iterations*populationSize)
            bestFit = opt.tell(paramValues, fitness)
            if len(bestFit.models) > 0 and (g+1) % populationSize == 0:
                # WORKAROUND TO SKOPT BUG
                bad_min = True
                while bad_min:
                    bad_min = False
                    try:
                        bestParams = expected_minimum(bestFit, n_random_starts=populationSize)[0]
                    except ValueError:
                        bad_min = True
                        print('FAILED')
                params = {}
                i = 0
                for p in paramNames:
                    params[p] = bestParams[i]
                    i += 1
                actualFitness = get_objective_func(params, metric)
                paramHistory.append(np.array(bestParams))
                fitnessHistory.append(actualFitness)

        np.savetxt(prefix + 'bayesParamHistory.txt', np.array(paramHistory))
        np.savetxt(prefix + 'bayesHistory.txt', np.array(fitnessHistory))
        
    return bestParams, fitnessHistory
        

#     new_expt = str_to_bool(config['new_expt'])
#     spearmint_dir = config['spearmint_dir']
#     start_spearmint_tune(spearmint_dir,WorkHOME,new_expt)

if __name__ == '__main__':
    main(sys.argv[1])
