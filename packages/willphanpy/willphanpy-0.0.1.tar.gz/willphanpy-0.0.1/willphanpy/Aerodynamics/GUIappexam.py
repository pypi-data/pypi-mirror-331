import sympy as sym
import numpy as np
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import messagebox


class GUI_ThanhNha:
    def __init__(self, root):
        self.root = root
        self.root.title('NAME')
        self.root.geometry('360x350')

        # An integer number
        Ratio_text = StringVar()
        Ratio_label = Label(root, text = 'Ratio', font = ('bold',14), pady =20)
        Ratio_label.grid(row = 0, column = 0, sticky = W)
        Ratio_entry = Entry(root, textvariable = Ratio_text)
        Ratio_entry.grid(row = 0, column = 1)
        # Factorials
        Gamma_text = StringVar()
        Gamma_label = Label(root, text = 'Gamma', font = ('bold',14), pady =20)
        Gamma_label.grid(row = 1, column = 0, sticky = W)
        Gamma_entry = Entry(root, textvariable = Gamma_text)
        Gamma_entry.grid(row = 1, column = 1)
        #
        Ini_text = StringVar()
        Ini_label = Label(root, text = 'Ini', font = ('bold',14), pady =20)
        Ini_label.grid(row = 2, column = 0, sticky = W)
        Ini_entry = Entry(root, textvariable = Ini_text)
        Ini_entry.grid(row = 2, column = 1)
        # Mach
        Mach_text = StringVar()
        Mach_label = Label(root, text = 'Mach', font = ('bold',14), pady =20)
        Mach_label.grid(row = 3, column = 0, sticky = W)
        Mach_entry = Entry(root, textvariable = Mach_text)
        Mach_entry.grid(row = 3, column = 1)
        # Define calcualation for factorials
        def factorial():
            r = float(Ratio_text.get())
            y = float(Gamma_text.get())
            x_o = float(Ini_text.get())
            x = sym.symbols('x')
            g = (1/x)*((2/(y+1))*(1+0.5*(y-1)*x**2))**(0.5*(y+1)/(y-1))
            f = sym.lambdify(x, g - r, 'numpy')
            dx = 0.001
            fd = (f(x+dx)-f(x-dx))/(2*dx)
            fd = sym.lambdify(x, fd, 'numpy')

            # Newton Iteration
            tol = 1e-6
            for i in range(1000):
                x_n = x_o - f(x_o)/fd(x_o)
                if abs(x_o - x_n) < tol:
                    break
                else:
                    #print(x_o)
                    x_o = x_n
            Mach_text.set(x_n)
        def reset():
            Ratio_text.set('')
            Gamma_text.set('')
            Ini_text.set('')
            Mach_text.set('')
        def exit():
            root.destroy()

        # Buttons
        btn_calculate = Button(root, text='Calculate', width=8, command=factorial).grid(row=0, column=3, pady=20)
        btn_reset = Button(root, text='Reset', width=8, command=reset).grid(row = 1, column=3,pady=20)
        btn_exit = Button(root, text='Exit', width=8, command=exit).grid(row = 2, column=3,pady=20)
if __name__=='__main__':
    root = Tk()
    application = GUI_ThanhNha(root)
    root.mainloop()
