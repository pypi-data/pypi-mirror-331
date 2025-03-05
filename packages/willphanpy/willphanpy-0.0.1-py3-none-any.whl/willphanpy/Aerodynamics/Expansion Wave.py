import sympy as sym
import numpy as np
import math
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import messagebox


class GUI_ThanhNha:
    def __init__(self, root):
        self.root = root
        self.root.title('EXPANSION WAVE')
        self.root.geometry('800x400')

        # Upstream Mach Value
        UpstreamMach_text = StringVar()
        UpstreamMach_label = Label(root, text = 'Upstream Mach', font = ('bold',14), pady =20)
        UpstreamMach_label.grid(row = 0, column = 0, sticky = W)
        UpstreamMach_entry = Entry(root, textvariable = UpstreamMach_text)
        UpstreamMach_entry.grid(row = 0, column = 1)
        # Specific Heat
        Gamma_text = StringVar()
        Gamma_label = Label(root, text = 'Gamma', font = ('bold',14), pady =20)
        Gamma_label.grid(row = 1, column = 0, sticky = W)
        Gamma_entry = Entry(root, textvariable = Gamma_text)
        Gamma_entry.grid(row = 1, column = 1)
        # Deflection Abgle (Theta)
        Theta_text = StringVar()
        Theta_label = Label(root, text = 'Deflection Angle', font = ('bold',14), pady =20)
        Theta_label.grid(row = 2, column = 0, sticky = W)
        Theta_entry = Entry(root, textvariable = Theta_text)
        Theta_entry.grid(row = 2, column = 1)
        # Mach downstream Result
        DownstreamMach_text = StringVar()
        DownstreamMach_label = Label(root, text = 'Downstream Mach', font = ('bold',14), pady =20, padx=60)
        DownstreamMach_label.grid(row = 0, column = 2, sticky = W)
        DownstreamMach_entry = Entry(root, textvariable = DownstreamMach_text)
        DownstreamMach_entry.grid(row = 0, column = 3)
        # Pressure Ratio downstream Result
        Pre_text = StringVar()
        Pre_label = Label(root, text = 'Downstream Pressure Ratio', font = ('bold',14), pady =20, padx=30)
        Pre_label.grid(row = 1, column = 2, sticky = W)
        Pre_entry = Entry(root, textvariable = Pre_text)
        Pre_entry.grid(row = 1, column = 3)
        # Temperature Ratio downstream Result
        Tem_text = StringVar()
        Tem_label = Label(root, text = 'Downstream Temperature Ratio', font = ('bold',14), pady =20, padx=10)
        Tem_label.grid(row = 2, column = 2, sticky = W)
        Tem_entry = Entry(root, textvariable = Tem_text)
        Tem_entry.grid(row = 2, column = 3)

        def solving():
            M = float(UpstreamMach_text.get())
            t = float(Theta_text.get())
            M_begin = M
            y = float(Gamma_text.get())

            x = sym.symbols('x')
            g = ((x**2-1)**(0.5))/((1+((y-1)/2)*x**2)*x)
            h = sym.lambdify(x, g, 'numpy')

            X = []
            Y = []

            dM = 0.001  #increment
            f = 0
            for i in range(1000):
                df = (((h(M+dM)+h(M))/2)*dM)*180/math.pi
                f = f + df
                if f >= t:
                    break
                else:
                    M = M + dM
                    X.append(f)
                    Y.append(M)
            DownstreamMach_text.set(M)

            # Calculate the pressure ratio p2/p1
            ratio = ((1+0.5*(y-1)*M_begin**2)/(1+0.5*(y-1)*M**2))**(y/(y-1))
            Pre_text.set(ratio)
            Tem_text.set(ratio**((y-1)/y))
            #Plotting
            plt.plot(X, Y)
            plt.title('Expansion Wave')
            plt.ylabel('Mach Number')
            plt.xlabel('Deflection Angle')
            plt.show()
        def reset():
            UpstreamMach_text.set('')
            Gamma_text.set('')
            Theta_text.set('')
            DownstreamMach_text.set('')
            Pre_text.set('')
            Tem_text.set('')
        def exit():
            root.destroy()

        # Buttons
        btn_calculate = Button(root, text='Calculate', width=8, command=solving).grid(row=3, column=0, pady=70)
        btn_reset = Button(root, text='Reset', width=8, command=reset).grid(row = 3, column=1,pady=20)
        btn_exit = Button(root, text='Exit', width=8, command=exit).grid(row = 3, column=2,pady=20)
if __name__=='__main__':
    root = Tk()
    application = GUI_ThanhNha(root)
    root.mainloop()



