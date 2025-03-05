from neutrino.agent import DataOnboardingAgent
from neutrino.utils.tools import extract_code_blocks_with_type

data = """{
		"customer_id": 9,
		"name": "Johnathan Rodriguez",
		"email": "thomasramirez@example.org",
		"phone": "001-845-290-8721x77863",
		"address": "743 Cervantes Causeway Apt. 762\nPort Lauren, NY 12698",
		"ip": "127.0.0.1",
		"time": "2023-01-01 00:00:00",
		"event_time": "2023-01-01 00:00:00",
		"uid": "2a02:aa08:e000:3100::2",
		"uid2":"1f71acbf-59fc-427d-a634-1679b48029a9"
}"""


agent = DataOnboardingAgent()

inference_ddl, inference_json = agent.inference(data, "customer")

ddl_code = extract_code_blocks_with_type(inference_ddl)
print(f"code type {ddl_code[0][0]}, schema sql : {ddl_code[0][1]}")

json_code = extract_code_blocks_with_type(inference_json)
print(f"code type {json_code[0][0]}, schema json : {json_code[0][1]}")


