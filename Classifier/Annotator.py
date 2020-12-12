import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
import os
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib import style
import matplotlib.animation as animation
import seaborn as sns


heading = 'Helvetica 14 bold'
my_font = ('Times New Roman', 14)
cache = None
curr_twt = None
file_path = ''
stats = {
                    'completed': 0,
                    'remaining': 0,
                    'negative': 0,
                    'not negative': 0,
                    'undecided': 0,
                    'error': 0,
                    'unrelated': 0,
                }

class AnnotatorApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry('1125x620')
        self.title('Data Annotator')
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        self.segments = {}

        for S in (HeaderPane, FileMenu, MainPane, StatsPane):
            segment = S(container, self)
            self.segments[S] = segment

        file_menu = self.segments[FileMenu]
        self.config(menu=file_menu)

    def get_segment(self, segment):
        return self.segments[segment]


class HeaderPane(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        
        self.grid(row=1, column=0)
        self.widgets()
       
    def widgets(self):
         # file path
        self.output = tk.Text(self, state='disabled', width=60, height=3, wrap=tk.WORD, bg='gainsboro', borderwidth=2, relief='groove')
        self.output.grid(column=1, row=1, sticky='W', padx=(5, 0), pady=10)

    def display_file_details(self, msg):

        self.output.configure(state='normal')
        self.output.delete(1.0, tk.END)
        self.output.insert(tk.END, msg + '\n')
        self.output.configure(state='disabled')


class FileMenu(tk.Menu):
    def __init__(self, parent, controller):
        tk.Menu.__init__(self, parent)
        self.controller = controller
        file_menu = tk.Menu(self, tearoff=False)
        self.add_cascade(label='File', underline=0, menu=file_menu)
        file_menu.add_command(label='Open Json...', underline=1, command=self.open_file)
        file_menu.add_separator()
        file_menu.add_command(label='Save', underline=1, command=self.save)
        file_menu.add_command(label='Save As', underline=1, command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', underline=1, command=self.exit)

    def open_file(self):
        global cache
        global curr_twt
        global file_path
        global stats

        file_path = askopenfilename()
        file_details = os.path.splitext(file_path)
        header_pane = self.controller.get_segment(HeaderPane)
        
        if file_details[1] == '.json':
            
            header_pane.display_file_details('Current file: ' + str(file_path))

            with open(file_path, 'rb') as f:
                cache = json.load(f)
                curr_twt = 0
                stats = {
                    'completed': 0,
                    'remaining': 0,
                    'negative': 0,
                    'not negative': 0,
                    'undecided': 0,
                    'error': 0,
                    'unrelated': 0,
                }

            for twt in cache:
                if 'negative' in twt:
                    if twt['negative']:
                        stats['negative'] += 1
                    if not twt['negative'] and not twt['error'] and not twt['undecided'] and not twt['unrelated']:
                        stats['not negative'] += 1
                    if twt['error']:
                        stats['error'] += 1
                    if twt['undecided']:
                        stats['undecided'] += 1
                    if twt['unrelated']:
                        stats['unrelated'] += 1
                else:
                    stats['remaining'] += 1
            stats['completed'] = len(cache) - stats['remaining']

        else:
            header_pane.display_file_details('Select a valid .json file')

    @staticmethod
    def save():
        global cache
        with open(file_path, 'w') as f:
            json.dump(cache, f, indent=2)

    @staticmethod
    def save_as():
        global cache

        filename = asksaveasfilename(defaultextension='.json', filetypes=[('All files', '*.*')])
        if filename:
            with open(filename, 'w') as f:
                json.dump(cache, f, indent=2)
        else:
            return

    def exit(self):
        self.master.destroy()


class MainPane(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
       
        self.grid(row=2, column=0)

        

        #self.w = tk.OptionMenu(self, self.var, 'Open File', 'Recent', 'Save As', 'Save', 'Save & Exit')
        # ---Buttons---
        # Unrelated, undecided, error
        self.unrl_btn = tk.Button(self, text='Unrelated', width=10, command=self.unrelated)
        self.unrl_btn.grid(row=5, column=0, padx=5)

        self.undc_btn = tk.Button(self, text='Undecided', width=10, command=self.undecided)
        self.undc_btn.grid(row=4, column=0, padx=5, pady=5)

        self.error_btn = tk.Button(self, text='Error tweet', width=10, command=self.error_twt)
        self.error_btn.grid(row=6, column=0, padx=5, pady=5)
        # Yes, No
        self.yes_btn = tk.Button(self, text='Yes', width=10, command=self.yes)
        self.yes_btn.grid(row=4, column=1, padx=5)
        self.no_btn = tk.Button(self, text='No', width=10, command=self.no)
        self.no_btn.grid(row=4, column=2, padx=5)

        # Start
        self.start_btn = tk.Button(self, text='Start', width=15, command=self.display_current)
        self.start_btn.grid(row=0, column=3)
        # Next, Previous
        self.prev_btn = tk.Button(self, text='Prev', command=self.prev)
        self.prev_btn.grid(row=4, column=3, sticky='E')
        self.next_btn = tk.Button(self, text='Next', command=self.next)
        self.next_btn.grid(row=4, column=4, sticky='W')
        # jump buttons
        self.jump_btn = tk.Button(self, text='Jump to first unmarked', width=20, command=self.jump_to_unmarked)
        self.jump_btn.grid(row=4, column=5, padx=5, sticky='W')

        self.jump2_btn = tk.Button(self, text='Jump to first undecided', width=20, command=self.jump_to_undecided)
        self.jump2_btn.grid(row=5, column=5, padx=5, pady=5, sticky='W')

        self.jump3_btn = tk.Button(self, text='Jump to first unrelated', width=20, command=self.jump_to_unrelated)
        self.jump3_btn.grid(row=6, column=5, padx=5, pady=5, sticky='W')

        self.jump4_btn = tk.Button(self, text='Jump to first error', width=20, command=self.jump_to_error)
        self.jump4_btn.grid(row=7, column=5, padx=5, pady=5, sticky='W')

        self.jump5_btn = tk.Button(self, text='Jump to Tweet no.', width=15, command=self.jump_to_index)
        self.jump5_btn.grid(row=8, column=4, padx=5, sticky='W')

        self.tweet_idx_input = tk.Text(self, width=10, height=1)
        self.tweet_idx_input.configure(font=my_font)
        self.tweet_idx_input.grid(row=8, column=5, padx=5, pady=5, sticky='W')
        # ---Labels---
        self.main_lbl = tk.Label(self, font=heading, text='Mark Tweet')
        self.main_lbl.grid(row=0, column=1, columnspan=2, padx=5, pady=(10, 5))

       

        self.mark_btns_lbl = tk.Label(self, text='Mark Tweet', font=heading)
        self.mark_btns_lbl.grid(row=3, column=0, columnspan=3, pady=5)
        self.navi_btns_lbl = tk.Label(self, text='Navigation', font=heading)
        self.navi_btns_lbl.grid(row=3, column=4, pady=5, columnspan=2)
        # tweet number
        self.no_lbl = tk.Label(self, text='Tweet No.')
        self.no_lbl.grid(row=1, column=0, padx=5, pady=(20, 5), sticky='E')
        # marked
        self.marked_lbl = tk.Label(self, text='Yes/No?')
        self.marked_lbl.grid(row=1, column=2, padx=5, pady=(20, 5), sticky='E')
        # ---Outputs---
        
        # tweet number field
        self.txt_no = tk.Text(self, state='disabled', bg='gainsboro', foreground='blue', font=('Helvetica', 12, 'bold'),  width=6, height=1, borderwidth=2, relief='groove')
        self.txt_no.grid(row=1, column=1, padx=5, pady=(20, 5), sticky='W')
        # marked field
        self.marked_txt = tk.Text(self, state='disabled', bg='gainsboro', foreground='green', font=('Helvetica', 12, 'bold'), width=15, height=1, borderwidth=2, relief='groove')
        self.marked_txt.grid(row=1, column=3, padx=5, pady=(20, 5), sticky='W')
        # main output
        self.txt_output = tk.Text(self, state='disabled',  width=70, height=7, wrap=tk.WORD, bg='gainsboro', borderwidth=2, relief='groove')
        self.txt_output.grid(row=2, column=0, columnspan=6, padx=5, pady=5)
        self.txt_output.configure(font=my_font)

    def display_tweet(self, msg):
        self.txt_output.configure(state='normal')
        self.txt_output.delete(1.0, tk.END)
        self.txt_output.insert(tk.END, msg, '\n')
        self.txt_output.configure(state='disabled')

    def display_tweet_num(self, num):
        self.txt_no.configure(state='normal')
        self.txt_no.delete(1.0, tk.END)
        self.txt_no.insert(tk.END, num, '\n')
        self.txt_no.configure(state='disabled')

   
    def display_current(self):
        stats_pane = self.controller.get_segment(StatsPane)
        global curr_twt
        global cache

        try:
            if curr_twt is not None:
                twt = cache[curr_twt]['text']
                self.display_tweet(twt)
                self.display_tweet_num(str(curr_twt + 1))

        except Exception as e:
            self.display_tweet(e)
            print('-------------------------------------------------------------------------------')
            print(cache[curr_twt]['text'])
            self.display_tweet_num(str(curr_twt + 1))

        self.marked_txt.configure(state='normal')
        self.marked_txt.delete(1.0, tk.END)
        if 'negative' not in cache[curr_twt]:
            self.marked_txt.insert(tk.END, 'Unmarked', '\n')
        elif cache[curr_twt]['negative']:
            self.marked_txt.insert(tk.END, 'YES', '\n')
        elif cache[curr_twt]['unrelated']:
            self.marked_txt.insert(tk.END, 'Unrelated', '\n')
        elif cache[curr_twt]['undecided']:
            self.marked_txt.insert(tk.END, 'Undecided', '\n')
        elif cache[curr_twt]['error']:
            self.marked_txt.insert(tk.END, 'Error', '\n')
        else:
            self.marked_txt.insert(tk.END, 'NO', '\n')
        self.marked_txt.configure(state='disabled')

        stats_pane.display_stats()

   

    def unrelated(self):
        global cache
        global curr_twt
        if 'negative' in cache[curr_twt]:
            if cache[curr_twt]['unrelated']:
                return
            if not cache[curr_twt]['negative'] and not cache[curr_twt]['unrelated'] and not cache[curr_twt]['undecided'] and not cache[curr_twt]['error']:
                stats['not negative'] -= 1
            if cache[curr_twt]['negative']:
                stats['negative'] -= 1
            if cache[curr_twt]['undecided']:
                stats['undecided'] -= 1
            if cache[curr_twt]['error']:
                stats['error'] -= 1
        else:
            stats['completed'] += 1
            stats['remaining'] -= 1
        cache[curr_twt]['unrelated'] = True
        cache[curr_twt]['negative'] = False
        cache[curr_twt]['undecided'] = False
        cache[curr_twt]['error'] = False
        if curr_twt + 1 < len(cache):
            curr_twt += 1
        stats['unrelated'] += 1

        self.display_current()

    def undecided(self):
        global cache
        global curr_twt
        if 'negative' in cache[curr_twt]:
            if cache[curr_twt]['undecided']:
                return
            if not cache[curr_twt]['negative'] and not cache[curr_twt]['unrelated'] and not cache[curr_twt]['undecided'] and not cache[curr_twt]['error']:
                stats['not negative'] -= 1
            if cache[curr_twt]['negative']:
                stats['negative'] -= 1
            if cache[curr_twt]['unrelated']:
                stats['unrelated'] -= 1
            if cache[curr_twt]['error']:
                stats['error'] -= 1
        else:
            stats['completed'] += 1
            stats['remaining'] -= 1
        cache[curr_twt]['undecided'] = True
        cache[curr_twt]['negative'] = False
        cache[curr_twt]['unrelated'] = False
        cache[curr_twt]['error'] = False
        if curr_twt + 1 < len(cache):
            curr_twt += 1
        stats['undecided'] += 1

        self.display_current()

    def error_twt(self):
        global cache
        global curr_twt
        if 'negative' in cache[curr_twt]:
            if cache[curr_twt]['error']:
                return
            if not cache[curr_twt]['negative'] and not cache[curr_twt]['unrelated'] and not cache[curr_twt]['undecided'] and not cache[curr_twt]['error']:
                stats['not negative'] -= 1
            if cache[curr_twt]['negative']:
                stats['negative'] -= 1
            if cache[curr_twt]['undecided']:
                stats['undecided'] -= 1
            if cache[curr_twt]['unrelated']:
                stats['unrelated'] -= 1
        else:
            stats['completed'] += 1
            stats['remaining'] -= 1
        cache[curr_twt]['error'] = True
        cache[curr_twt]['undecided'] = False
        cache[curr_twt]['negative'] = False
        cache[curr_twt]['unrelated'] = False
        if curr_twt + 1 < len(cache):
            curr_twt += 1
        stats['error'] += 1

        self.display_current()

    def yes(self):
        global cache
        global curr_twt
        if 'negative' in cache[curr_twt]:
            if cache[curr_twt]['negative']:
                return
            if not cache[curr_twt]['negative'] and not cache[curr_twt]['unrelated'] and not cache[curr_twt]['undecided'] and not cache[curr_twt]['error']:
                stats['not negative'] -= 1
            if cache[curr_twt]['unrelated']:
                stats['unrelated'] -= 1
            if cache[curr_twt]['undecided']:
                stats['undecided'] -= 1
            if cache[curr_twt]['error']:
                stats['error'] -= 1
        else:
            stats['completed'] += 1
            stats['remaining'] -= 1
        cache[curr_twt]['negative'] = True
        cache[curr_twt]['unrelated'] = False
        cache[curr_twt]['undecided'] = False
        cache[curr_twt]['error'] = False
        if curr_twt + 1 < len(cache):
            curr_twt += 1
        stats['negative'] += 1

        self.display_current()

    def no(self):
        global cache
        global curr_twt
        if 'negative' in cache[curr_twt]:
            if not cache[curr_twt]['negative'] and not cache[curr_twt]['unrelated'] and not cache[curr_twt]['undecided'] and not cache[curr_twt]['error']:
                return
            if cache[curr_twt]['negative']:
                stats['negative'] -= 1
            if cache[curr_twt]['unrelated']:
                stats['unrelated'] -= 1
            if cache[curr_twt]['undecided']:
                stats['undecided'] -= 1
            if cache[curr_twt]['error']:
                stats['error'] -= 1
        else:
            stats['completed'] += 1
            stats['remaining'] -= 1
        cache[curr_twt]['negative'] = False
        cache[curr_twt]['unrelated'] = False
        cache[curr_twt]['undecided'] = False
        cache[curr_twt]['error'] = False
        if curr_twt + 1 < len(cache):
            curr_twt += 1
        stats['not negative'] += 1

        self.display_current()

    def next(self):
        global curr_twt
        if curr_twt + 1 < len(cache):
            curr_twt += 1
        self.display_current()

    def prev(self):
        global curr_twt
        if curr_twt > 0:
            curr_twt -= 1
            self.display_current()
        else:
            return

    def jump_to_unmarked(self):
        global cache
        global curr_twt
        idx = 0
        for twt in cache:
            if 'negative' not in twt:
                curr_twt = idx
                self.display_current()
                break
            else:
                idx += 1

    def jump_to_undecided(self):
        global cache
        global curr_twt
        idx = 0
        for twt in cache:
            if 'undecided' in twt and twt['undecided']:
                curr_twt = idx
                self.display_current()
                break
            else:
                idx += 1

    def jump_to_unrelated(self):
        global cache
        global curr_twt
        idx = 0
        for twt in cache:
            if 'unrelated' in twt and twt['unrelated']:
                curr_twt = idx
                self.display_current()
                break
            else:
                idx += 1

    def jump_to_error(self):
        global cache
        global curr_twt
        idx = 0
        for twt in cache:
            if 'error' in twt and twt['error']:
                curr_twt = idx
                self.display_current()
                break
            else:
                idx += 1

    def jump_to_index(self):
        global curr_twt
        index = self.tweet_idx_input.get(1.0, tk.END)
        try:
            idx_int = int(index)
        except ValueError:
            return
        if idx_int <= len(cache):
            curr_twt = idx_int - 1
            self.display_current()
        else:
            return

class StatsPane(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.grid(row=1, column=1, rowspan=2, sticky='N')

        self.side_lbl = tk.Label(self, text='Info', font=heading)
        self.side_lbl.grid(row=0, column=0)

        # Info field
        self.stats_display = tk.Text(self, state='disabled', width=25, height=15, wrap=tk.WORD, bg='gainsboro',
                                     borderwidth=2, relief='groove')
        self.stats_display.grid(row=1, column=0, sticky='ns')
        self.stats_display.configure(font=my_font)

        sns.set_style('darkgrid', {'axes.linewidth': 1, 'axes.edgecolor': 'black'})
        self.fig = plt.Figure(figsize=(5, 3), dpi=80, facecolor='gainsboro')

        self.ax1 = self.fig.add_subplot(111)
        # plt.gcf().subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
        canvas = FigureCanvasTkAgg(self.fig, self)
        ani = animation.FuncAnimation(self.fig, self.animate, interval=1000)
        canvas.draw()
        canvas.get_tk_widget().grid(row=2, column=0, sticky='w')

    def animate(self, i):
            xs = []
            ys = []

            for stat in stats.items():
                if stat[0] not in {'remaining', 'completed'}:
                    xs.append(stat[0])
                    ys.append(stat[1])

            self.ax1.clear()
            bar_list = self.ax1.bar(xs, ys)
            self.ax1.tick_params(labelsize=8)
            bar_list[0].set_color('red')
            bar_list[1].set_color('green')
            bar_list[2].set_color('orange')
            bar_list[3].set_color('yellow')
            bar_list[4].set_color('blue')


    def display_stats(self):
        comp = stats['completed']
        rem = stats['remaining']
        neg = stats['negative']
        not_neg = stats['not negative']
        err = stats['error']
        und = stats['undecided']
        unr = stats['unrelated']
        try:
            neg_perc = neg/comp*100
            not_neg_perc = not_neg/comp*100
            err_perc = err/comp*100
            und_perc = und/comp*100
            unr_perc = unr/comp*100
        except ZeroDivisionError:
            neg_perc = 0
            not_neg_perc = 0
            err_perc = 0
            und_perc = 0
            unr_perc = 0

        info = f" Completed:     {comp} of {len(cache)}\n Remaining:      {rem}\n----------------------------------\n" \
            f" Negative:         {neg}  {neg_perc:.1f}%\n Not Negative:  {not_neg}  {not_neg_perc:.1f}%\n----------------------------------\n" \
            f" Error Tweets:  {err}  {err_perc:.1f}%\n Undecided:     {und}  {und_perc:.1f}%\n Unrelated:       {unr}  {unr_perc:.1f}%"
        self.stats_display.configure(state='normal')
        self.stats_display.delete(1.0, tk.END)
        self.stats_display.insert(tk.END, info)
        self.stats_display.configure(state='disabled')

def main():
    app = AnnotatorApp()
    #master.geometry('1125x620')
    #master.title('Data Annotator')

    #main_bar = MainBar(master)
    app.mainloop()


if __name__ == '__main__':
    main()