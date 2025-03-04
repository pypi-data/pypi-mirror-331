# Copyright (c) Facebook, Inc. and its affiliates.
from minihack import MiniHackNavigation, LevelGenerator
from nle.nethack import Command, CompassDirection
from minihack.envs import register
import gymnasium as gym
from nle.nethack.nethack import TERMINAL_SHAPE


MOVE_AND_KICK_ACTIONS = tuple(
    list(CompassDirection) + [Command.OPEN, Command.KICK]
)


class MiniGridHack(MiniHackNavigation):
    def __init__(self, *args, **kwargs):
        # Only ask users to install minigrid if they actually need it
        try:
            import minigrid  # noqa: F401
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "To use MiniGrid-based environments, please install"
                " minigrid: pip3 install minigrid"
            )

        height, width = TERMINAL_SHAPE
        height -= 3  # adjust for topline -1 and bottomlines -2
        width -= 4  # adjust for left -2 and right -2 borders
        self.minigrid_env = gym.make(
            kwargs.pop("env_name"), width=width, height=height
        )
        self.num_mon = kwargs.pop("num_mon", 0)
        self.num_trap = kwargs.pop("num_trap", 0)
        self.door_state = kwargs.pop("door_state", "closed")
        if self.door_state == "locked":
            kwargs["actions"] = kwargs.pop("actions", MOVE_AND_KICK_ACTIONS)

        lava_walls = kwargs.pop("lava_walls", False)
        if lava_walls:
            self.wall = "L"
        else:
            self.wall = "|"

        des_file = self.get_env_desc()
        super().__init__(*args, des_file=des_file, **kwargs)

    def get_env_map(self, env):
        door_pos = []
        goal_pos = None
        empty_strs = 0
        empty_str = True
        env_map = []

        for j in range(env.unwrapped.grid.height):
            str = ""
            for i in range(env.unwrapped.width):
                c = env.unwrapped.grid.get(i, j)
                if c is None:
                    str += "."
                    continue
                empty_str = False
                if c.type == "wall":
                    str += self.wall
                elif c.type == "door":
                    str += "+"
                    door_pos.append((i, j - empty_strs))
                elif c.type == "floor":
                    str += "."
                elif c.type == "lava":
                    str += "L"
                elif c.type == "goal":
                    goal_pos = (i, j - empty_strs)
                    str += "."
                elif c.type == "player":
                    str += "."
            if not empty_str and j < env.unwrapped.grid.height - 1:
                if set(str) != {"."}:
                    str = str.replace(".", " ", str.index(self.wall))
                    inv = str[::-1]
                    str = inv.replace(".", " ", inv.index(self.wall))[::-1]
                    env_map.append(str)
            elif empty_str:
                empty_strs += 1

        start_pos = (
            int(env.unwrapped.agent_pos[0]),
            int(env.unwrapped.agent_pos[1]) - empty_strs,
        )
        env_map = "\n".join(env_map)

        return env_map, start_pos, goal_pos, door_pos

    def get_env_desc(self):
        self.minigrid_env.reset()
        env = self.minigrid_env

        map, start_pos, goal_pos, door_pos = self.get_env_map(env)

        lev_gen = LevelGenerator(map=map)

        lev_gen.add_goal_pos(goal_pos)
        lev_gen.set_start_pos(start_pos)

        for d in door_pos:
            lev_gen.add_door(self.door_state, d)

        lev_gen.wallify()

        for _ in range(self.num_mon):
            lev_gen.add_monster()

        for _ in range(self.num_trap):
            lev_gen.add_trap()

        return lev_gen.get_des()

    def seed(self, core=None, disp=None, reseed=False):
        """The signature of this method corresponds to that of NLE base class.
        For more information see
        https://github.com/heiner/nle/blob/main/nle/env/base.py.

        Sets the state of the NetHack RNGs after the next reset.

        Arguments:
            core [int or None]: Seed for the core RNG. If None, chose a random
                value.
            disp [int or None]: Seed for the disp (anti-TAS) RNG. If None, chose
                a random value.
            reseed [boolean]: As an Anti-TAS (automation) measure,
                NetHack 3.6 reseeds with true randomness every now and then. This
                flag enables or disables this behavior. If set to True,
                trajectories won't be reproducible.

        Returns:
            [tuple] The seeds supplied, in the form (core, disp, reseed).
        """
        self.minigrid_env.seed(core)
        return super().seed(core, disp, reseed)

    def reset(self, options=dict(wizkit_items=None), **kwargs):
        des_file = self.get_env_desc()
        self.update(des_file)
        return super().reset(options=options, **kwargs)


class MiniHackMultiRoomN2(MiniGridHack):
    def __init__(self, *args, **kwargs):
        kwargs["max_episode_steps"] = kwargs.pop("max_episode_steps", 40)
        super().__init__(
            *args, env_name="MiniGrid-MultiRoom-N2-S4-v0", **kwargs
        )


class MiniHackMultiRoomN4(MiniGridHack):
    def __init__(self, *args, **kwargs):
        kwargs["max_episode_steps"] = kwargs.pop("max_episode_steps", 120)
        super().__init__(
            *args, env_name="MiniGrid-MultiRoom-N4-S5-v0", **kwargs
        )


class MiniHackMultiRoomN6(MiniGridHack):
    def __init__(self, *args, **kwargs):
        kwargs["max_episode_steps"] = kwargs.pop("max_episode_steps", 240)
        super().__init__(*args, env_name="MiniGrid-MultiRoom-N6-v0", **kwargs)


register(
    id="MiniGrid-MultiRoom-N10-v0",
    entry_point="minigrid.envs:MultiRoomEnv",
    kwargs={"minNumRooms": 10, "maxNumRooms": 10},
)


class MiniHackMultiRoomN10(MiniGridHack):
    def __init__(self, *args, **kwargs):
        kwargs["max_episode_steps"] = kwargs.pop("max_episode_steps", 360)
        super().__init__(*args, env_name="MiniGrid-MultiRoom-N10-v0", **kwargs)


# open door version of the above envs - methods with message-based bonuses tend to fail on these
# because there is no message "the door opens" when visiting a new room


class MiniHackMultiRoomN6OpenDoor(MiniGridHack):
    def __init__(self, *args, **kwargs):
        kwargs["max_episode_steps"] = kwargs.pop("max_episode_steps", 240)
        kwargs["door_state"] = kwargs.pop("door_state", "open")
        super().__init__(*args, env_name="MiniGrid-MultiRoom-N6-v0", **kwargs)


class MiniHackMultiRoomN10OpenDoor(MiniGridHack):
    def __init__(self, *args, **kwargs):
        kwargs["max_episode_steps"] = kwargs.pop("max_episode_steps", 360)
        kwargs["door_state"] = kwargs.pop("door_state", "open")
        super().__init__(*args, env_name="MiniGrid-MultiRoom-N10-v0", **kwargs)


register(
    id="MiniHack-MultiRoom-N2-v0",
    entry_point="minihack.envs.minigrid:MiniHackMultiRoomN2",
)
register(
    id="MiniHack-MultiRoom-N4-v0",
    entry_point="minihack.envs.minigrid:MiniHackMultiRoomN4",
)
register(
    id="MiniHack-MultiRoom-N6-v0",
    entry_point="minihack.envs.minigrid:MiniHackMultiRoomN6",
)
register(
    id="MiniHack-MultiRoom-N10-v0",
    entry_point="minihack.envs.minigrid:MiniHackMultiRoomN10",
)
register(
    id="MiniHack-MultiRoom-N6-OpenDoor-v0",
    entry_point="minihack.envs.minigrid:MiniHackMultiRoomN6OpenDoor",
)
register(
    id="MiniHack-MultiRoom-N10-OpenDoor-v0",
    entry_point="minihack.envs.minigrid:MiniHackMultiRoomN10OpenDoor",
)


# MiniGrid: LockedMultiRoom
class MiniHackMultiRoomN2Locked(MiniGridHack):
    def __init__(self, *args, **kwargs):
        kwargs["max_episode_steps"] = kwargs.pop("max_episode_steps", 40)
        kwargs["door_state"] = "locked"
        super().__init__(
            *args, env_name="MiniGrid-MultiRoom-N2-S4-v0", **kwargs
        )


class MiniHackMultiRoomN4Locked(MiniGridHack):
    def __init__(self, *args, **kwargs):
        kwargs["max_episode_steps"] = kwargs.pop("max_episode_steps", 120)
        kwargs["door_state"] = "locked"
        super().__init__(
            *args, env_name="MiniGrid-MultiRoom-N4-S5-v0", **kwargs
        )


class MiniHackMultiRoomN6Locked(MiniGridHack):
    def __init__(self, *args, **kwargs):
        kwargs["max_episode_steps"] = kwargs.pop("max_episode_steps", 240)
        kwargs["door_state"] = "locked"
        super().__init__(*args, env_name="MiniGrid-MultiRoom-N6-v0", **kwargs)


register(
    id="MiniHack-MultiRoom-N2-Locked-v0",
    entry_point="minihack.envs.minigrid:MiniHackMultiRoomN2Locked",
)
register(
    id="MiniHack-MultiRoom-N4-Locked-v0",
    entry_point="minihack.envs.minigrid:MiniHackMultiRoomN4Locked",
)
register(
    id="MiniHack-MultiRoom-N6-Locked-v0",
    entry_point="minihack.envs.minigrid:MiniHackMultiRoomN6Locked",
)


# MiniGrid: LavaMultiRoom
class MiniHackMultiRoomN2Lava(MiniGridHack):
    def __init__(self, *args, **kwargs):
        kwargs["max_episode_steps"] = kwargs.pop("max_episode_steps", 40)
        kwargs["lava_walls"] = True
        super().__init__(
            *args, env_name="MiniGrid-MultiRoom-N2-S4-v0", **kwargs
        )


class MiniHackMultiRoomN4Lava(MiniGridHack):
    def __init__(self, *args, **kwargs):
        kwargs["max_episode_steps"] = kwargs.pop("max_episode_steps", 120)
        kwargs["lava_walls"] = True
        super().__init__(
            *args, env_name="MiniGrid-MultiRoom-N4-S5-v0", **kwargs
        )


class MiniHackMultiRoomN6Lava(MiniGridHack):
    def __init__(self, *args, **kwargs):
        kwargs["max_episode_steps"] = kwargs.pop("max_episode_steps", 240)
        kwargs["lava_walls"] = True
        super().__init__(*args, env_name="MiniGrid-MultiRoom-N6-v0", **kwargs)


class MiniHackMultiRoomN10Lava(MiniGridHack):
    def __init__(self, *args, **kwargs):
        kwargs["max_episode_steps"] = kwargs.pop("max_episode_steps", 360)
        kwargs["lava_walls"] = True
        super().__init__(*args, env_name="MiniGrid-MultiRoom-N10-v0", **kwargs)


class MiniHackMultiRoomN6LavaOpenDoor(MiniGridHack):
    def __init__(self, *args, **kwargs):
        kwargs["max_episode_steps"] = kwargs.pop("max_episode_steps", 240)
        kwargs["lava_walls"] = True
        kwargs["door_state"] = kwargs.pop("door_state", "open")
        super().__init__(*args, env_name="MiniGrid-MultiRoom-N6-v0", **kwargs)


class MiniHackMultiRoomN10LavaOpenDoor(MiniGridHack):
    def __init__(self, *args, **kwargs):
        kwargs["max_episode_steps"] = kwargs.pop("max_episode_steps", 360)
        kwargs["lava_walls"] = True
        kwargs["door_state"] = kwargs.pop("door_state", "open")
        super().__init__(*args, env_name="MiniGrid-MultiRoom-N10-v0", **kwargs)


register(
    id="MiniHack-MultiRoom-N2-Lava-v0",
    entry_point="minihack.envs.minigrid:MiniHackMultiRoomN2Lava",
)
register(
    id="MiniHack-MultiRoom-N4-Lava-v0",
    entry_point="minihack.envs.minigrid:MiniHackMultiRoomN4Lava",
)
register(
    id="MiniHack-MultiRoom-N6-Lava-v0",
    entry_point="minihack.envs.minigrid:MiniHackMultiRoomN6Lava",
)
register(
    id="MiniHack-MultiRoom-N10-Lava-v0",
    entry_point="minihack.envs.minigrid:MiniHackMultiRoomN10Lava",
)
register(
    id="MiniHack-MultiRoom-N6-Lava-OpenDoor-v0",
    entry_point="minihack.envs.minigrid:MiniHackMultiRoomN6LavaOpenDoor",
)
register(
    id="MiniHack-MultiRoom-N10-Lava-OpenDoor-v0",
    entry_point="minihack.envs.minigrid:MiniHackMultiRoomN10LavaOpenDoor",
)


# MiniGrid: MonsterpedMultiRoom
class MiniHackMultiRoomN2Monster(MiniGridHack):
    def __init__(self, *args, **kwargs):
        kwargs["max_episode_steps"] = kwargs.pop("max_episode_steps", 40)
        kwargs["num_mon"] = 3
        super().__init__(
            *args, env_name="MiniGrid-MultiRoom-N2-S4-v0", **kwargs
        )


class MiniHackMultiRoomN4Monster(MiniGridHack):
    def __init__(self, *args, **kwargs):
        kwargs["max_episode_steps"] = kwargs.pop("max_episode_steps", 120)
        kwargs["num_mon"] = 6
        super().__init__(
            *args, env_name="MiniGrid-MultiRoom-N4-S5-v0", **kwargs
        )


class MiniHackMultiRoomN6Monster(MiniGridHack):
    def __init__(self, *args, **kwargs):
        kwargs["max_episode_steps"] = kwargs.pop("max_episode_steps", 240)
        kwargs["num_mon"] = 9
        super().__init__(*args, env_name="MiniGrid-MultiRoom-N6-v0", **kwargs)


# MiniGrid: MonsterMultiRoom
register(
    id="MiniHack-MultiRoom-N2-Monster-v0",
    entry_point="minihack.envs.minigrid:MiniHackMultiRoomN2Monster",
)
register(
    id="MiniHack-MultiRoom-N4-Monster-v0",
    entry_point="minihack.envs.minigrid:MiniHackMultiRoomN4Monster",
)
register(
    id="MiniHack-MultiRoom-N6-Monster-v0",
    entry_point="minihack.envs.minigrid:MiniHackMultiRoomN6Monster",
)


# MiniGrid: ExtremeMultiRoom
class MiniHackMultiRoomN2Extreme(MiniGridHack):
    def __init__(self, *args, **kwargs):
        kwargs["max_episode_steps"] = kwargs.pop("max_episode_steps", 40)
        kwargs["num_mon"] = 3
        kwargs["lava_walls"] = True
        kwargs["door_state"] = "locked"
        super().__init__(
            *args, env_name="MiniGrid-MultiRoom-N2-S4-v0", **kwargs
        )


class MiniHackMultiRoomN4Extreme(MiniGridHack):
    def __init__(self, *args, **kwargs):
        kwargs["max_episode_steps"] = kwargs.pop("max_episode_steps", 120)
        kwargs["num_mon"] = 6
        kwargs["lava_walls"] = True
        kwargs["door_state"] = "locked"
        super().__init__(
            *args, env_name="MiniGrid-MultiRoom-N4-S5-v0", **kwargs
        )


class MiniHackMultiRoomN6Extreme(MiniGridHack):
    def __init__(self, *args, **kwargs):
        kwargs["max_episode_steps"] = kwargs.pop("max_episode_steps", 240)
        kwargs["num_mon"] = 9
        kwargs["lava_walls"] = True
        kwargs["door_state"] = "locked"
        super().__init__(*args, env_name="MiniGrid-MultiRoom-N6-v0", **kwargs)


register(
    id="MiniHack-MultiRoom-N2-Extreme-v0",
    entry_point="minihack.envs.minigrid:MiniHackMultiRoomN2Extreme",
)
register(
    id="MiniHack-MultiRoom-N4-Extreme-v0",
    entry_point="minihack.envs.minigrid:MiniHackMultiRoomN4Extreme",
)
register(
    id="MiniHack-MultiRoom-N6-Extreme-v0",
    entry_point="minihack.envs.minigrid:MiniHackMultiRoomN6Extreme",
)


# Note: the N6-Extreme-v0 env above is impossible to solve consistently even for a human
# due to too many monsters. Here are some easier envs with lava and fewer monsters.


class MiniHackMultiRoomN2LavaMonsters(MiniGridHack):
    def __init__(self, *args, **kwargs):
        kwargs["max_episode_steps"] = kwargs.pop("max_episode_steps", 40)
        kwargs["num_mon"] = 1
        kwargs["lava_walls"] = True
        super().__init__(
            *args, env_name="MiniGrid-MultiRoom-N2-S4-v0", **kwargs
        )


class MiniHackMultiRoomN4LavaMonsters(MiniGridHack):
    def __init__(self, *args, **kwargs):
        kwargs["max_episode_steps"] = kwargs.pop("max_episode_steps", 120)
        kwargs["num_mon"] = 2
        kwargs["lava_walls"] = True
        super().__init__(
            *args, env_name="MiniGrid-MultiRoom-N4-S5-v0", **kwargs
        )


class MiniHackMultiRoomN6LavaMonsters(MiniGridHack):
    def __init__(self, *args, **kwargs):
        kwargs["max_episode_steps"] = kwargs.pop("max_episode_steps", 240)
        kwargs["num_mon"] = 3
        kwargs["lava_walls"] = True
        super().__init__(*args, env_name="MiniGrid-MultiRoom-N6-v0", **kwargs)


register(
    id="MiniHack-MultiRoom-N2-LavaMonsters-v0",
    entry_point="minihack.envs.minigrid:MiniHackMultiRoomN2LavaMonsters",
)
register(
    id="MiniHack-MultiRoom-N4-LavaMonsters-v0",
    entry_point="minihack.envs.minigrid:MiniHackMultiRoomN4LavaMonsters",
)
register(
    id="MiniHack-MultiRoom-N6-LavaMonsters-v0",
    entry_point="minihack.envs.minigrid:MiniHackMultiRoomN6LavaMonsters",
)


# MiniGrid: LavaCrossing
register(
    id="MiniGrid-LavaCrossingS19N13-v0",
    entry_point="minigrid.envs:CrossingEnv",
    kwargs={"size": 19, "num_crossings": 13},
)
register(
    id="MiniGrid-LavaCrossingS19N17-v0",
    entry_point="minigrid.envs:CrossingEnv",
    kwargs={"size": 19, "num_crossings": 17},
)


register(
    id="MiniHack-LavaCrossingS9N1-v0",
    entry_point="minihack.envs.minigrid:MiniGridHack",
    kwargs={"env_name": "MiniGrid-LavaCrossingS9N1-v0"},
)
register(
    id="MiniHack-LavaCrossingS9N2-v0",
    entry_point="minihack.envs.minigrid:MiniGridHack",
    kwargs={"env_name": "MiniGrid-LavaCrossingS9N2-v0"},
)
register(
    id="MiniHack-LavaCrossingS9N3-v0",
    entry_point="minihack.envs.minigrid:MiniGridHack",
    kwargs={"env_name": "MiniGrid-LavaCrossingS9N3-v0"},
)
register(
    id="MiniHack-LavaCrossingS11N5-v0",
    entry_point="minihack.envs.minigrid:MiniGridHack",
    kwargs={"env_name": "MiniGrid-LavaCrossingS11N5-v0"},
)
register(
    id="MiniHack-LavaCrossingS19N13-v0",
    entry_point="minihack.envs.minigrid:MiniGridHack",
    kwargs={"env_name": "MiniGrid-LavaCrossingS19N13-v0"},
)

register(
    id="MiniHack-LavaCrossingS19N17-v0",
    entry_point="minihack.envs.minigrid:MiniGridHack",
    kwargs={"env_name": "MiniGrid-LavaCrossingS19N17-v0"},
)


# MiniGrid: Simple Crossing
register(
    id="MiniHack-SimpleCrossingS9N1-v0",
    entry_point="minihack.envs.minigrid:MiniGridHack",
    kwargs={"env_name": "MiniGrid-SimpleCrossingS9N1-v0"},
)
register(
    id="MiniHack-SimpleCrossingS9N2-v0",
    entry_point="minihack.envs.minigrid:MiniGridHack",
    kwargs={"env_name": "MiniGrid-SimpleCrossingS9N2-v0"},
)
register(
    id="MiniHack-SimpleCrossingS9N3-v0",
    entry_point="minihack.envs.minigrid:MiniGridHack",
    kwargs={"env_name": "MiniGrid-SimpleCrossingS9N3-v0"},
)
register(
    id="MiniHack-SimpleCrossingS11N5-v0",
    entry_point="minihack.envs.minigrid:MiniGridHack",
    kwargs={"env_name": "MiniGrid-SimpleCrossingS11N5-v0"},
)
