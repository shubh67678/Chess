import math
# from collections import Counter


# def to_int(a):
#     temp = 1
#     ans = 0
#     for i in reversed(a):
#         ans += i*temp
#         temp = temp*10
#     return ans


# a = [2, 0, 0, 0]
# a1 = [i for i in a]
# a2 = [j for j in a]

# a1.sort()
# a2.sort(reverse=True)

# ans = []

# for i in range(100):
#     n1 = to_int(a1)
#     n2 = to_int(a2)
#     print(n1, n2)
#     if n1 > n2:
#         x = n1-n2
#     else:
#         x = n2-n1

#     # ans.append(n1)
#     # ans.append(n2)
#     ans.append(x)
#     x = str(x)
#     a = [int(i) for i in x]
#     a1 = [i for i in a]
#     a2 = [j for j in a]
#     a1.sort()
#     a2.sort(reverse=True)
#     # print(a, a1, a2, x)
# a = Counter(ans).most_common()
# print(a)
a = 0
ans = 0
a1 = 0
x = 15
for i in range(6):
    a = (-1)**i
    a = a * (x**(2*i+1))
    a = a/math.factorial(2*i+1)
    ans += a
ans = ans * ans
a1 += ans
ans = 0
for i in range(6):
    a = (-1)**i
    a = a * (x**(2*i))
    a = a/math.factorial(2*i)
    ans += a
a1 += ans*ans
a1 += 6
print(a1)
a = 1 + 5**0.5
a = a / 2
area = 0.5 * (a**0.5)
a1 += area
print(a1)
