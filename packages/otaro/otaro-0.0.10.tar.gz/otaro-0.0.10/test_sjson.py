import json
from itertools import combinations

from otaro.parsing import llm_parse_json

# from otaro.parsing.jsonfix import Fixer

# fixer = Fixer()

malformed_json = '{"name": \'Alice\', "age": 30, "tweet": "Someone said "Hello"d", "foo": "bar"}'  # Missing closing quote for "city" value
# malformed_json = '{"name": none}'
correct_json = '{"name": "Alice", "age": 30, "tweet": "Someone said \\"Hello\\"d", "foo": "bar"}'  # Missing closing quote for "city" value

malformed_json = """
["Feeling inadequate about your writing? You're not alone! The trick is to just WRITE. Write for yourself, learn from others, and don't compare yourself to the "authorities." Your unique perspective matters! #writing #inspiration", "Writing isn't just about producing content; it's about learning, thinking, and leveraging AI. Don't let the fear of not being "good enough" stop you. Get those thoughts out of your head and onto the page! #writingtips #productivity"]
"""

parse = llm_parse_json(malformed_json)

print(parse)

quit()


# Brute force escape chars
def escape_json(json_str: str, num_escapes: int = 1):
    quote_pos = [i for i, c in enumerate(json_str) if c in "\"'"]
    candidates = combinations(quote_pos, num_escapes)
    for candidate in candidates:
        new_json_str = ""
        for start, end in zip([0, *candidate], [*candidate, len(json_str)]):
            new_json_str += json_str[start:end] + "\\"
        new_json_str = new_json_str[:-1]
        try:
            print(llm_parse_json(new_json_str))
            # print(json.loads(new_json_str))
        except Exception:
            pass


escape_json(malformed_json, num_escapes=2)
quit()

print(json.loads(correct_json))

for seg in malformed_json.split('"'):
    print([seg])
print()
for seg in correct_json.split('"'):
    print([seg])
quit()

fixed_json = fixer.fix(malformed_json)


print(llm_parse_json(fixed_json))
