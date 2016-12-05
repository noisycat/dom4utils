import random
def open_roll(*args):
    if len(args) == 1:
	a = 1
	n = args[0]
    elif len(args) == 2:
	a = args[0]
	n = args[1]

    tmp = random.randint(a,n)
    if tmp == n:
        return (n-1) + open_roll(a,n)
    return tmp

def drn(): return open_roll(6)

def DRN(): return drn()+drn()

__all__ = ['open_roll','drn','DRN']

if __name__ == '__main__':
    import argparse
    from sys import maxint
    parser = argparse.ArgumentParser(description='Provides open ended rollers for dom4 simulation. Main program produces the charge located in the beginning on the dom4 manual')
    parser.add_argument('-N','--numtrials', type=int, default=1000, help='number of trials')
    parser.add_argument('--seed', type=int, default=random.randint(0,maxint), help='seed of random number generator')
    parser.add_argument('--table-limits', nargs=2, type=int, default=[-10,10], help='table limits')
    args = parser.parse_args()
    N = args.numtrials
# Monte Carlo method
    print("Differencing Chart")
    for i in range(args.table_limits[0],args.table_limits[1]+1):
        answers = [(i+DRN() > DRN()) for k in range(N)]
        chance = round(answers.count(True) * (100.0/N),3)
        print(i,chance)

