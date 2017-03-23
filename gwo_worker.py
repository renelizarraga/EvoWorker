import uuid
import os
import numpy as np

from EvoloPy import GWO as gwo
from worker import  Worker

class GWO_Worker(Worker):
    def setup(self):
        pass
        #evospace_sample = self.space.get_sample(self.conf['sample_size'])

    def get(self):
        self.evospace_sample = self.space.get_sample(self.conf['sample_size'])
        pop = [cs['chromosome'] for cs in self.evospace_sample['sample']]
        return np.array(pop)

    def put_back(self, s):
        final_pop = [{"chromosome": tuple(ind), "id": None,
                      "fitness": {"DefaultContext": 0, "score": 0}} for ind in
                     s.pop]

        self.evospace_sample['sample'] = final_pop

        if 'benchmark' in self.conf:
            experiment_id = 'experiment_id' in conf and conf['experiment_id'] or 0
            self.evospace_sample['benchmark_data'] = {'params': self.params, 'evals': s.convergence, 'algorithm': 'GWO',
                                                      'benchmark': self.conf['function'],
                                                      'instance': self.conf['instance'],
                                                      'worker_id': str(self.worker_uuid),
                                                      'experiment_id': experiment_id,
                                                      'dim': self.conf['dim'],
                                                      'fopt': self.function.getfopt()}
        self.space.put_sample(self.evospace_sample)



    def run(self, pop):
        self.function.__name__ = "F%s instance %s" % (self.conf['function'], self.conf['instance'])
        return gwo.GWO(objf=self.function, lb=conf['lb'], ub=conf['ub'], dim=self.conf['dim'], SearchAgents_no=conf['sample_size'], Max_iter=conf['NGEN'], Positions=pop, fopt=self.function.getfopt())


if __name__ == "__main__":
    conf = {}
    conf['function'] = 3
    conf['instance'] = 1
    conf['dim'] = 5
    conf['sample_size'] = 100
    conf['FEmax'] = 500000
    conf['evospace_url'] = 'EVOSPACE_URL' in os.environ and os.environ['EVOSPACE_URL'] or '127.0.0.1:3000/evospace'
    conf['pop_name'] = 'POP_NAME' in os.environ and os.environ['POP_NAME'] or 'test_pop'
    conf['max_samples'] = 'MAX_SAMPLES' in os.environ and int(os.environ['MAX_SAMPLES']) or 100
    conf['benchmark'] = 'BENCHMARK' in os.environ
    conf['experiment_id'] = 'EXPERIMENT_ID' in os.environ and int(os.environ['EXPERIMENT_ID']) or str(uuid.uuid1())
    conf['lb'] = 'LOWER_BOUND' in os.environ and int(os.environ['LOWER_BOUND']) or -5
    conf['ub'] = 'UPPER_BOUND' in os.environ and int(os.environ['UPPER_BOUND']) or 5
    conf['NGEN'] = 'NGEN' in os.environ and int(os.environ['NGEN']) or  10
    conf['experiment_id'] = 3

    worker = GWO_Worker(conf)

    print "Ready"
    for i  in range(conf['max_samples']):
        pop = worker.get()
        s = worker.run(pop)
        print s.best, '%+10.9e' % (s.best - worker.function.getfopt() + 1e-8)
        worker.put_back(s)