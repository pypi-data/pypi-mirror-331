class Wpya:
    def __init__(self):
        pass
    
    #calculate factorial of a non-negative number a (a!)
    @staticmethod
    def factorial(a):
        fac=1
        for i in range(1, a+1):
            fac=fac*i
        return fac

    #calculate a combinatorics of (n,k)
    @staticmethod
    def combinatorics(n, k):
        return Wpya.factorial(n)//(Wpya.factorial(k)*Wpya.factorial(n-k))

    #calculate an arrangement of (n,k)
    @staticmethod
    def arrangement(n,k):
        return Wpya.factorial(n)//Wpya.factorial(n-k)

    #calculate a permutation of (k)
    @staticmethod
    def permutation(k):
        return Wpya.factorial(k)

    #find a root of an equation using bisection method
    @staticmethod
    def bisection(f, a, b, loop):
        xn=(a+b)/2
        for n in range(loop):
            print(xn)
            if f(xn)==0:
                break
            if f(xn)*f(a)>0:
                a=xn
                xnew=(a+b)/2
            elif f(xn)*f(a)<0:
                b=xn
                xnew=(a+b)/2
            xn=xnew

    #find a root of an equation using iterative method
    @staticmethod
    def iterative(g, q, x0, tol, loop):
        xn=x0
        for n in range(loop):
            xnew=g(xn)
            if (q*abs(xnew-xn)/(1-q))<tol:
                break
            print(xnew)
            xn=xnew

    #find a root of an equation using Newton method
    @staticmethod
    def newton(f ,fd, x0, tol, loop):
        xn=x0
        for n in range(loop):
            xnew=xn-f(xn)/fd(xn)
            if abs(xnew - xn)<tol:
                break
            print(xnew)
            xn=xnew

    @staticmethod
    def seriessin():
        x = sym.symbols('x')
        b = 0
        for i in range(100):
            a = (-1)**i*(x**(2*i+1)/Wpya.factorial(2*i+1))
            b += a
        return b

    @staticmethod
    def seriescos():
        x = sym.symbols('x')
        b = 0
        for i in range(100):
            a = (-1)**i*(x**(2*i)/Wpya.factorial(2*i))
            b += a
        return b

    @staticmethod
    def read_excel(file: str):
        # Reading the Excel file
        data = pd.read_excel(file)

        # Display the first few rows
        return data.to_numpy()
    
    @staticmethod
    def randomInt(fromNumber: int, toNumber: int, size: int):
        return np.random.randint(fromNumber, toNumber + 1, size)

    # Algorithm that converts infix expression to postfix expression
    @staticmethod
    def infixToPostfix(infix: str) -> str:
        power1 = ['+', '-']
        power2 = ['*', '/']
        parenthesis = ['(', ')']
        operator = power1 + power2
        postfix = ''

        stack = [] # stack

        for i in range(len(infix)):
            e = infix[i]
            if(e not in operator + parenthesis):
                postfix = postfix + e
                continue

            if(e in operator):
                if(len(stack) == 0):
                    stack.append(e)
                    continue

                if(stack[-1] in power2):
                    postfix = postfix + stack.pop()
                    stack.append(e)

                else:
                    stack.append(e)

                continue

            if(e in parenthesis):
                if(e == '('):
                    stack.append(e)
                
                else:
                    while(stack[-1] != '('):
                        postfix = postfix + stack.pop()

                    stack.pop() # remove the openning parenthesis
                    
        while(True):
            if(len(stack) == 0):
                break
            postfix = postfix + stack.pop()
        return postfix

    # Algorithm that converts postfix expression back to infix expression
    @staticmethod
    def evaluatePostfix(postfix: str) -> int:
        stack = []
        power1 = ['+', '-']
        power2 = ['*', '/']
        operator = power1 + power2

        for i in range(len(postfix)):
            e = postfix[i]

            if(e not in operator):
                stack.append(e)
                continue

            pop_2 = stack.pop()
            pop_1 = stack.pop()

            match(e):
                case '+':
                    stack.append(int(pop_1) + int(pop_2))
                case '-':
                    stack.append(int(pop_1) - int(pop_2))
                case '*':
                    stack.append(int(pop_1) * int(pop_2))
                case '/':
                    stack.append(int(pop_1) / int(pop_2))

        return stack.pop()


