
import re

B = r"(?:<(?:(?:\w+(?:\.\w+)+)::)?(?:\w+)>)"
SEP = r"[,|]+"
L1_internal = rf"{B}(?:{SEP}{B})*"
L1_full = rf"{B}\[{L1_internal}\]"

L2_element = rf"(?:{L1_full}|{B})"
L2_internal = rf"{L2_element}(?:{SEP}{L2_element})*"
L2_full = rf"{B}\[{L2_internal}\]"

final_regex = rf"^(?:{L2_full}|{L1_full})$"



class BaseTypeFqn(str):

    _PATTERN: re.Pattern[str] = re.compile(
        "^<(?:(?P<context>\\w+(?:\\.\\w+)+)::)?(?P<type>\\w+)>$"
    )

class GenericTypeFqn(str):
    
    _PATTERN: re.Pattern[str] = re.compile(final_regex)

