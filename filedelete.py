from tkinter import *
from tkinter.filedialog import askdirectory
from tkinter.messagebox import showerror
import tkinter.ttk as ttk
import os, csv
import time, datetime, calendar

LARGE_FONT = ("Verdana", 12)
NORM_FONT = ("Verdana", 10)
SMALL_FONT = ("Verdana", 9)

def path_shorten(path):
    path = path.split('/')
    if len(path) <= 4:
        return os.sep.join(path)
    else:
        return os.sep.join(path[:2]+['...']+path[-2:])

def open_file(selection,file_path_list):
    os.startfile(file_path_list[selection-1])

def msgbox(msg, dryrun_list=0, file_name_len=0, file_path_len = 0):
    mb = Tk()
    if isinstance(dryrun_list, list):
        mb.wm_title("Notice")
        label = ttk.Label(mb, text=msg, font=NORM_FONT)
        label.pack(side=TOP, fill=BOTH)
        scrollbar = Scrollbar(mb)
        scrollbar.pack(side=RIGHT, fill=Y)
        listbox = Listbox(mb, yscrollcommand=scrollbar.set, height=30, width=120, font='TkFixedFont')
        listbox.insert(END, 'File name'.ljust(file_path_len + 2) + 'Date Created') # plus 2 for column spacing
        listbox.itemconfig(0, {'bg': 'lightblue'})
        file_path_list = []
        for i in dryrun_list:
            manip_path = path_shorten(str(i[2]))
            justify = file_path_len

            listbox.insert(END, manip_path.ljust(justify+2) + str(i[1]) )
            file_path_list.append(i[2])
        listbox.pack(side=TOP, fill=BOTH)
        scrollbar.config(command=listbox.yview)
        listbox.bind('<Double-1>', lambda x: open_file(listbox.curselection()[0],file_path_list))

    else:
        mb.wm_title("Warning!")
        label = ttk.Label(mb, text=msg, font=NORM_FONT)
        label.pack(side=TOP, fill=BOTH)

    button = ttk.Button(mb, text="Okay", command=mb.destroy)
    button.pack(side=BOTTOM, fill=BOTH)
    mb.mainloop()


def walk_dir(main_obj, path, daydif, filetype):
    current_time = datetime.datetime.now().strftime("%m_%d_%y")
    dryrun_list = []
    file_name_len = 0
    file_path_len = 0
    if os.path.isdir(path) and os.path.exists(path):
        file_cnt = 0
        # this is for counting for prog bar increment
        for dirpath, dirnames, filenames in os.walk(path):
            for file in filenames:
                full_file_path = os.path.join(dirpath, file).replace("\\","/")
                seconds_dif = calendar.timegm(time.gmtime()) - os.path.getmtime(full_file_path)
                days, seconds = divmod(seconds_dif, 24 * 60 * 60)
                if int(days) >= daydif:
                    if file.endswith("." + filetype):
                        file_cnt += 1
        if file_cnt == 0:
            msgbox('No files found meeting the selected conditions. There may be empty directories but they cannot be deleted indepedent of deleting files')
            return False

        with open(path + '/Files removed ' + current_time + '.csv', 'w', newline='') as output:
            csv_output = csv.writer(output, delimiter=',')
            csv_output.writerows([['File Name', 'Removed From']])
            # this is for deleting
            for dirpath, dirnames, filenames in os.walk(path):
                for file in filenames:

                    full_file_path = os.path.join(dirpath, file).replace("\\","/")
                    time_created = time.ctime(os.path.getmtime(full_file_path))

                    seconds_dif = calendar.timegm(time.gmtime()) - os.path.getmtime(full_file_path)
                    days, seconds = divmod(seconds_dif, 24 * 60 * 60)

                    if int(days) >= daydif:
                        if file.endswith("." + filetype):
                            main_obj.progbar.step((1 / file_cnt) * 100)
                            main_obj.progbar.update()

                            if main_obj.checkvar.get() == '0':
                                #dry run not selected
                                os.remove(os.path.join(dirpath, file))
                                csv_output.writerows([[file,dirpath]])
                            else:
                                #dry run selected')
                                if len(file) > file_name_len:
                                    file_name_len = len(file)
                                if len(path_shorten(full_file_path)) > file_path_len:
                                    file_path_len = len(path_shorten(full_file_path))
                                dryrun_list.append([file, time_created, full_file_path])



            if dryrun_list != []:
                msgbox('If you run with the current settings these are the files you will delete.', dryrun_list,
                       file_name_len,file_path_len)
                dryrun_list = []
                return

            if main_obj.empdir_var.get() == '0':  # rmdir checkbox
                print('remove dir not selected')
                msgbox('Processing complete!')
                return
            else:
                for dirpath, n, f in os.walk(path, topdown=False):
                    try:
                        os.rmdir(dirpath)
                    except OSError as ex:
                        print("Directory not empty.")
                msgbox('Processing complete!')
                return
            return # close csv????
    elif path == 'Click Browse to add folder':
        msgbox('Select a directory to run the script on.')
    else:
        msgbox("'" + path + "'" + ' does not exist or is not a valid path')
    file_cnt = 0



class MainFrame:
    def __init__(self, master):
        master.title('Dated File Removal Tool')
        # TOP FRAME
        self.topframe = ttk.Frame()
        self.topframe.grid(row=0, column=0, padx=10, pady=2, sticky='W')
        # browse button
        self.browseButton = Button(self.topframe, text="Browse", command=self.load_dir, width=15).grid(row=0, column=0)
        # okbutton test
        button = Button(self.topframe, text="Execute", command=self.ok_click, width=15)
        button.grid(row=0, column=1, sticky='E')

        # MIDDLE FRAME
        self.middleFrame = ttk.Frame()
        self.middleFrame.grid(row=1, column=0, sticky='W', padx=10, pady=5)
        # path display box
        self.dir_path = StringVar()
        browse_entry = Entry(self.middleFrame, width=65, textvariable=self.dir_path, state=DISABLED)
        browse_entry.grid(row=0, column=0)
        self.dir_path.set("Click Browse to add folder")


        # label frame
        self.options_lf = ttk.Labelframe(self.middleFrame, text='Options')
        # days combobox
        days = ('00 days', '30 Days', '60 Days', '90 Days')
        self.days_cmb = ttk.Combobox(self.options_lf, values=days, state='readonly')
        self.days_cmb.current(0)  # set selection
        self.days_cmb.grid(row=0, column=0, padx=25)
        # file types combobox
        filetypes = ('jpg', 'mp3', 'avi')
        self.file_cmb = ttk.Combobox(self.options_lf, values=filetypes, state='readonly')
        self.file_cmb.current(0)  # set selection
        self.file_cmb.grid(row=0, column=1, padx=25, pady=2)
        # test run checkbox
        self.checkvar = StringVar()
        dryrun_cb = Checkbutton(self.options_lf, text="Test Run", variable=self.checkvar)
        dryrun_cb.grid(row=1, column=0, sticky='W', padx=25)
        self.checkvar.set(1)
        # Remove dirs checkbox
        self.empdir_var = StringVar()
        empdir_cb = Checkbutton(self.options_lf, text="Remove Empty Dirs", variable=self.empdir_var)
        empdir_cb.grid(row=1, column=1, sticky='W', padx=25)
        self.empdir_var.set(0)
        # place in frame
        self.options_lf.grid(row=1, column=0, sticky='W')

        # BOTTOM FRAME
        self.bottomframe = ttk.Frame()
        self.bottomframe.grid(row=3, column=0)
        # prog bar
        self.progbar = ttk.Progressbar(self.bottomframe, orient='horizontal', mode='determinate', length=420)
        self.progbar.grid(row=1, column=0)

    def load_dir(self):
        dirname = askdirectory()
        if not dirname:
            pass  # file upload cancelled
        self.dir_path.set(dirname)

    def ok_click(self):
        daydif = int(self.days_cmb.get()[:2])
        walk_dir(self, self.dir_path.get(), daydif, self.file_cmb.get())


if __name__ == "__main__":
    root = Tk()
    b = MainFrame(root)
    root.resizable(width=FALSE, height=FALSE)
    root.mainloop()
