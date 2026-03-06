import asyncio
import json
import os
from openai import AsyncOpenAI
from env import FrozenLakeEnvironment, MoveParams


def get_secrets():
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    secrets = {}
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    secrets[key.strip().lower()] = val.strip()
    return secrets


async def run_agent_test(max_turns=50):
    secrets = get_secrets()
    oai_client = AsyncOpenAI(api_key=secrets.get("openai_api_key"))

    tasks = FrozenLakeEnvironment.list_tasks(split="test")
    task = tasks[0]

    print(f"=== Agent Test: FrozenLake ===")
    print(f"Task: {task['id']}")

    env = FrozenLakeEnvironment(task_spec=task, secrets=secrets)
    prompt = await env.get_prompt()

    tools = [
        {
            "type": "function",
            "name": "move",
            "description": "Move in the given direction on the frozen lake.",
            "parameters": {
                "type": "object",
                "properties": {
                    "direction": {
                        "type": "string",
                        "enum": ["up", "down", "left", "right"],
                        "description": "Direction to move"
                    }
                },
                "required": ["direction"],
                "additionalProperties": False
            }
        },
    ]

    input_list = [{"role": "user", "content": prompt[0].text}]
    finished = False
    turn = 0

    while not finished and turn < max_turns:
        turn += 1
        response = await oai_client.responses.create(
            model="gpt-5.2",
            tools=tools,
            input=input_list
        )

        input_list += response.output

        for item in response.output:
            if item.type == "function_call":
                args = json.loads(str(item.arguments))
                result = await env.move(MoveParams(**args))
                finished = result.finished
                reward = result.reward

                input_list.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": result.blocks[0].text
                })

                if turn % 5 == 0 or finished:
                    print(f"  Turn {turn}: move({args.get('direction')}), reward={reward:.3f}, finished={finished}")

                if finished:
                    print(f"\n=== FINISHED! Final reward: {reward:.3f} ===")
                    break

    if not finished:
        print(f"\n=== Hit max turns ({max_turns}) without finishing ===")


if __name__ == "__main__":
    asyncio.run(run_agent_test())
