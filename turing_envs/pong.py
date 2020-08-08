import sys
import numpy as np
from .import_fix import pygame
import gym
from gym.utils import seeding


class Bar:
    def __init__(self, x, y, screen_width, screen_height,
                 length=20, width=2, velocity=2, horizontal=True, np_random=np.random):
        self.np_random = np_random
        self.x = int(x)
        self.y = int(y)
        self.length = length
        self.width = width
        self.velocity = velocity
        self.horizontal = horizontal
        self.screen_width = screen_width
        self.screen_height = screen_height
        self._direction = 0

    def draw(self, screen, color=(255, 255, 255)):  # desenhar em pygame
        pygame.draw.rect(screen, color, (
                         self.x-self.width/2, self.y-self.length/2, self.width, self.length))

    # mode = machine | enemy
    # arg  = action  | ball
    def move(self, arg,  mode='human'):
        if mode == 'machine':
            actions = {
                0: lambda x: x,
                1: lambda x: x + self.velocity,
                2: lambda x: x - self.velocity,
            }
            self.y = actions[arg](self.y)

        elif mode == 'enemy':
            ball = arg
            # Depois de começar a se movimentar, o inimigo demora um tempo
            # para verificar novamente a posição da bola
            if self._direction != 0:
                if self.np_random.random() < .08:
                    self._direction = 0
            # O inimigo só consegue "ver" a bola quando ela está próxima,
            # e tem um tempo de resposta aleatório
            elif ball.x >= self.screen_width*.6 and self.np_random.random() < .85:
                self._direction = np.sign(ball.y - self.y)
            self.y += self.velocity*self._direction

        else:
            raise ValueError(f'Invalid mode: {mode}')

        self.y = np.clip(self.y, 0, self.screen_height)


class Ball:
    def __init__(self, x, y, size, velocity=1, np_random=np.random):
        self.np_random = np_random
        self.x = int(x)
        self.y = int(y)
        self.size = size
        self.abs_velocity = velocity
        self.reset_velocity()

    def reset_velocity(self):
        v = self.abs_velocity
        direction = self.np_random.uniform(np.pi/8, np.pi/3)  # first quadrant
        direction *= self.np_random.choice([-1, 1])  # right side
        direction += self.np_random.choice([0, np.pi])  # left side
        self.velocity = [
            v*np.cos(direction), -v*np.sin(direction)]

    def move(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]

    def draw(self, screen, color=(255, 255, 255)):
        pygame.draw.rect(screen, color, (
            self.x - self.size, self.y - self.size, 2*self.size, 2*self.size))

    def bounce(self, wall):
        lookup_table = {False: [-1, 1],
                        True: [1, -1]}
        if abs(self.x - wall.x) < (wall.width/2 + self.size - 1) \
                and abs(self.y - wall.y) < (wall.length/2 + self.size):
            self.velocity[0] *= lookup_table[wall.horizontal][0]
            self.velocity[1] *= lookup_table[wall.horizontal][1]
            return True
        return False


class PongEnv(gym.Env):
    _gym_disable_underscore_compat = True
    metadata = {'render.modes': ['human', 'rgb_array']}
    reward_range = (-float('inf'), float('inf'))
    action_space = gym.spaces.Discrete(3)
    observation_space = gym.spaces.Box(
        low=-np.float32('inf'), high=np.float32('inf'), shape=(4,))

    def __init__(self, height=300, width=400, repeat_actions=3,
                 bar_velocity=3, ball_velocity=2,
                 num_matches=7, fps=50):

        self.observation_space = gym.spaces.Box(
            low=np.array([0, 0, 0, 0]),
            high=np.array([width, height, width, height]),
            dtype=np.float32)

        self.height = height
        self.width = width
        self.num_matches = num_matches
        self.fps = fps
        self.clock = pygame.time.Clock()
        self.repeat_actions = repeat_actions

        param_names = ['x', 'y', 'length', 'width', 'velocity', 'horizontal']
        w, h, vel = width, height, bar_velocity
        bar_parameters = [
            # (x,    y,   len, width, vel, horizontal)
            (w/27,   h/2, h/3, w/50, vel, False),  # jogador
            (w-w/27, h/2, h/3, w/50, vel, False),  # oponente
            (w/2,    0,   5,   w,    0,   True),   # teto
            (w/2,    h,   5,   w,    0,   True),   # chão
            (0,      h/2, h,   5,    0,   False),  # parede esq.
            (w,      h/2, h,   5,    0,   False),  # parede dir.
        ]
        # Obs: as paredes esquerda e direita têm propósito puramente estético

        self.bars = []
        for bar in bar_parameters:
            kwargs = dict(zip(param_names, bar))
            self.bars.append(
                Bar(screen_width=width, screen_height=height, **kwargs))

        self.control_bar = self.bars[0]
        self.other_bar = self.bars[1]
        self.left_wall = self.bars[4]
        self.right_wall = self.bars[5]

        self.ball = Ball(x=width/2, y=height/2, size=10,
                         velocity=ball_velocity)

        self.seed()
        self.viewer = None
        self.screen = None

    def reset_match(self):
        self.ball.x, self.ball.y = self.width/2, self.height/2
        self.control_bar.y = self.height/2
        self.other_bar.y = self.height/2
        self.ball.reset_velocity()

    def _get_state(self):
        return np.array([self.control_bar.x, self.control_bar.y,
                         self.ball.x, self.ball.y])

    def reset(self):
        self.reset_match()
        self.done = False
        self.score = [0, 0]
        return self._get_state()

    def step(self, action):
        reward = 0
        for _ in range(self.repeat_actions):
            reward += self._step(action)
            if self.done:
                break
        return self._get_state(), reward, self.done, {}

    def _step(self, action):
        if self.done:
            return

        self.control_bar.move(action, mode='machine')
        self.other_bar.move(self.ball, mode='enemy')
        self.ball.move()

        for bar in self.bars:
            self.ball.bounce(bar)

        if self.ball.bounce(self.left_wall):
            player_scored = False
            self.score[1] += 1
        elif self.ball.bounce(self.right_wall):
            player_scored = True
            self.score[0] += 1
        else:  # no points
            return 0

        reward = 500
        if max(self.score) > self.num_matches / 2:
            self.done = True
            reward += 2000
        self.reset_match()
        return reward if player_scored else -reward

    def draw(self):
        if self.screen is None:
            self.screen = pygame.Surface((self.width, self.height))
        self.screen.fill((20, 20, 20))
        for bar in self.bars:
            bar.draw(self.screen)
        self.ball.draw(self.screen)

    def render(self, mode='human', wait=True):
        if wait:
            self.clock.tick(self.fps)

        self.draw()
        img = pygame.surfarray.array3d(self.screen).astype(np.uint8)

        # Conversão de eixos [y][x][canal] para [x][y][canal]
        img = np.transpose(img, [1, 0, 2])

        if mode == 'rgb_array':
            return img
        elif mode == 'human':
            if self.viewer is None:
                from gym.envs.classic_control import rendering
                self.viewer = rendering.SimpleImageViewer(maxwidth=self.width)
            self.viewer.imshow(img)
            self.viewer.window.set_caption(
                f'Pong - {self.score[0]} x {self.score[1]} ({sys.argv[0]})')
        else:
            return super().render(mode=mode)

    def close(self):
        if self.viewer:
            self.viewer.close()
            self.viewer = None

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        self.ball.np_random = self.np_random
        for bar in self.bars:
            bar.np_random = self.np_random
        return [seed]


class EasyPongEnv(PongEnv):
    observation_space = gym.spaces.Box(
        low=-np.float32('inf'), high=np.float32('inf'), shape=(2,))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        low = self.observation_space.low
        high = self.observation_space.high
        self.observation_space = gym.spaces.Box(
            low=np.array([low[0] - high[2], low[1] - high[3]]),
            high=np.array([high[0] - low[2], high[1] - low[3]]),
            dtype=np.float32)

    def _get_state(self):
        dx = self.control_bar.x - self.ball.x  # s[0] - s[2]
        dy = self.control_bar.y - self.ball.y  # s[1] - s[3]
        return np.array([dx, dy])
