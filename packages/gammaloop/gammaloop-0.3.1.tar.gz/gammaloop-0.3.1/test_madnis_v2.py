# type: ignore
import sys
import os
import logging
import torch
try:
    from gammaloop.interface.gammaloop_interface import *
except:
    gammaloop_path = os.path.abspath(os.path.join(os.getcwd(), "python"))
    print(gammaloop_path)
    sys.path.insert(0, gammaloop_path)
    try:
        from gammaloop.interface.gammaloop_interface import *
        from gammaloop.misc.common import *
        print('\n'.join(["",
                         "Note: gammaLoop could not be loaded from default PYTHONPATH.",
                         f"Path '{gammaloop_path}' was successfully used instead.", ""]))
    except:
        print('\n'.join([
            "ERROR: Could not import Python's gammaloop module.",
            "Add '<GAMMALOOP_INSTALLATION_DIRECTORY>/python' to your PYTHONPATH."]))
        sys.exit(1)

from madnis.integrator import Integrator
from pprint import pp

#############
# PARAMETERS
#############

GL_LEARNING_RATE = 1.5
INTEGRATION_STATISTICS = 100_000
TRAINING_STATISTICS = 100
SAMPLING = "tropical"
# SAMPLING = "spherical"
# PROCESS = 'examples/cards/scalar_mercedes'
# PROCESS = 'GL_OUTPUT_1L_AA_AAAA'
PROCESS = 'GL_OUTPUT_1L_AA_AAAA_euclidean'

PHASE = 'real'

######
# RUN
######

SAMPLING_OPTIONS = {
    # Tropical sampling
    "tropical": "set sampling {'type': 'discrete_graph_sampling', 'subtype': 'tropical', 'upcast_on_failure': True}",
    # Regular sampling with cartesian product of spherical parameterisation
    "spherical": "set sampling {'type':'default'}"
}

PROCESSES = {
    'examples/cards/scalar_mercedes': {
        'generate': """
            import_graphs ./python/gammaloop/tests/test_data/graph_inputs/ltd_topology_f.dot
            output examples/cards/scalar_mercedes
            """,
        'name': 'ltd_topology_f',
        'load': """
            set e_cm 1.
            set externals.data.momenta [[0.,0.,0.,1.],]
            set use_ltd False""",
        'spherical_dimensions': 9,
        'tropical_dimensions': 23,
        'target': '(-5.26647e-6,0.)'
    },
    'GL_OUTPUT_1L_AA_AAAA': {
        'generate': """
            import_model sm-full
            import_graphs python/gammaloop/tests/test_data/graph_inputs/physical_1L_6photons.dot
            output GL_OUTPUT_1L_AA_AAAA
            """,
        'load': """
            set_model_param mz 91.188 -nu
            set_model_param gf 1.19874983504616246e-5 -nu
            set_model_param mt 173.0 -nu
            set_model_param ymt 173.0 -nu
            set_model_param aewm1 128.93 -nu
            set_model_param update_only 0.
            set externals.data.momenta [\
[500.0,0.,-300.,400.],\
[500.0,0.,300.,-400.],\
[88.551333054502976,-22.100690287689979,40.080353191685333,-75.805430956936632],\
[328.32941922709853,-103.84961188345630,-301.93375538954012,76.494921387165888],\
[152.35810946743061,-105.88095966659220,-97.709638326975707,49.548385226792817],\
"dependent",\
]
            set integrated_phase 'imag'
            set use_ltd False
            set rotation_axis [{"type":"x"}]
            set rotate_numerator True
            set externals.data.helicities [-1,-1,-1,-1,-1,-1]
        """,
        'name': 'physical_1L_6photons',
        'spherical_dimensions': 3,
        'tropical_dimensions': 15,
        'target': '(9.27759500687454717e-11,3.68394576249870544e-11)'
    },
    'GL_OUTPUT_1L_AA_AAAA_euclidean': {
        'generate': """
            import_model sm-full
            import_graphs python/gammaloop/tests/test_data/graph_inputs/physical_1L_6photons.dot
            output GL_OUTPUT_1L_AA_AAAA_euclidean
            """,
        'load': """
            set_model_param mz 91.188 -nu
            set_model_param gf 1.19874983504616246e-5 -nu
            set_model_param mt 1500.0 -nu
            set_model_param ymt 1500.0 -nu
            set_model_param aewm1 128.93 -nu
            set_model_param update_only 0.
            set externals.data.momenta [\
[500.0,0.,-300.,400.],\
[500.0,0.,300.,-400.],\
[88.551333054502976,-22.100690287689979,40.080353191685333,-75.805430956936632],\
[328.32941922709853,-103.84961188345630,-301.93375538954012,76.494921387165888],\
[152.35810946743061,-105.88095966659220,-97.709638326975707,49.548385226792817],\
"dependent",\
]
            set integrated_phase 'imag'
            set use_ltd False
            set rotation_axis [{"type":"x"}]
            set rotate_numerator True
            set externals.data.helicities [-1,-1,-1,-1,-1,-1]
        """,
        'name': 'physical_1L_6photons',
        'spherical_dimensions': 3,
        'tropical_dimensions': 15,
        'target': '(1.22898408452706e-13,3.94362534040412e-13)'
    },
}

GL_DEBUG = False
register_symbolica()
gL_runner = GammaLoop()
gL_runner.run(CommandList.from_string("""import_model scalars-full"""))

# Generate integrand code if not already done
if not os.path.isdir(PROCESS):
    print("Generating integrand code...")
    gL_runner.run(CommandList.from_string(PROCESSES[PROCESS]['generate']))

# Load integrand code
gL_runner.run(CommandList.from_string("""
    launch %s
    set integrated_phase '%s'
    %s
    """ % (PROCESS, PHASE, SAMPLING_OPTIONS[SAMPLING])))
gL_runner.run(CommandList.from_string(PROCESSES[PROCESS]['load']))

GL_CONSOLE_HANDLER.setLevel(logging.INFO)

# Perform the integration with gammaLoop
gL_runner.run(CommandList.from_string("""
    set continuous_dim_learning_rate %f
    set n_start %d
    set n_max %d
    integrate %s -c 10 -r -t %s
""" % (GL_LEARNING_RATE,
       int(INTEGRATION_STATISTICS/10.),
       INTEGRATION_STATISTICS,
       PROCESSES[PROCESS]['name'],
       PROCESSES[PROCESS]['target'],
       )))


def itg(batch):
    res = []
    for xs in batch:
        # print(xs.tolist())
        res.append(gL_runner.rust_worker.inspect_integrand(
            PROCESSES[PROCESS]['name'], xs.tolist(), tuple([0,]), False, False, False)[0 if PHASE == 'real' else 1])
    # print(res)
    return torch.FloatTensor(res)


integrator = Integrator(
    itg, dims=PROCESSES[PROCESS]['%s_dimensions' % SAMPLING])


def callback(status):
    if (status.step + 1) % 10 == 0:
        print(f"Batch {status.step + 1}: loss={status.loss:.5f}")


GL_CONSOLE_HANDLER.setLevel(logging.CRITICAL)
integrator.train(TRAINING_STATISTICS, callback)
print("Integrating...")
result, error = integrator.integrate(INTEGRATION_STATISTICS)
print(f"Integration result: {result:.5e} +- {error:.5e}")

pp(integrator.integration_metrics(INTEGRATION_STATISTICS))
