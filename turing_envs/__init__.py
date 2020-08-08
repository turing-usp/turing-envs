from .pong import PongEnv, EasyPongEnv
from gym.envs.registration import register


register(
    id='pong-normal-v0',
    entry_point='turing_envs.pong:PongEnv',
    max_episode_steps=7_500,
)

register(
    id='pong-easy-v0',
    entry_point='turing_envs.pong:EasyPongEnv',
    max_episode_steps=7_500,
)
