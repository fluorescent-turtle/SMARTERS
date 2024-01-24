import tkinter as tk
from tkinter import Tk, ttk

from simulator import begin_simulation, Simulator


class SimulatorWindow(Tk):

    def __init__(self):
        super().__init__()

        # window title
        self.title("Smarters")

        window_width = 500
        window_height = 500

        # get the screen dimension
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # find the center point
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)

        # set the position of the window to the center of the screen
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        # parameters entry
        frame = ttk.Frame(self)
        frame.place(anchor='center')

        # field options
        options = {'padx': 20, 'pady': 20}

        # frame label
        frame_label = ttk.Label(self, text='Simulator features', font=('Arial', 18))
        frame_label.grid(row=1, column=0, columnspan=3, **options)

        # tassel's dimension
        first_label = ttk.Label(frame, text='Dimension of the tassel (m): ')
        first_label.grid(column=0, row=2, sticky='W', **options)

        self.tassel_dim = tk.StringVar()
        self.tassel_dim.set(str(0.5))
        tassel_dim_entry = ttk.Entry(frame, textvariable=self.tassel_dim)
        tassel_dim_entry.grid(column=1, row=2, **options)
        tassel_dim_entry.focus()

        # cutting cycle time
        second_label = ttk.Label(frame, text='Cutting cycle time (h): ')
        second_label.grid(column=0, row=3, sticky='W', **options)

        self.cutting_cycle = tk.IntVar()
        cutting_cycle_entry = ttk.Entry(frame, textvariable=self.cutting_cycle)
        cutting_cycle_entry.grid(column=1, row=3, **options)
        cutting_cycle_entry.focus()

        # repetition's times
        third_label = ttk.Label(frame, text='Repetition times: ')
        third_label.grid(column=0, row=4, sticky='W', **options)

        self.repetitions = tk.IntVar()
        repetitions_entry = ttk.Entry(frame, textvariable=self.repetitions)
        repetitions_entry.grid(column=1, row=4, **options)
        repetitions_entry.focus()

        # Next button
        next_button = tk.Button(self, text="Next", command=self.click_next)
        next_button.place(x=350, y=400)

        # add padding to the frame and show it
        frame.grid(padx=20, pady=20)

    def click_next(self):
        begin_simulation(Simulator(tassel_dimension=float(self.tassel_dim.get()),
                                   cutting_time=self.cutting_cycle.get(), repetitions=self.repetitions.get()))
