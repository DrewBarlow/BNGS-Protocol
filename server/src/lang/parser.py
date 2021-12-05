from typing import Tuple, List

"""
<query>   -> ADD <obj>
           | REMOVE <obj>
           | GET <plural_obj>
<target>  -> message | group
<bulk>    -> message | messages | subjects | num
<number>  -> new | messages
"""

# defining a length checker here to remove repetitive error lines
def length_checking(fxn):
    def wrapper(tokens):
        if len(tokens) == 0:
            return (False, [])
        
        return fxn(tokens)
    return wrapper

@length_checking
def query(tokens: List[str]) -> Tuple[bool, List[str]]:
    if tokens[0].upper() in ["ADD", "REMOVE"]:
        return target(tokens[1:])
    elif tokens[0].upper() == "GET":
        return bulk(tokens[1:])
    elif tokens[0].upper() in ["HELP", "BYE"]:
        return (True, [])

    return (False, tokens)

@length_checking
def target(tokens: List[str]) -> Tuple[bool, List[str]]:
    if tokens[0].lower() in ["message", "group"]:
        return (True, [])
    
    return (False, tokens)

@length_checking
def bulk(tokens: List[str]) -> Tuple[bool, List[str]]:
    if tokens[0].lower() in ["message", "messages", "subjects"]:
        return (True, [])
    elif tokens[0].upper() == "NUM":
        return number(tokens[1:])

    return (False, tokens)

@length_checking
def number(tokens: List[str]) -> Tuple[bool, List[str]]:
    if tokens[0].lower() in ["new", "messages"]:
        return (True, [])
    
    return (False, tokens)
