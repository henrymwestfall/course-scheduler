from pulp import LpAffineExpression, LpVariable


# define summation function (built-in sum does not work on Affine Expressions)
def summation(terms):
    """
    return a usable sum of `terms` where coefficients are 1
    """
    total = LpAffineExpression({t: 1 for t in terms})
    return total

def summation_test():
    """
    test the summation function and return a boolean of it's result.
    """

    test_1 = LpVariable("Test_1", lowBound = 0, upBound = 1, cat="Integer")
    test_2 = LpVariable("Test_2", lowBound = 0, upBound = 1, cat="Integer")
    test_3 = LpVariable("Test_3", lowBound = 0, upBound = 1, cat="Integer")
    if str(summation([test_1, test_2, test_3])) == "Test_1 + Test_2 + Test_3":
        print("Summation test passed.")
        return True
    else:
        print("Summation test failed.")
        return False