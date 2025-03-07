import time

from terminal_gpt.helper.partial_json_parse import partial_json_parse


def structured_json_parse(code: str):
    partial_json = partial_json_parse(code)
    if not isinstance(partial_json, dict):
        return {"steps": []}
    parsed_steps = []
    output = {"steps": parsed_steps}
    if "steps" in partial_json and isinstance(partial_json["steps"], list):
        for step in partial_json["steps"]:
            if not isinstance(step, dict) or len(step) == 0:
                continue
            key, value = next(iter(step.items()))
            if key[:3] == "exp":
                parsed_steps.append({"explanation": value or ""})
            elif key[:3] == "ext":
                parsed_steps.append({"extra_example_shell_code": value or ""})
    if "final_shell_code_to_execute" in partial_json:
        output["final_shell_code_to_execute"] = partial_json["final_shell_code_to_execute"]
    return output


def test_partial_json_parse():
    code = """
    {"steps":[{"explanation":"This shows which dependenci\\nes are out-of-date."},{"extra_example_shell_code":"poetry show --outdated"}],"final_shell_code_to_execute":"poetry show --outdated"}
    """.strip()
    code = """
    {"steps":[{"explanation":"This shows which dependenci\\nes a"}]}
    """.strip()
    for i in range(len(code) + 1):
        time.sleep(0.1)
        partial_code = code[:i]
        print("\n\n==== PARTIAL CODE ====")
        print(partial_code)
        print("==== PARSED CODE ====")
        try:
            parsed_output = structured_json_parse(partial_code)
            print(parsed_output)
        except Exception:
            print("ERROR")
        print("==========")
