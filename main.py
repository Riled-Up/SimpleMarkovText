#!/usr/bin/python

import markov
import Tkinter as tk
import tkMessageBox
import pickle
import os

class MarkovChainWindow:
    def __init__(self, root):
        root.title("Markov Chain")
        # Makes widgets.
        self.top_frame = tk.Frame(root)
        self.output_text_frame = tk.Frame(root)
        self.output_text_label = tk.Label(self.output_text_frame, text = "Output Text:")
        self.output_text = tk.Text(self.output_text_frame, bd = 2, relief = "ridge", height = 19)
        self.input_text_frame = tk.Frame(self.top_frame)
        self.input_text_label = tk.Label(self.input_text_frame, text = "Input Text:")
        self.input_text = tk.Text(self.input_text_frame, bd = 2, relief = "ridge", height = 19)
        self.archive_frame = tk.Frame(self.top_frame)
        self.archive_current_frame = tk.Frame(self.archive_frame) 
        self.archive_current_label = tk.Label(self.archive_current_frame, text = "Current Archive:") 
        self.archive_current = tk.Entry(self.archive_current_frame)
        self.archive_current.bind("<Key>", self.archive_entry_changed)
        self.archive_list_frame = tk.Frame(self.archive_frame)
        self.archive_list_scrollbar = tk.Scrollbar(self.archive_list_frame)
        self.archive_list = tk.Listbox(self.archive_list_frame, yscrollcommand = self.archive_list_scrollbar.set, selectmode = 'single')
        self.archive_list.bind("<<ListboxSelect>>", self.archive_list_clicked)
        self.archive_list_scrollbar.config(command = self.archive_list.yview)
        self.update_archive_list()
        self.archive_list.activate('anchor')
        self.archive_current.insert(0, self.archive_list.get('active'))
        self.button_horizontal_frame = tk.Frame(self.archive_frame)
        self.button_new_archive = tk.Button(self.button_horizontal_frame, text = "New", command = self.new_archive)
        self.button_delete_archive = tk.Button(self.button_horizontal_frame, text = "Delete", command = 0)
        self.button_generate_output = tk.Button(self.archive_frame, text = "Generate Text from Archive", command = 0)
        self.button_add_to_archive = tk.Button(self.archive_frame, text = "Add Text to Archive", command = self.add_text_to_archive)
        # Packs widgets.
        self.top_frame.pack(fill = 'x')
        self.output_text_frame.pack(fill = "both", expand = True)
        self.output_text_label.pack()
        self.output_text.pack(fill = "both", expand = True)
        self.archive_frame.pack(side = "right")
        self.archive_current_frame.pack() 
        self.archive_current_label.pack()
        self.archive_current.pack(fill = 'x') 
        self.archive_list_frame.pack(fill = 'both', expand = True)
        self.archive_list_scrollbar.pack(side = "right", fill = 'y')
        self.archive_list.pack(side = "left", fill = 'both', expand = True)
        self.button_horizontal_frame.pack(fill = 'x')
        self.button_new_archive.pack(side = "left", fill = 'x', expand = True)
        self.button_delete_archive.pack(side = "right", fill = 'x', expand = True)
        self.button_generate_output.pack(side = "bottom", fill = 'x')
        self.button_add_to_archive.pack(side = "bottom", fill = 'x')
        self.input_text_frame.pack(side = "left", fill = "both", expand = True)
        self.input_text_label.pack()
        self.input_text.pack(fill = "both", expand = True)
    
    def save_obj(self, obj, name):
        with open('archives/'+ name + '.pkl', 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
    
    def load_obj(self, name):
        with open('archives/' + name + '.pkl', 'rb') as f:
            return pickle.load(f)
    
    def archive_list_clicked(self, event):
        if self.archive_list.curselection() == ():
            return 1
        self.archive_current.delete(0, 'end')
        self.archive_current.insert(0, self.archive_list.get(self.archive_list.curselection()))
    
    def archive_entry_changed(self, event):
        self.update_archive_list()
        index = 0
        for archive in self.archive_list.get(0, 'end'):
            if archive == self.archive_current.get() + event.char:
                self.archive_list.activate(index)
            else:
                index += 1
    
    def update_archive_list(self):
        self.archive_list.delete(0, 'end')
        for archive in os.listdir('archives/'):
            if archive[-4:] == '.pkl':
                self.archive_list.insert('end', archive[:-4])
                
    def new_archive(self):
        self.update_archive_list()
        for archive in os.listdir('archives/'):
            if archive[:-4] == self.archive_current.get():
                tkMessageBox.showwarning("Archive already exists", "The archive '%s' already exists." % archive[:-4])
                return 1
        self.save_obj([], self.archive_current.get())
        self.archive_list.append('end', self.archive_current.get())
        self.archive_list.activate('end')
        self.archive_list_clicked(0)

    def add_text_to_archive(self):
        self.update_archive_list()
        if self.archive_current.get() == '':
            tkMessageBox.showwarning("No archive selected", "Please select an archive.")
            return 1
        pickle_file_exists = False
        for archive in self.archive_list.get(0, 'end'):
            if archive == self.archive_current.get():
                pickle_file_exists = True
        if pickle_file_exists == False:
            tkMessageBox.showwarning("No archive named '%s'" % self.archive_current.get(), "There is currently no archive named '%s'." % self.archive_current.get())
            return 1
        new_list_of_dicts = markov.read_text(self.input_text.get(1.0, "end-1c"))
        old_list_of_dicts = self.load_obj(self.archive_current.get())
        should_add = True
        for curr_old_dict in old_list_of_dicts:
            for curr_new_dict in new_list_of_dicts:
                if curr_old_dict['Preceding Word'] == curr_new_dict['Preceding Word']:
                    should_add = False
                    for old_word in curr_old_dict:
                        if curr_new_dict.has_key(old_word) and old_word != 'Preceding Word':
                            curr_new_dict[old_word] += curr_old_dict[old_word]
                        else:
                            curr_new_dict[old_word] = curr_old_dict[old_word]
            if should_add:
                new_list_of_dicts.append(curr_old_dict)
            should_add = True
        self.save_obj(new_list_of_dicts, self.archive_current.get())
        self.input_text.delete('1.0', 'end')


if __name__ == "__main__":
    root = tk.Tk()
    window = MarkovChainWindow(root)
    root.mainloop()
