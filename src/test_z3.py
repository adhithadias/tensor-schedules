from z3 import Int, solve, simplify

i = Int('i')
j = Int('j')
k = Int('k')
l = Int('l')
m = Int('m')
n = Int('n')
jpos = Int('jpos')
kpos = Int('kpos')

z3_variables = {'i': i, 'j': j, 'k': k, 'l': l, 'm': m, 'n': n, 'jpos': jpos, 'kpos': kpos}
z3_constraints = []

z3_constraints = [i == 165000, j == 9000, 
                k == 1000, l == 16, m == 16, n == 16,
                jpos >= 0, kpos >= 0,
                100 * i * jpos * kpos < i * j * k,   # i*jpos < 0.01 * i*j
                i * j * k < 1000 * i * jpos * kpos]  # 0.001 * i*j < i*jpos

t1 = i * jpos * kpos * l + j * m * k * l + n * m * k * l # loop depth of 4 is better
t2 = i * jpos * kpos * l * m + k * n * l * m # loop depth of 5 is worse # we will find values that loop depth 5 is less than loop depth 4
t3 = i * jpos * kpos * l * m * n

m1 = k * j
m2 = k
m3 = 0

# increase j and k more

solve(i > 0, j > 0, 
        k > 0, 
        l >= 8, l <= 256, m >= 8, m <= 256, n >= 8, n <= 256,
        jpos >= 0, kpos >= 0, jpos <= j, kpos <= k,
        100 * i * jpos * kpos < i * j * k,   # i*jpos < 0.01 * i*j
        i * j * k < 1000 * i * jpos * kpos,
        t2 < t1, t2 < t3)


solve(i > 0, j > 0, 
        k >= 0, 
        l >= 8, l <= 256, m >= 8, m <= 256, n >= 8, n <= 256,
        jpos >= 0, kpos >= 0, jpos <= j, kpos <= k,
        100 * i * jpos * kpos < i * j * k,   # i*jpos < 0.01 * i*j
        i * j * k < 1000 * i * jpos * kpos,
        t1 < t2, t1 < t3)


solve(i > 0, j > 0, 
        k >= 0, 
        l >= 8, l <= 256, m >= 8, m <= 256, n >= 8, n <= 256,
        jpos >= 0, kpos >= 0, jpos <= j, kpos <= k,
        100 * i * jpos * kpos < i * j * k,   # i*jpos < 0.01 * i*j
        i * j * k < 1000 * i * jpos * kpos,
        t3 < t2, t3 < t1)

print( simplify(t1) )


# loop depth 4 is the lowest
m = 16 
j = 1649
l = 103
k = 1922
i = 1700
kpos = 1725
jpos = 17
n = 9

m = 16 
j = 1600
l = 64
k = 2000
i = 1700
kpos = 1600
jpos = 16
n = 10

m = 16 
j = 800
l = 64
k = 1000
i = 1800
kpos = 400
jpos = 16
n = 32

# loop depth 5 is the lowest
m = 234
j = 1207
l = 251
k = 479
i = 265
kpos = 2
jpos = 961
n = 42


jpos = 5
j = 939
n = 256
i = 269
l = 59
k = 1861
kpos = 1238
m = 256

# loop depth 6 is the lowest for this value set
jpos = 17
j = 203
n = 191
i = 1
l = 255
k = 2047
kpos = 121
m = 229


jpos = 16
j = 200
n = 196
i = 1
l = 256
k = 4000
kpos = 100
m = 200