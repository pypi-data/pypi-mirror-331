from neutrino.pipeline import DataExtractionAgent
from neutrino.utils.tools import extract_code_blocks_with_type

data = """{
		"customer_id": 100,
		"name": "Johnathan Rodriguez",
		"email": "thomasramirez@example.org",
		"phone": "001-845-290-8721x77863",
		"address": "743 Cervantes Causeway Apt. 762\nPort Lauren, NY 12698"
	}"""

source_stream_name = "kafka_cdc_postgres_customers"
target_stream_name = "customers"

agent = DataExtractionAgent()

agent1_output, agent2_output, agent3_output = agent.pipeline_with_mutable_stream(data, source_stream_name, target_stream_name, ["customer_id"])

code1 = extract_code_blocks_with_type(agent1_output)
print(f"code type {code1[0][0]}, extraction sql : {code1[0][1]}")

code2 = extract_code_blocks_with_type(agent2_output)
print(f"code type {code2[0][0]}, target stream schema DDL : {code2[0][1]}")

code3 = extract_code_blocks_with_type(agent3_output)
print(f"code type {code3[0][0]}, mv extraction DDL : {code3[0][1]}")