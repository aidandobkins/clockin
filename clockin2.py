from tkinter import *
import sqlite3
import time
import os.path

def forgotClock():
    forgotWindow = Toplevel()
    forgotWindow.geometry("400x200")
    forgotWindow.configure(bg = '#e5edf5')

    Label(forgotWindow, text = "It seems that the you clocked in last, but it was on a different day\nPlease contact your timekeeper and let them know you may have forgotten to clock out.", bg = '#e5edf5', pady = 15, wrap = 350).pack()
    Label(forgotWindow, text = "Your clock has been registered as a clock in,\nplease notify your timekeeper if this is a mistake and you are currently clocking out", bg = '#e5edf5', pady = 15, wrap = 350).pack()


def popUpConfirm(inout, curr_time, curr_date):
    popUp = Toplevel()
    popUp.geometry("200x100")
    popUp.configure(bg = '#e5edf5')

    Label(popUp, text = "You have been clocked " + inout + "\nat " + curr_time + " " + curr_date + "\n\nThis window will close \nin 30 seconds...", bg = '#e5edf5', pady = 15).pack()

    popUp.after(30000, lambda: popUp.destroy()) #closes window after 30 seconds

def login():
    conn = sqlite3.connect('logins/user_information.db')
    c = conn.cursor()   

    records = c.execute("SELECT * FROM user_info").fetchall()

    found = False
    inout = "N/A"

    for row in records: #tests if the login info is in the database
        if row[0] == username.get():
            if row[1] == password.get():
                found = True
                userdb = "timesheets/" + row[3] + row[2] + ".db"
                usertxtfile = "inout/" + row[3] + row[2] + ".txt"
                loginCalc(userdb, usertxtfile, inout)
                break
    
    if not(found): #makes the labels not stack up
        if notFound.winfo_ismapped():
            notFound.pack_forget()
        notFound.pack()
        
    conn.commit()
    conn.close()

    #database to put in clock time

def loginCalc(userdb, usertxtfile, inout):

    conn = sqlite3.connect(userdb)
    c = conn.cursor()    

    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='clock_times' ''')
    if c.fetchone()[0] == 0 : 
        c.execute("""CREATE TABLE clock_times
        (
            clocked_in TEXT,
            clocked_out TEXT,
            date TEXT,
            raw_in TEXT,
            raw_out TEXT
        )   
        """)

    if not(os.path.isfile(usertxtfile)):
        f = open(usertxtfile, "w")
        f.write("OUT")
        f.close()

    f = open(usertxtfile, "r")
    lastClock = f.readline()
    f.close()

    t = time.localtime()
    curr_time = time.strftime("%H:%M", t)
    curr_date = time.strftime("%m/%d/%Y", t)

    rawtime = curr_time

    formtimestr = curr_time[3] + curr_time[4]
    formtime = int(formtimestr)

    if formtime >= 53 and formtime <= 7:
        curr_time = curr_time[0] + curr_time[1] + ":00"

    if formtime >= 8 and formtime <= 22:
        curr_time = curr_time[0] + curr_time[1] + ":15"

    if formtime >= 23 and formtime <= 37:
        curr_time = curr_time[0] + curr_time[1] + ":30"

    if formtime >= 38 and formtime <= 52:
        curr_time = curr_time[0] + curr_time[1] + ":45"

    if lastClock == "IN": #if they are clocking OUT

        #function for detecting if its been longer than 12 hours since last clockin
        #if it has, make new window, inform user they may have forgotten to clock out,
        #reset the text file to have last clock be "out" then tell them to contact
        #their boss that they forgot to clock out, and mark their clock as an "in"
        #in a new row

        records1 = c.execute("SELECT count(*) FROM clock_times").fetchone()
        records2 = records1[0] #gets the amount of entries

        lastrecord = c.execute("SELECT date FROM clock_times").fetchall()

        for row in range(records2): #gets last clocked in time
            clockDate = lastrecord[row]

        clockDate = clockDate[0]

        if clockDate == curr_date:
            diffDate = False
        else:
            diffDate = True

        if diffDate:
            forgotClock()

            c.execute("INSERT INTO clock_times (clocked_in, date, raw_in) VALUES (:curr_time, :curr_date, :rawtime)",
            {
                'curr_time': curr_time,
                'curr_date': curr_date,
                'rawtime': rawtime
            }
                 )
            f = open(usertxtfile, "w")
            f.write("IN")
            inout = "in"

        elif diffDate == False:
            c.execute("UPDATE clock_times SET clocked_out = (:curr_time) WHERE rowid = (:records2)",
            {
                'curr_time': curr_time,
                'records2': records2
            }
                 )

            c.execute("UPDATE clock_times SET raw_out = (:rawtime) WHERE rowid = (:records2)",
            {
                'rawtime': rawtime,
                'records2': records2
            }
                 )

            f = open(usertxtfile, "w")
            f.write("OUT")
            inout = "out"
        
        #sets inout to in

        
        

    if lastClock == "OUT": #if they are clocking IN

        inout = "in"

        c.execute("INSERT INTO clock_times (clocked_in, date, raw_in) VALUES (:curr_time, :curr_date, :rawtime)",
        {
            'curr_time': curr_time,
            'curr_date': curr_date,
            'rawtime': rawtime
        }
                )

        f = open(usertxtfile, "w")
        f.write("IN")

    f.close()

    username.delete(0, END)
    password.delete(0, END)

    conn.commit()
    conn.close()

    popUpConfirm(inout, curr_time, curr_date)

    
def regUser():
    conn = sqlite3.connect('logins/user_information.db')
    c = conn.cursor()

    #checking if table exists, if not, create it
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='user_info' ''')
    if c.fetchone()[0] == 0 : 
        c.execute("""CREATE TABLE user_info
        (
            username text,
            password text,
            first_name text,
            last_name text
        )   
        """)



    c.execute("INSERT INTO user_info VALUES (:newName, :newPass, :newFirst, :newLast)",
    {
        'newName': newName.get(),
        'newPass': newPass.get(),
        'newFirst': newFirst.get(),
        'newLast': newLast.get()
    }
            )

    conn.commit()
    conn.close()

    newName.delete(0, END)
    newPass.delete(0, END)
    newFirst.delete(0, END)
    newLast.delete(0, END)

def register():
    regWindow = Toplevel()
    regWindow.geometry("350x400")
    regWindow.configure(bg = '#e5edf5')

    Label(regWindow, text = "Enter your desired information below", bg = '#e5edf5', fg = '#17aaff', font = 'Arial 11 bold', pady = '5').pack()
    Label(regWindow, bg = '#e5edf5').pack() #spacer

    global newName, newPass, newFirst, newLast

    Label(regWindow, text = "Username", bg = '#e5edf5', fg = '#17aaff', font = 'Arial 11 bold', pady = '5').pack()
    newName = Entry(regWindow, font = '12')
    newName.pack()
    Label(regWindow, text = "Password", bg = '#e5edf5', fg = '#17aaff', font = 'Arial 11 bold', pady = '5').pack()
    newPass = Entry(regWindow, font = '12')
    newPass.pack()
    Label(regWindow, text = "First Name", bg = '#e5edf5', fg = '#17aaff', font = 'Arial 11 bold', pady = '5').pack()
    newFirst = Entry(regWindow, font = '12')
    newFirst.pack()
    Label(regWindow, text = "Last Name", bg = '#e5edf5', fg = '#17aaff', font = 'Arial 11 bold', pady = '5').pack()
    newLast = Entry(regWindow, font = '12')
    newLast.pack()
    Label(regWindow, bg = '#e5edf5').pack() #spacer

    regButton = Button(regWindow, command = regUser, borderwidth = 0, pady = 30)
    regButton.config(image = registerpic)
    regButton.pack()

    Label(regWindow, bg = '#e5edf5').pack() #spacer

#root window 

root = Tk()
root.title("Clock In System")
root.geometry("350x350")
root.configure(bg = '#e5edf5')
root.iconbitmap('imgs/hchh.ico')

newName = StringVar() #declaring in global scope
newPass = StringVar()
newFirst = StringVar()
newLast = StringVar()

Label(root, bg = '#e5edf5').pack() #spacer
Label(root, text = "Username", bg = '#e5edf5', fg = '#17aaff', font = 'Arial 11 bold', pady = '5').pack()
username = Entry(root, font = '12', bg = 'white')
username.pack()
Label(root, text = "Password", bg = '#e5edf5', fg = '#17aaff', font = 'Arial 11 bold', pady = '5').pack()
password = Entry(root, font = '12', bg = 'white', show = '*')
password.pack()
Label(root, bg = '#e5edf5').pack() #spacer
Label(root, bg = '#e5edf5').pack() #spacer

registerpic = PhotoImage(file = "imgs/registerbutton.png")
clockpic = PhotoImage(file = "imgs/clockbutton.png")
regpic = PhotoImage(file = "imgs/regbutton.png")

clockButton = Button(root, command = login, borderwidth = 0)
clockButton.config(image = clockpic)
clockButton.pack()
Label(root, bg = '#e5edf5').pack() #spacer
newButton = Button(root, text = "New Employee", command = register, borderwidth = 0)
newButton.config(image = regpic)
newButton.pack()

notFound = Label(root, text = "Incorrect Username or Password, please try again.", fg = "red")

root.mainloop()
