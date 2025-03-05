
import sympy as sym
import numpy as np
import math
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import messagebox

class GUI_ThanhNha:
    def __init__(self, root):
        self.root = root
        self.root.title('VELOCITY MEASUREMENT')
        self.root.geometry('500x350')

        # Ratio
        Ratio_text = StringVar()
        Ratio_label = Label(root, text = 'Ratio of p02/p1', font = ('bold',14), pady =20)
        Ratio_label.grid(row = 0, column = 0, sticky = W)
        Ratio_entry = Entry(root, textvariable = Ratio_text)
        Ratio_entry.grid(row = 0, column = 1)
        # Gamma
        Gamma_text = StringVar()
        Gamma_label = Label(root, text = 'Gamma', font = ('bold',14), pady =20)
        Gamma_label.grid(row = 1, column = 0, sticky = W)
        Gamma_entry = Entry(root, textvariable = Gamma_text)
        Gamma_entry.grid(row = 1, column = 1)
        # Initial Value for Mach
        Ini_text = StringVar()
        Ini_label = Label(root, text = 'Initial Value for Mach number', font = ('bold',14), pady =20)
        Ini_label.grid(row = 2, column = 0, sticky = W)
        Ini_entry = Entry(root, textvariable = Ini_text)
        Ini_entry.grid(row = 2, column = 1)
        # Mach
        Mach_text = StringVar()
        Mach_label = Label(root, text = 'Freestream Mach', font = ('bold',14), pady =20)
        Mach_label.grid(row = 3, column = 0, sticky = W)
        Mach_entry = Entry(root, textvariable = Mach_text)
        Mach_entry.grid(row = 3, column = 1)
        # Define calcualation for factorials
        def solving():
            r = float(Ratio_text.get())
            y = float(Gamma_text.get())
            x0 = float(Ini_text.get())

            x = sym.symbols('x')
            M_2 = ((1+(y-1)*x**2/2)/(y*x**2-(y-1)/2))**(0.5)
            p_0_2_over_p_2 = (1+((y-1)*M_2**2)/2)**(y/(y-1))
            p_2_over_p_1 = 1+(2*y*(x**2-1)/(y+1))
            h = p_0_2_over_p_2*p_2_over_p_1
            g = sym.lambdify(x, h, 'numpy') # using when flow is supersonic
            k = (1+((y-1)*x**2)/2)**(y/(y-1))
            u = sym.lambdify(x, k, 'numpy') # using when flow is subsonic

            #fine a root of an equation by using Newton method
            tol = 1e-6
            dx = 1e-10
            if r > g(1):
                f = sym.lambdify(x, h - r,'numpy')
                fd = (f(x+dx) - f(x-dx))/(2*dx)
                fd = sym.lambdify(x, fd, 'numpy')
                xn=x0
                for n in range(1000):
                    xnew=xn-f(xn)/fd(xn)
                    if abs(xnew - xn)<tol:
                        break
                    else:
                        xn = xnew
                Mach_text.set(xnew)
            elif r < g(1):
                f = sym.lambdify(x, k - r, 'numpy')
                fd = (f(x+dx) - f(x-dx))/(2*dx)
                fd = sym.lambdify(x, fd, 'numpy')
                xn=x0
                for n in range(1000):
                    xnew=xn-f(xn)/fd(xn)
                    if abs(xnew - xn)<tol:
                        break
                    else:
                        xn=xnew
                Mach_text.set(xnew)

            M_1 = np.linspace(1, 10, 100)
            M_12 = np.linspace(0, 1, 100)
            plt.plot(M_1,g(M_1), 'r', M_12, u(M_12), 'b')
            plt.xlabel('Mach')
            plt.ylabel('Ratio p_02/p_1')
            plt.legend(['Supersonic','Subsonic'])
            plt.show()
        def reset():
            Ratio_text.set('')
            Gamma_text.set('')
            Ini_text.set('')
            Mach_text.set('')
        def exit():
            root.destroy()

        # Buttons
        btn_calculate = Button(root, text='Calculate', width=8, command=solving).grid(row=4, column=0, pady=20)
        btn_reset = Button(root, text='Reset', width=8, command=reset).grid(row = 4, column=1,pady=20)
        btn_exit = Button(root, text='Exit', width=8, command=exit).grid(row = 4, column=2,pady=20)
if __name__=='__main__':
    root = Tk()
    application = GUI_ThanhNha(root)
    root.mainloop()