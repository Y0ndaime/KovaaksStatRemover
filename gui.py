import json
from tkinter import *
from tkinter import filedialog
import os
import csv


class Gui:
    def __init__(self, **kwargs):
        # Read config and initialize Variables for Gui
        self.config = kwargs
        self.window = Tk()
        self.window.title("Stat Remover")
        self.window.geometry("550x400")
        self.path = StringVar()
        self.threshold = StringVar()
        self.above_under = StringVar()
        self.scenario = StringVar()
        self.scenario.trace('w', self.on_change)
        self.scen_list = self.get_scen_list()
        self.all_stats = list(sorted(os.listdir(config['stats_path'])))

        # Give startvalue to variables
        self.above_under.set("above")
        self.threshold.set("0")
        self.path.set(self.config["stats_path"])
        self.above_under_options = ["above", "under"]

    def browse_path(self):
        self.path.set(filedialog.askdirectory(initialdir=self.path.get(), title="Open Stats Folder"))

    def main(self):
        # Gui for path
        path_frame = Frame(self.window)
        pre_path_label = Label(path_frame, text="Kovaak's Stats Path: ")
        browse_path_button = Button(path_frame, text="Browse", command=self.browse_path)
        path_label = Label(path_frame, textvariable=self.path)
        pre_path_label.pack(side="left")
        path_label.pack(side="left")
        browse_path_button.pack(side="right")

        advanced_padding = 25
        settings_frame = Frame(self.window)

        # Threshold
        threshold_frame = Frame(self.window)
        threshold_entry = Entry(threshold_frame, textvariable=self.threshold)
        pre_threshold_label = Label(threshold_frame, text="Score Threshold: ")
        pre_threshold_label.pack(side="left")
        threshold_entry.pack(fill="x")

        # Listbox (code for this and methods for listbox from
        # https://stackoverflow.com/questions/47839813/python-tkinter-autocomplete-combobox-with-like-search
        listbox_frame = Frame(settings_frame)
        list_box_entry = Entry(listbox_frame, textvariable=self.scenario)
        list_box_entry.pack(fill="x")

        self.listbox = Listbox(listbox_frame)
        self.listbox.pack(fill="x")
        self.listbox.bind('<<ListboxSelect>>', self.on_select)
        self.listbox_update(self.scen_list)
        listbox_frame.pack(fill="x")

        # Above/under
        above_under_frame = Frame(settings_frame)
        above_under_label_left = Label(settings_frame, text="Delete scores ")
        above_under_label_right = Label(settings_frame, text="threshold ")
        above_under_dropdown = OptionMenu(settings_frame, self.above_under, *self.above_under_options)
        above_under_label_left.pack(side="left")
        above_under_dropdown.pack(side="left")
        above_under_label_right.pack(side="left")
        above_under_frame.pack(padx=advanced_padding, side="top")

        # Finished/Exit buttons
        finished_frame = Frame(self.window)
        delete_button = Button(finished_frame, command=self.delete_score, text="Delete")
        delete_button.grid(row="1", column="0", columnspan="2")
        finished_button = Button(finished_frame, command=self.exit, text="Finish")
        finished_button.grid(row="1", column="2", columnspan="2")

        # Message Label
        message_frame = Frame(self.window)
        self.message_label = Label(message_frame)
        self.message_label.pack(fill="x")

        # Pack all frames and run mainloop
        path_frame.pack(fill="x")
        threshold_frame.pack(fill="x")
        settings_frame.pack(fill="x")
        finished_frame.pack()
        message_frame.pack(fill="x")

        self.window.mainloop()

    @staticmethod
    def get_scen_list():
        stats = set(
            map(lambda stat: stat[0:stat.find(" - Challenge - ")], list(sorted(os.listdir(config['stats_path'])))))
        return list(stats)

    def delete_score(self):
        counter = 0
        for file in self.all_stats:
            if self.scenario.get().lower() == file[0:file.find(" - Challenge - ")].lower():
                score = self.read_score_from_file(f'{config["stats_path"]}/{file}')
                if self.above_under.get() == "above":
                    if score >= float(self.threshold.get()):
                        os.remove(f'{config["stats_path"]}/{file}')
                        counter += 1
                else:
                    if score <= float(self.threshold.get()):
                        os.remove(f'{config["stats_path"]}/{file}')
                        counter += 1
        self.message_label.config(text=f'Just deleted {counter} {self.scenario.get()} stats.')

    def exit(self):
        self.config["stats_path"] = self.path.get()
        with open("config.json", "w") as outfile:
            json.dump(self.config, outfile, indent=4)
        self.window.destroy()

    def on_change(self, *args):
        value = self.scenario.get()
        value = value.strip().lower()

        if value == '':
            data = self.scen_list
        else:
            data = []
            for item in self.scen_list:
                if value in item.lower():
                    data.append(item)

        # update data in listbox
        self.listbox_update(data)

    def listbox_update(self, data):
        # delete previous data
        self.listbox.delete(0, 'end')

        # sorting data
        data = sorted(data, key=str.lower)

        # put new data
        for item in data:
            self.listbox.insert('end', item)

    def on_select(self, event):
        # display element selected on list
        self.scenario.set(event.widget.get(event.widget.curselection()))

    @staticmethod
    def read_score_from_file(file_path: str) -> float:
        with open(file_path, newline='') as csvfile:
            for row in csv.reader(csvfile):
                if row and row[0] == 'Score:':
                    return round(float(row[1]), 1)
        return 0.0


config_file = 'config.json'
if not os.path.isfile(config_file):
    sys.exit(1)
config = json.load(open(config_file, 'r'))
gui = Gui(**config)
gui.main()
