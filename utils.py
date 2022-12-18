def replace_in_message(message: str, s_from:str, s_to: str) -> str:
    return message.replace(f'<{s_from}>', str(s_to))