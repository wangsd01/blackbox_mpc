"""
Tutorial four: create a parallel environment for the pendulum environment and then learn the dynamics model
from random rollouts, log the data in tensorboard and use the learned model to control the agent with MPC.
"""
from tf_neuralmpc.environment_utils import EnvironmentWrapper
import logging
from tf_neuralmpc.dynamics_functions import DeterministicMLP
from tf_neuralmpc.examples.cost_funcs import pendulum_actions_reward_function, pendulum_state_reward_function
from tf_neuralmpc import Runner
import tensorflow as tf
logging.getLogger().setLevel(logging.INFO)


number_of_agents = 1
log_path = './tutorial_4'
single_env, parallel_env = EnvironmentWrapper.make_standard_gym_env("Pendulum-v0", random_seed=0,
                                                                    num_of_agents=number_of_agents)
my_runner = Runner(env=[single_env, parallel_env],
                   log_path=log_path,
                   num_of_agents=number_of_agents)
dynamics_function = DeterministicMLP()
state_size = single_env.observation_space.shape[0]
input_size = single_env.action_space.shape[0]
dynamics_function.add_layer(state_size + input_size,
                            32, activation_function=tf.math.tanh)
dynamics_function.add_layer(32, 32, activation_function=tf.math.tanh)
dynamics_function.add_layer(32, 32, activation_function=tf.math.tanh)
dynamics_function.add_layer(32, state_size)
system_dynamics_handler = my_runner.learn_dynamics_from_randomness(number_of_rollouts=40,
                                                                   task_horizon=200,
                                                                   dynamics_function=dynamics_function)
mpc_controller = my_runner.make_mpc_policy(system_dynamics_handler=system_dynamics_handler,
                                           state_reward_function=pendulum_state_reward_function,
                                           actions_reward_function=pendulum_actions_reward_function,
                                           planning_horizon=40,
                                           optimizer_name='PI2',
                                           true_model=False)

my_runner.record_rollout(horizon=300, policy=mpc_controller,
                         record_file_path=log_path+'/episode_1')
