import sys
from argparse import ArgumentParser

if __name__ == "__main__":

    parser = ArgumentParser(description="Steiner triple systems (CSPLib prob044) solved with Glucose.")
    parser.add_argument("-i", "--input", default="input.in", type=str,
                        help="The instance file (contains the order n).")
    parser.add_argument("-n", "--order", type=int,
                        help="The order n given directly (then the input file is not read).")
    args = parser.parse_args()

    # get the input instance
    #the instance file contains a single number: the order n (the number of points)
    n = args.order if args.order is not None else int(open(args.input).read().split()[0])
    if n < 1:
        sys.exit("The order n has to be a positive integer.")
    print("order n = " + str(n))