import random
from string import ascii_uppercase, digits

text = [random.choice(ascii_uppercase + digits)
        for i in range(6)]

print(''.join(text))
