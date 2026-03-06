import textarena as ta
from typing import List
from pydantic import BaseModel, field_validator
from openreward.environments import Environment, JSONObject, ToolOutput, TextBlock, tool


class TaskSpec(BaseModel):
    id: str
    env_id: str
    seed: int
    variant: str = ""


class MoveParams(BaseModel, extra="forbid"):
    direction: str

    @field_validator("direction")
    @classmethod
    def validate_direction(cls, v):
        v = v.strip().lower()
        if v not in ("up", "down", "left", "right"):
            raise ValueError("direction must be one of: up, down, left, right")
        return v


class FrozenLakeEnvironment(Environment):
    GAME_NAME = "FrozenLake"
    VARIANTS = [
        'FrozenLake-v0',
        'FrozenLake-v0-train',
        'FrozenLake-v0-raw',
        'FrozenLake-v0-random',
        'FrozenLake-v0-random-train',
        'FrozenLake-v0-random-raw',
        'FrozenLake-v0-hardcore',
        'FrozenLake-v0-hardcore-train',
        'FrozenLake-v0-hardcore-raw'
    ]
    NUM_TASKS_PER_VARIANT = 50

    def __init__(self, task_spec, secrets={}):
        super().__init__(task_spec)
        self.config = TaskSpec.model_validate(task_spec)
        self.ta_env = ta.make(env_id=self.config.env_id)
        self.game_done = False
        self.turn_count = 0

    @classmethod
    def list_splits(cls):
        return ["train", "test"]

    @classmethod
    def list_tasks(cls, split):
        tasks = []
        for variant_id in cls.VARIANTS:
            for seed_idx in range(cls.NUM_TASKS_PER_VARIANT):
                seed = seed_idx if split == "train" else seed_idx + 10000
                tasks.append({
                    "id": f"{variant_id}_seed{seed}",
                    "env_id": variant_id,
                    "seed": seed,
                    "variant": variant_id
                })
        return tasks

    def _map_reward(self, raw):
        return max(0.0, min(1.0, (raw + 1.0) / 2.0))

    async def get_prompt(self):
        self.ta_env.reset(num_players=1, seed=self.config.seed)
        _, obs = self.ta_env.get_observation()
        obs_text = obs if isinstance(obs, str) else str(obs)
        prompt = f"""You are playing Frozen Lake.

{obs_text}

Use the move tool to navigate the frozen lake. Move up, down, left, or right.
Reach the goal (G) while avoiding holes (H). The ice may be slippery!"""
        return [TextBlock(text=prompt)]

    @tool
    async def move(self, params: MoveParams) -> ToolOutput:
        """Move in the given direction (up, down, left, right) on the frozen lake grid."""
        if self.game_done:
            return ToolOutput(
                blocks=[TextBlock(text="Game is already over.")],
                metadata={"error": "game_finished"},
                reward=0.0,
                finished=True
            )

        action = f"[{params.direction}]"
        done, info = self.ta_env.step(action=action)
        self.turn_count += 1

        if done:
            self.game_done = True
            rewards, game_info = self.ta_env.close()
            raw = rewards.get(0, 0.0) if isinstance(rewards, dict) else float(rewards)
            reward = self._map_reward(raw)

            reason = ""
            if isinstance(game_info, dict) and 0 in game_info:
                reason = game_info[0].get("reason", "")

            summary = f"Game Over! Reward: {reward:.2f}"
            if reason:
                summary += f"\n{reason}"

            return ToolOutput(
                blocks=[TextBlock(text=summary)],
                metadata={"turn": self.turn_count, "reward": reward},
                reward=reward,
                finished=True
            )

        _, obs = self.ta_env.get_observation()
        obs_text = obs if isinstance(obs, str) else str(obs)

        return ToolOutput(
            blocks=[TextBlock(text=obs_text)],
            metadata={"turn": self.turn_count},
            reward=0.0,
            finished=False
        )
