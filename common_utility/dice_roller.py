import random
def open_roll(n):
    tmp = random.randint(1,n)
    if tmp == n:
        return (n-1) + open_roll(n)
    return tmp
def drn(): return open_roll(6)
def DRN(): return drn()+drn()

if __name__ == '__main__':
    N = 1000
# MC method
    for i in range(-10,10):
        answers = [(i+DRN() > DRN()) for k in range(N)]
        chance = answers.count(True) * (100.0/N)
        print i,chance


# expected values
    term = 0
    for i in range(10):
        term += 1./6**(i+1) * (5*i + (1+2+3+4+5+5))
        print i,term
