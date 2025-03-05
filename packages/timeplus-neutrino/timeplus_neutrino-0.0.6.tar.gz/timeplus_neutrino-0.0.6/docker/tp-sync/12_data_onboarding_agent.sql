CREATE OR REPLACE FUNCTION schema_inference(data string,name string) RETURNS string LANGUAGE PYTHON AS 
$$
import traceback
import json
from neutrino.utils.tools import extract_code_blocks_with_type
from neutrino.agent import DataOnboardingAgent


def schema_inference(data, name):
    results = []
    for (data, name) in zip(data, name):
        try:
            agent = DataOnboardingAgent()
            inference_ddl, inference_json = agent.inference(data, name)
            

            ddl_code = extract_code_blocks_with_type(inference_ddl)
            json_code = extract_code_blocks_with_type(inference_json)
            result = {}
            result["ddl"] = ddl_code[0][1]
            result["json"] = json_code[0][1]

            results.append(json.dumps(result))
        except Exception as e:
            trace = traceback.format_exc()
            results.append(trace)

    return results

$$;


CREATE OR REPLACE FUNCTION field_summary(data string, columns string) RETURNS string LANGUAGE PYTHON AS 
$$
import traceback
from neutrino.agent import DataOnboardingAgent
from neutrino.utils.tools import extract_code_blocks_with_type


def field_summary(data, columns):
    results = []
    for (data, columns) in zip(data, columns):
        try:
            agent = DataOnboardingAgent()
            summary_result = agent.summary(data, columns)
            extracted_sql_result = extract_code_blocks_with_type(summary_result)
            results.append(extracted_sql_result[0][1])
        except Exception as e:
            trace = traceback.format_exc()
            results.append(trace)

    return results

$$;

CREATE OR REPLACE FUNCTION analysis_recommendation(data string, columns string, name string) RETURNS string LANGUAGE PYTHON AS 
$$
import traceback
from neutrino.agent import DataOnboardingAgent
from neutrino.utils.tools import extract_code_blocks_with_type


def analysis_recommendation(data, columns, name):
    results = []
    for (data, columns, name) in zip(data, columns, name):
        try:
            agent = DataOnboardingAgent()
            recommendation_result = agent.recommendations(data, columns, name)
            extracted_sql_result = extract_code_blocks_with_type(recommendation_results)
            results.append(extracted_sql_result[0][1])
        except Exception as e:
            trace = traceback.format_exc()
            results.append(trace)

    return results

$$;