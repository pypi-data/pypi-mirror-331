import json
import time
from datetime import datetime, timezone
from functools import lru_cache
from queue import Queue
from threading import Thread
from timeit import default_timer
from typing import Literal, TypedDict

from loguru import logger
from openai import OpenAI

from terminal_gpt.helper.db import get_db
from terminal_gpt.helper.serde import json_dumps_consistent
from terminal_gpt.settings import OPENAI_API_KEY, TERMINAL_GPT_MODEL


class Message(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str


class Response(TypedDict):
    id: str
    object: str
    created: int
    model: str
    choices: list["Choice"]
    delay: float


class Choice(TypedDict):
    index: int
    delta: "Delta"
    finish_reason: str | None


class Delta(TypedDict, total=False):
    role: str
    content: str


SENTINEL = object()


openai_client = OpenAI(api_key=OPENAI_API_KEY)


def fetch_chat_completion(
    messages: list[Message],
    *,
    model: str = TERMINAL_GPT_MODEL,
    functions: list | None = None,
    function_call: str | list | dict | None = None,
    temperature: float = 1.0,
    top_p: float = 1.0,
    n: int = 1,
    stop: str | list | None = None,
    max_tokens: int | None = None,
    presence_penalty: float = 0,
    frequency_penalty: float = 0,
    logit_bias: dict | None = None,
    user: str | None = None,
    cache_delay: bool = True,
    cache_speed_up: float = 5.0,
):
    # Prepare request for storage
    messages = [{"role": x["role"], "content": x["content"]} for x in messages]
    params = {
        "messages": messages,
        "model": model,
        "temperature": temperature,
        "top_p": top_p,
        "n": n,
        "stop": stop,
        "max_tokens": max_tokens,
        "presence_penalty": presence_penalty,
        "frequency_penalty": frequency_penalty,
    }

    if functions is not None:
        params["functions"] = functions
    if function_call is not None:
        params["function_call"] = function_call
    if logit_bias is not None:
        params["logit_bias"] = logit_bias
    if user is not None:
        params["user"] = user
    db = get_db()
    create_chatgpt_tables()

    # Check cache
    params_json = json_dumps_consistent(params)
    row = db.execute(
        "SELECT response FROM chatgpt_chat_completion WHERE params = ? ORDER BY requested_at DESC LIMIT 1",
        (params_json,),
    ).fetchone()
    if row:
        logger.debug("[ChatGPT] Got from cache!")
        response_iter = json.loads(row[0])
        for response_item in response_iter:
            if cache_delay:
                time.sleep(response_item["delay"] / cache_speed_up)
            yield response_item
        return

    # API Call
    logger.debug("[ChatGPT] Calling API!")
    requested_at = datetime.now(timezone.utc)

    # Start the producer thread
    data_queue = Queue()
    Thread(
        target=_fetch_chat_completion,
        args=(params, data_queue),
    ).start()

    # Listen to the producer thread (we're doing this so natural streaming delay isn't blocked)
    responses = []
    while True:
        item = data_queue.get()
        if item is SENTINEL:
            break
        responses.append(item)
        yield item

    # Save to db
    db.execute(
        """
        INSERT INTO chatgpt_chat_completion (params, response, requested_at)
        VALUES (?, ?, ?)
        """,
        (params_json, json.dumps(responses), requested_at.isoformat()),
    )
    db.commit()


def _fetch_chat_completion(params: dict, q: Queue):
    last_time = default_timer()

    # request API
    response_iter = openai_client.chat.completions.create(**params, stream=True)

    # Stream responses
    for response_item in response_iter:
        current_time = default_timer()

        # serialize and deserialize so it's always consistent
        response_item = json.loads(response_item.to_json())

        # calculate delay before message
        response_item["delay"] = current_time - last_time
        last_time = current_time

        # add to queue
        q.put(response_item)

    # finish
    q.put(SENTINEL)


@lru_cache()
def create_chatgpt_tables():
    DDL = """
    CREATE TABLE IF NOT EXISTS chatgpt_chat_completion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        params TEXT NOT NULL,
        response TEXT NOT NULL,
        requested_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS chatgpt_chat_completion_params_idx ON chatgpt_chat_completion (params);
    """
    get_db().executescript(DDL)
    get_db().commit()
