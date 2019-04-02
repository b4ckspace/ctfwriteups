map = {
    'z':'_',
    'a':'a',
    'x':'b',
    'q':'c',
    'l':'w',
    'v':'h',
    'e':'i',
    'f':'j',
    'b':'k',
    'r':'l',
    'g':'m',
    'n':'n',
    'o':'x',
    'p':'y',
    's':'d',
    'c':'e',
    'w':'f',
    'd':'g',
    't':'o',
    'h':'p',
    'm':'q',
    'k':'u',
    'i':'v',
    'y':'r',
    'j':'s',
    'u':'t',
    '_':'z',
}

encrypted = "hajjzvajvzqyaqbendzvajvqauzarlapjzrkybjzenzuvczjvastlj"

clean = ''
for i in encrypted:
    clean += map[i]
print(clean)
