import logging

from synthrl.env import MAEnvironment
from synthrl.utils import Timer

logger = logging.getLogger(__name__)

def synthesize_from_oracle(dsl=None, synthesizer=None, verifier=None, oracle=None, ioset=[], budget=None, testing=None, testing_opt={}):
  # gets callable dsl
  #      synthsizer and verifier agent
  #      callable oracle and initial ioset
  #      time budget
  # and returns synthesized program
  trail = 0
  program = None
  for t in Timer(budget):
    trail += 1
    logger.info('[{:.2f}s] {} trails'.format(t.total_seconds(), trail))

    env = MAEnvironment(ioset=ioset, dsl=dsl, testing=lambda pgm1, pgm2: testing(pgm1, pgm2, **testing_opt))
    state, (r_syn, r_ver), (t_syn, t_ver) = env.reset()

    while not t_syn:
      action = synthesizer.take(state, env.action_space)
      state, (r_syn, r_ver), (t_syn, t_ver) = env.step(action)
    
    if r_syn <= 0:
      logger.warning('Fail to synthesize the program.')
      break

    program = env.program

    while not t_ver:
      action = verifier.take(state, env.action_space)
      state, (r_syn, r_ver), (_, t_ver) = env.step(action)

    if r_ver <= 0:
      logger.info('Fail to generate distinguishing input.')
      break

    distingusing_input = env.distingusing_input
    ioset.append((distingusing_input, oracle(distingusing_input)))

  return program
  
def synthesize_interactively(dsl=None, synthesizer=None, verifier=None):
  raise NotImplementedError