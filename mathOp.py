import re
from termcolor import colored as coloured


# compile our regular expression patterns
pattern = re.compile("(?<=[0-9])(?=([-+*/\^]|$))")
sectionX = re.compile("[0-9]+(\*{2}|\^)[0-9]+")
section = re.compile("[0-9]+(\*|\/)[0-9]+")
xmatch = re.compile("\*{1,2}|\^|\/")

def floatify(x, default=0):
    try: return float(x)
    except: return default

# count how many order / division / multiplication terms are present in an equation
def countX(x):
    return len(xmatch.findall(x))

# embrace ODM terms in a braces / parentheses block
def embraceX(x):
    x_ = x

    # orders are prioritised
    for a in sectionX.finditer(x):
        if "**" not in x_:
            break
        t = x[a.start() : a.end()]
        x_ = x_.replace(t, f"({t})")

    # division and multiplication operations follow after
    for a in sectionX.finditer(x):
        t = x[a.start() : a.end()]
        x_ = x_.replace(t, f"({t})")

    return x_

def solveEquation(eqstr, verbose=False):
    terms = []
    total = 0

    # last start index
    lastIndex = 0

    # remove whitespace from the equation string
    eqstr = eqstr.replace(" ", "")

    # embrace x blocks
    if countX(eqstr) > 1:
        eqstr = embraceX(eqstr)

    # check if parentheses count checks out
    if eqstr.count("(") - eqstr.count(")") != 0:
        print("A parentheses block isn't closed.")
        return total

    # parentheses block variables
    depth = 0
    blockStart = 0
    finalEqstr = eqstr

    # solve parentheses blocks
    for i in range(len(eqstr)):
        # set the start of block
        if eqstr[i] == '(':
            if depth == 0:
                blockStart = i

            # increase our block depth
            depth += 1

        # terminate parentheses check when block depth is zero
        if eqstr[i] == ')':
            depth -= 1

            # block zero depth
            if depth == 0:
                parenthesesBlock = eqstr[blockStart + 1 : i]

                # solve the extracted equation
                result = str(solveEquation(parenthesesBlock, verbose))

                # and replace the parentheses block with our result
                finalEqstr = finalEqstr.replace(f"({parenthesesBlock})", f"b{result}")

    # split equation string into terms
    for match in pattern.finditer(finalEqstr):
        term = finalEqstr[lastIndex : match.start()]
        lastIndex = match.start()

        # insert it to our terms list
        terms.append(term)

    # our queue of arithmetical operations
    operationsQueue = []

    # reference to our last term
    lastTerm = 0

    # re-order operations in a queue according to the BODMAS / PEMDAS order of operations
    for term in terms:
        if verbose: print(f"Term: {term}, Last Term: {lastTerm}")

        # reorder equation (so it complies to the order of operations properly)
        if term.startswith('**') or term.startswith('^') or term.startswith('*') or term.startswith('/'):
            if lastTerm in operationsQueue:
                operationsQueue.remove(lastTerm)

            # insert it with our ODM terms
            if type(lastTerm) is not list:
                lastTerm = [lastTerm, term]
            else:
                lastTerm = lastTerm + [term]

            operationsQueue.insert(0, lastTerm)
        else:
            # add operation to queue
            operationsQueue.append(term)
            # last term reference
            lastTerm = term

    # turn our items into tuples
    operationsQueue = [tuple(x) if type(x) is list else tuple([x]) for x in operationsQueue]

    # join terms back together
    if verbose: print(f"\n{operationsQueue}")

    # solve it, at long last
    for queueItem in operationsQueue:
        # current item total
        itemTotal = 0

        # evaluate items in our queue
        for item in queueItem:
            # strip brackets marker
            if 'b' in item:
                item = item.replace('b', '')

            # determine which operation we should use
            # ORDER operations
            # power / repeated multiplication
            if item.startswith('^'):
                itemTotal **= floatify(item[1::])

            elif item.startswith("**"):
                itemTotal **= floatify(item[2::])


            # DM operations
            # multiplication operation
            elif item.startswith('*'):
                itemTotal *= floatify(item[1::])

            # division operation
            elif item.startswith('/'):
                try:
                    itemTotal /= floatify(item[1::])
                except ZeroDivisionError:
                    print(f"Trying to divide by zero! Excluding {item} from this equation.")

            # AS operations
            # subtraction operation
            elif item.startswith('-'):
                itemTotal -= floatify(item[1::])

            # addition operation
            elif item.startswith('+'):
                itemTotal += floatify(item[1::])
            else:
                # if a term has no operation symbol, use addition, by default
                itemTotal += floatify(item)

        # combine the totals
        total += itemTotal

    # return the result of our equation
    return total


def solve(x):
    print(f"\nSolving for \"{x}\"...")
    print(coloured(f"{solveEquation(x, True):,.2f}", "blue"))


# solve a bunch of equations
solve("(10 * 50) * ((20 + 5) * 100)") # expected: 1,250,000
solve("((((50 + 20) - 30) * 10) + ((30 / 2) * 12)) / 10") # expected: 58
solve("10 - 30 * ((50) + (20)) - 10") # expected: -2,100
solve("(2 ** 8) ** 2") # expected: 65,536
solve("((10 + 5) * 12) - (12 + 5)") # expected: 163
solve("7 - 1 * 0 + 3 / 3") # expected: 8
solve("1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 * 0 + 1") # expected: 12
solve("2 + (10 * 20 + 30 / 10 * 3) + (50)") # expected: 261
solve("10 * 20 + 30 / 10 * 3") # expected: 209
solve("2 + (10 * 20 + 30 / 10 * 3) + (50) * 12 / 12 * 32 * 32 / 20") # expected 2,771
solve("2 * 2 * 2 * 2 * 2 * 2 + 12 ** 3 * 2 / 100 * 3") # expected 167.68
solve("5 / 10 * 30 / 10 + (2 ** 8 - 20 / 2 * 30)") # expected -42.5
solve("1200 + 2800 * 30 + (50 + (20 * (30) - 12) * 2) + 8 ** 4 / 2 + 1 - 100") # expected 88,375
solve("2 * 3 ** 4 * 5 ** 6 * 2 * 7 / 100 / 20 / 50") # expected 354.375
solve("(20 * 30) * (20 * (2 ** 3 / 1000)) * (((30 * 20) + 10 - 30) - 10 * 20) / 50 / 10") # expected 72.96
solve("4^3 * 12 / 2") # expected 384
solve("2^2^2 + 30/2^3") # expected 19.75
