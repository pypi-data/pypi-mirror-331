CREATE OR REPLACE FUNCTION debezium_payload_extraction(data string, source_stream string, target_stream string) RETURNS string LANGUAGE PYTHON AS 
$$
import traceback
import json
from neutrino.pipeline import DataExtractionAgent
from neutrino.utils.tools import extract_code_blocks_with_type


def debezium_payload_extraction(data, source_stream, target_stream):
    results = []
    for (data, source_stream, target_stream) in zip(data, source_stream, target_stream):
        try:
            agent = DataExtractionAgent()
            payload_extraction_sql, target_stream_ddl, extraction_mv_ddl = agent.pipeline(data, source_stream, target_stream)

            code_target_stream_ddl = extract_code_blocks_with_type(target_stream_ddl)
            code_extraction_mv_ddl = extract_code_blocks_with_type(extraction_mv_ddl)
            result = {
                "target_stream_ddl" : code_target_stream_ddl[0][1],
                "extraction_mv_ddl" : code_extraction_mv_ddl[0][1] 
            }
            results.append(json.dumps(result))
        except Exception as e:
            trace = traceback.format_exc()
            results.append(trace)

    return results

$$;