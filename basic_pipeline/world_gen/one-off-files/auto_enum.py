from enum import Enum, auto

# This is a snippet from a generated response to the following Google Search
# "What is an auto enum in Python?"

'''
In Python, enum.auto is a feature provided by the enum module 
that automatically assigns unique integer values to the members 
of an enumeration. When defining an Enum, if you use auto() for 
a member's value, Python automatically generates the next 
sequential integer, starting from 1 by default, for that member. 
This simplifies the process of creating enums, especially when 
the specific values don't matter, but their uniqueness does.
'''

class Color(Enum):
    RED = auto()
    GREEN = auto()
    BLUE = auto()

print(Color.RED)
print(Color.RED.value)
print(Color.GREEN.value)
print(Color.BLUE.value)