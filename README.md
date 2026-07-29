# FrozenLake

[![OpenReward Environment](https://img.shields.io/badge/%E2%AD%90%20OpenReward-Environment-f7e6cc)](https://openreward.ai/GeneralReasoning/FrozenLake)

## Description

**FrozenLake** is an ORS environment for evaluating agents on a grid navigation game where they must reach a goal while avoiding holes on a slippery frozen lake. This environment wraps the FrozenLake implementation from [TextArena](https://github.com/LeonGuertler/TextArena), a framework for text-based game environments.

## Capabilities

- Navigation and pathfinding under uncertainty
- Risk-aware decision-making with stochastic transitions
- Spatial reasoning on grid-based environments

## Compute Requirements

FrozenLake does not require a sandbox. It has minimal compute requirements.

## License

[MIT](https://github.com/LeonGuertler/TextArena/blob/main/LICENSE).

## Tasks

There are two splits: train (450 tasks) and test (450 tasks). Each split contains 50 tasks across each of 9 variants:

- **FrozenLake-v0**: Standard frozen lake with formatted feedback
- **FrozenLake-v0-train**: Training variant with guidance
- **FrozenLake-v0-raw**: Raw feedback without formatting
- **FrozenLake-v0-random**: Random map generation
- **FrozenLake-v0-random-train**: Random maps with training guidance
- **FrozenLake-v0-random-raw**: Random maps with raw feedback
- **FrozenLake-v0-hardcore**: More challenging maps
- **FrozenLake-v0-hardcore-train**: Hardcore with training guidance
- **FrozenLake-v0-hardcore-raw**: Hardcore with raw feedback

Each task is seeded for reproducibility.

## Reward Structure

This is a sparse reward environment. TextArena's FrozenLake reward is already in `[0.0, 1.0]` and is passed through unchanged: reaching the goal scores `1.0`, and every other terminal outcome (falling into a hole or hitting the turn limit) scores a continuous progress fraction of the journey toward the goal. Intermediate moves score `0.0`.

We do not use LLM graders for this environment; reward is determined programmatically.

## Data

Game state is generated procedurally by the TextArena engine using seeded randomness. No external data files are required.

## Tools

Agents are given a single tool:

- `move(direction)`: Move in the given direction (up, down, left, right) on the frozen lake grid.

## Time Horizon

FrozenLake is a multi-turn environment.

## Environment Difficulty

Easy to Hard. The difficulty varies significantly across variants, from simple deterministic paths to complex randomly generated maps with slippery mechanics that add stochasticity to movement.

## Other Environment Requirements

There are no further environment requirements; FrozenLake works out of the box without any secrets or API keys.

## Safety

Agents in FrozenLake interact only with a grid navigation game and have no access to external systems, the internet, or sensitive data. The environment does not present safety risks.

## Citations

```bibtex
@software{textarena2024,
  author    = {Guertler, Leon and Banting, Wilfried and Pignatelli, Eduardo},
  title     = {TextArena},
  year      = {2024},
  publisher = {GitHub},
  url       = {https://github.com/LeonGuertler/TextArena}
}
```
