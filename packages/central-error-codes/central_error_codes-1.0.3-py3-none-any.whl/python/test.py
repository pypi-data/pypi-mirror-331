from error_codes import ErrorCode

error_codes = ErrorCode()
# Use the correct class name
print("All Errors:", ErrorCode.get_error())
print("Generic Error:", ErrorCode.get_generic_error()["P1_INITIALIZATION_ERROR"])
print("LLM Gateway Error:", ErrorCode.get_llm_gateway_error()["P1_ERROR_HASH_CALCULATION"])