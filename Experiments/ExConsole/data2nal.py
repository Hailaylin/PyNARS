'''Data to NAL
Define a format for converting Python data structures to Narsese
Core function: <Python data structure>→<NAL **text**>
'''
from pynars.Narsese import Punctuation
from pynars.Narsese import parser
# pynars

# Constants #


def SIGN_TYPE_NAMES(type): return type.__name__


# {1,2,3}
SIGN_RELATION_BELONG: str = 'belong'
# [1,2,3]
SIGN_RELATION_OBJ_ITEM_VALUE: str = 'obj_item_value'
# {a: 1, b: 2}
SIGN_RELATION_OBJ_PROPERTY_VALUE: str = 'obj_property_value'

# Utils #

# Preset identification


def is_basic_type(obj: any) -> bool:
    '''Determining whether a type is an "immutable type"
    Note: Strings are counted'''
    t = type(obj)
    return obj == None or t == bool or t == int or t == float or t == str


def verify_term_name(name: str) -> str | None:
    try:
        return (
            name
            if parser.parse(text=f'< {name} --> {name} >.')
            else None)
    except:
        return None

# term construction


def term_rel(A: str, B: str) -> str:
    '''Construct the term "Relationship between A and B"'''
    return f'(*,{A},{B})'


def term_name(A: any) -> str:
    '''Build term "object name"'''
    t: type = type(A)
    # test whether the object can be directly accepted as a lexical item, if it is attached, if not, no
    instance_wrapper: str = '%s' if is_basic_type(A) else '{%s}'
    # first format encapsulation: Fill "class name _ value /id"
    init_name: str = verify_term_name(f'{t.__name__}_{str(A)}')
    # check: Whether the filled term is valid (cause: the array "first pass, second fail" problem)
    init_name = verify_term_name(
        init_name if init_name else f'{t.__name__}_{id(A)}')
    # second format encapsulation: Specifies whether an instance term is required
    final_name: str = instance_wrapper % init_name
    # return
    return final_name

# sentence construction


def sentence_inh(A: str, B: str, punct: Punctuation | str = Punctuation.Judgement) -> str:
    '''Building relationships "A is B"'''
    return f'<{A} --> {B}>{punct.value if isinstance(punct,Punctuation) else punct}'  # <A --> B> default with "."


def sentence_rel(A: str, r: str, B: str, punct: Punctuation = Punctuation.Judgement) -> str:
    '''Construct relation "ArB" i.e. "The relation between A and B" is r"'''
    return sentence_inh(term_rel(A, B), f'{r}', punct=punct)  # <(*,A,B) --> r>. The "relationship" between A and B is r


def sentence_type_sign(name: str, type: type, punct: Punctuation = Punctuation.Judgement) -> str:
    '''Name the name based on the type of the object'''
    return sentence_inh(name, SIGN_TYPE_NAMES(type), punct=punct)  # name --> type


def sentence_tri_rel(obj: str, key: str, value: str, relation: str = SIGN_RELATION_OBJ_PROPERTY_VALUE,
                     punct: Punctuation = Punctuation.Judgement) -> str:
    '''Building a ternary relationship "Object [key] = value"
    Example: (*,{object},(*,{attribute},{value})) --> object_attribute_value
    '''
    return sentence_rel(obj, relation, term_rel(key, value), punct=punct)  # (*,{obj},(*,{key},{value})) --> relation

# Main conversion module #

# basic


# Use kwargs to automatically pass "punctuation" information
def none2NAL(n: None, special_name: str, **kwargs) -> list[str]:
    '''None to NAL'''
    return [sentence_type_sign(special_name, type(n), **kwargs)]


def bool2NAL(b: str, special_name: str, **kwargs) -> list[str]:
    '''boolean to NAL'''
    result: list[str] = [sentence_type_sign(
        special_name, bool, **kwargs)]  # preset type identification
    return result


def int2NAL(i: int, special_name: str, **kwargs) -> list[str]:
    '''Integer to NAL
        TODO: Build an integer system'''
    result: list[str] = [sentence_type_sign(
        special_name, int, **kwargs)]  # preset type identification
    return result


def float2NAL(f: float, special_name: str, **kwargs) -> list[str]:
    '''Floating-point number becomes NAL
    TODO: Build a floating point number system and combine it with an integer system'''
    result: list[str] = [sentence_type_sign(
        special_name, float, **kwargs)]  # preset type identification
    return result


def str2NAL(s: str, special_name: str, **kwargs) -> list[str]:
    '''Set to NAL
    TODO: How does distinguish between "name" and "value" of a string?'''
    # tests whether a string can be directly accepted as a term, appended if it is, unappended if it is not
    # Try to use the string itself as a name for easy identification
    final_name = verify_term_name(s)
    final_name: str = special_name + \
        (f'「{s}」' if final_name else '')  # Include itself if you can, do not add information otherwise
    # preset type identification
    result: list[str] = [sentence_type_sign(final_name, str, **kwargs)]
    return result

# containers


def set2NAL(s: set, special_name: str, **kwargs) -> list[str]:
    '''Set to NAL
    Use the relative item "belong"
    Import a collection name as the concept name, and then convert all elements within it to NAL
    Return: A list of multiple NAL statements (easy to split)'''
    result: list[str] = [sentence_type_sign(
        special_name, set, **kwargs)]  # preset type identification
    for item in s:  # TODO: Implementing recursive logic @auto2NAL(item)
        result.append(sentence_rel(term_name(item),
                      SIGN_RELATION_BELONG, special_name, **kwargs))
    return result


def lis_tuple2NAL(array: list | tuple, special_name: str, **kwargs) -> List[str]:
    '''List/tuple to NAL: Lists whose keys are integers'''
    result: list[str] = [sentence_type_sign(
        special_name, type(array), **kwargs)]  # preset type identification
    for i in range(len(array)):
        # get element
        item: any = array[i]
        iName: str = term_name(i)
        item_name: str = term_name(item)
        # pre-add definitions for keys and values
        result.extend(auto2NAL(item, item_name, **kwargs))
        result.extend(auto2NAL(i, iName, **kwargs))
        # bind objects, keys, and values
        result.append(sentence_tri_rel(
            special_name,
            iName,
            item_name,
            **kwargs))  # list[integer_index] = value
    return result


def dict2NAL(d: dict, special_name: str, **kwargs) -> list[str]:
    '''dict to NAL
    #! In fact, JSON is a dictionary, to achieve the dictionary↔NAL conversion, which is equivalent to NARS can read JSON
    TODO models dictionaries using an index system'''
    result: list[str] = [sentence_type_sign(
        special_name, dict, **kwargs)]  # preset type identification
    for key, value in d.items():
        key_name: str = term_name(key)
        value_name: str = term_name(value)
        # pre-add definitions for keys and values
        result.extend(auto2NAL(key, key_name, **kwargs))
        result.extend(auto2NAL(value, value_name, **kwargs))
        # bind objects, keys, and values
        result.append(sentence_tri_rel(
            special_name,
            key_name,
            value_name,
            **kwargs))  # dictionary[immutable_data_index] = value
    return result


def type2NAL(t: type, special_name: str, **kwargs) -> list[str]:
    '''Type to NAL
    The "type" itself also needs to become NAL'''
    return [sentence_type_sign(special_name, type, **kwargs)]  # only type notations

# default values


def default2NAL(obj: any, special_name: str, **kwargs) -> list[str]:
    '''Other objects become NAL
    Temporarily occupy the one place, will later be separated from many types'''
    print(f'WARNING: unsupported object {obj} with type {type(obj)}')
    # only type notations
    return [sentence_type_sign(special_name, type, **kwargs)]

# Main function: Integrate all parts #


CONVERT_FUNCTIONS: dict[type:any] = {
    type(None): none2NAL,
    int: int2NAL,
    float: float2NAL,
    bool: bool2NAL,
    str: str2NAL,
    list: lis_tuple2NAL,
    tuple: lis_tuple2NAL,
    set: set2NAL,
    dict: dict2NAL,
    type: type2NAL,
    None: default2NAL,
}


def auto2NAL(obj: any, name: str = None, punct: Punctuation = Punctuation.Judgement) -> list[str]:
    '''Function integration: Python object →NAL statement sequence
    Automatically identify the object type and call the corresponding conversion function'''
    # get name
    # If no, automatically generate
    name = name if name else term_name(obj)
    # get type
    t = type(obj)
    # select & Generate, with default values (all parameters must accept a "Narsese parsed name")
    nars_sentences: list[str] = CONVERT_FUNCTIONS.get(
        t, CONVERT_FUNCTIONS[None])(obj, name, punct=punct)
    # verify
    for sentence in nars_sentences:
        parser.parse(sentence)
    # return
    return nars_sentences
