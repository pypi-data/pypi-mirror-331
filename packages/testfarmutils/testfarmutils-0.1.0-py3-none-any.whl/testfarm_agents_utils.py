import os


__all__ = [
    "add_custom_magic_variable",
    "expand_magic_variables"
]


default_magic_variables = {
    '$__TF_TOOLS_DIR__': os.getenv('TF_TOOLS_DIR'),
    '$__TF_TEMP_DIR__': os.getenv('TF_TEMP_DIR'),
    '$__BASE_TEST_CONCERNS_DIR__': os.getenv('SD_BLOX_TEST_CONCERNS'),
    '$__BLOX_EXE_DIR__': os.getenv('SD_BLOX_EXE_DIR'),
}


custom_magic_variables = {
    
}


def add_custom_magic_variable(name: str, value: str):
    if not name or not value:
        raise ValueError("Custom magic variable name and value must not be empty.")
    
    if not name.startswith('$__') or not name.endswith('__'):
        raise ValueError(f"Custom magic variable name is incorrect. Please stick to $__CUSTOM_VAR_NAME__ format.")
    
    if name in custom_magic_variables or name in default_magic_variables:
        raise ValueError(f"Magic variable {name} already exists.")

    custom_magic_variables[name] = value


def expand_magic_variables(text: str) -> str:
    expanded_text = text

    magic_variables = {**default_magic_variables, **custom_magic_variables}

    for key in magic_variables:
       expanded_text = expanded_text.replace(key, magic_variables[key])
       
    return expanded_text

