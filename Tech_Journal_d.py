import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkcalendar import Calendar, DateEntry
from babel.dates import format_date, parse_date, get_day_names, get_month_names
from babel.numbers import *  # Additional Import

import tkinter.messagebox
import service_db_connect

import sqlite3

###################### Main Window ############################################
###############################################################################
window1 = tk.Tk()

window1.title("Service Ticket")
WIDTH=1024
HEIGHT=900
# center the form to the user's screen
sc_width = window1.winfo_screenwidth()
sc_height = window1.winfo_screenheight()
x_coordinate = (sc_width/2)-(WIDTH/2)
y_coordinate = (sc_height/2)-(HEIGHT/2)        
window1.geometry("%dx%d+%d+%d"%(WIDTH, HEIGHT, x_coordinate, y_coordinate))

frame1 = tk.Frame(window1, bd=10, relief='ridge')

global start_rec_id
global inv_rec_id


   
##################### Main Window Frames #####################################
##############################################################################
 
frame1.place(relwidth=1, relheight=1)

frame1a = tk.Frame(frame1)   # Date, TR and WO/PO Labels
frame1a.place(relx=0.5, relwidth=1, relheight=0.435, anchor='n')

frame1b = tk.Frame(frame1)   # Buttons
frame1b['relief'] = tk.RIDGE
frame1b.place(relx=0.5, rely=0.53, relwidth=0.95, relheight=0.075, anchor='n')

frame1c = tk.Frame(frame1)   # DataGrid
frame1c['relief'] = tk.RIDGE
frame1c.place(relx=0.5, rely=0.62, relwidth=0.95, relheight=0.21, anchor='n')

frame1d = tk.Frame(frame1)   # History/Search Label and Buttons
frame1d.place(relx=0.5, rely=0.827, relwidth=1, relheight=0.17, anchor='n')

####################Main Window Functions ###################################
#############################################################################

##------------Main Window Function Fill the Treeview/Data Grid-----------
def DisplayData():
    conn = sqlite3.connect("service.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM ticket")
    data=[]
    tree1.delete(*tree1.get_children())
    for row in cur.fetchall():
        data.append(tree1.insert('', 0, values=row))
    conn.close()
    
    # this hilites the last entry but does not set the focus
    #child_id = tree1.get_children()[-1]
    #tree1.selection_set(child_id)
    #tree1.focus(child_id)
    
    return

##------------Main Window Function Save New Record to Database and add to Treeview-----------
def SaveRec():
    ##### verify that the essential text boxes are not empty
    cnt = 0
    var1 = date_svar.get()
    var2 = tr_svar.get()
    var4 = cust_svar.get()
    var5 = addr_svar.get()
    var6 = issue_svar.get()
    var7 = notes_txt.get(1.0, 'end-1c')
    
    if var1 == '':
        cnt = cnt+1
    if var2 == '':
        cnt = cnt+1
    if var4 == '':
        cnt = cnt+1
    if var5 == '':
        cnt = cnt+1
    if var6 == '':
        cnt = cnt+1
    if var7 == '':
        cnt = cnt+1
    if cnt > 0:
        tkinter.messagebox.showwarning('', "All fields with asterisks must have data entered.")
    else:
        conn = sqlite3.connect("service.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO ticket VALUES(NULL,?,?,?,?,?,?,?)", (
            cal_txt.get(), tr_txt.get(), wo_txt.get(), cust_cbo.get(), addr_cbo.get(),
            issue_txt.get(), notes_txt.get('1.0', tk.END)))
        conn.commit()
        conn.close()
        Reset()
        cal_txt.focus()
                  
        DisplayData()
        fill_custbox()
        
        response = tkinter.messagebox.askyesno("Check for Parts Used", "Did You Use Any Inventory ?")
        if response == 1:
            PartsChildWindow()
        
            
        
##------------Main Window Function Remove Text from all input boxes-----------
def Reset():
     
    cal_txt.delete(0, tk.END)
    tr_txt.delete(0, tk.END)
    wo_txt.delete(0, tk.END)
    cust_cbo.delete(0, tk.END)
    addr_cbo.delete(0, tk.END)
    addr_cbo['values'] = ""
    
   
    issue_txt.delete(0, tk.END)
    notes_txt.delete("1.0", tk.END)

##------------Main Window Function Delete Record from Database and Treeview-----------
def DeleteRec():
    
    try:
        selected_item = tree1.selection()[0] ## get selected item from treeview        
        tree1.delete(selected_item) 
        conn = sqlite3.connect("service.db")
        cur = conn.cursor()
        cur.execute("DELETE FROM ticket WHERE id=?", (start_rec_id,))            
        conn.commit()            
        conn.close()
        DisplayData()            
        Reset()        
    except IndexError:
        tkinter.messagebox.showwarning('', "There is no record selected to delete.")       
    return

##------------Main Window Function Exit the App-----------
def CloseApp():
    if tkinter.messagebox.askyesno("Service Ticket", "Confirm that you want to Exit"):   
        window1.destroy()
    
##------------Main Window Function when treeview item is selected all of the information------- 
##------------is entered back into the textboxes of main window and the Update window which----
##------------then opens to allow for modification of the record in the database and-----------
##------------the treeview---------------------------------------------------------------------
def RecSelected(ev):

    Reset()
    viewInfo = tree1.focus()
    selected_data = tree1.item(viewInfo)
    row = selected_data['values']
        
    cal_txt.delete(0, tk.END)      # this is a tkcalender DateEntry Box and it doesn't use the set method
    cal_txt.insert(0, row[1])      # but it does use some of the same methods as a standard Entry box             
    tr_txt.insert(0, row[2])            
    wo_txt.insert(0, row[3])
    cust_cbo.insert(0, row[4])
    addr_cbo.insert(0, row[5])
   
    issue_txt.insert(0, row[6])           
    notes_txt.insert(tk.END, (row[7]))   # this is a multi line Text box and it doesn't use the set method
    global start_rec_id
    start_rec_id = format(row[0])        # must be formatted to a string so the update function can use it
    
    UpdateChildWindow()      # opens the Update window
    return

##------------Main Window Function pulls each of the customer names from the database and-------
##------------enters them into the dropdown with no duplication---------------------------------
def fill_custbox(*args):
    
    conn = sqlite3.connect("service.db")
    cur = conn.cursor()            
    cur.execute("SELECT DISTINCT cust FROM ticket Order BY cust")
    data = []
    for row in cur.fetchall():
        data.append(row[0])
    cust_cbo['values'] = data                
    conn.close()
    

##------------Main Window Function when a selection is made in the customer dropdown all the addresses-------    
##------------for that customer are pulled from the database and added to the address dropdown---------------
##------------which is required for the history search-------------------------------------------------------
def fill_addrbox(*args):      
    conn = sqlite3.connect("service.db")
    cur = conn.cursor()       
    cur.execute("SELECT distinct addr FROM ticket WHERE cust = '%s' Order by addr" % (cust_cbo.get(),))
    data = []
    for row in cur.fetchall():
        data.append(row[0])
    addr_cbo['values'] = data
    conn.close()
    

##------------Main Window/Update Window Function when the update window is either saved or closed any information---
##------------changes/or not are transferred back to main window and the treeview-----------------------------------
def RefillWindow1(update_var1, update_var2, update_var3, update_var4,
                  update_var5, update_var6, update_var7):
    Reset()
    
    cal_txt.delete(0, tk.END)
    cal_txt.insert('', update_var1)
    tr_txt.insert(tk.END, update_var2) 
    wo_txt.insert(tk.END, update_var3) 
    cust_cbo.insert(tk.END, update_var4) 
    addr_cbo.insert(tk.END, update_var5)
    
    issue_txt.insert(tk.END, update_var6)
    notes_txt.delete('1.0', tk.END)
    notes_txt.insert(tk.END, update_var7)  
    return

##------------Main Window Function if an address has been selected from the drop down or-------
##------------typed into the drop down, all the records with that address will be pulled-------
##------------from the database and the treeview will be cleared and then refilled with--------
##------------with the pulled data-------------------------------------------------------------
def DisplayHistory():
    cnt = 0
    var1 = addr_svar.get()
    if var1 == '':
        cnt = cnt+1
    if cnt > 0:
        tkinter.messagebox.showwarning('', "Address field must have data entered.")
    else:
        conn = sqlite3.connect("service.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM ticket WHERE addr = '%s'" % (addr_cbo.get()))
        data=[]
        tree1.delete(*tree1.get_children())
        for row in cur.fetchall():
            data.append(tree1.insert('', tk.END, values=row))
        conn.close()

##------------Main Window Function when finished searching the history all records will be-------    
##------------restored to the treeview-----------------------------------------------------------
def EndHistory():
    tree1.delete(*tree1.get_children())
    DisplayData()

##------------Main Window Function search for strings or parts of strings in the 3 fields outlined-------
##------------and show only records with those strings---------------------------------------------------
def SrchTicket():
    if SEARCH.get() != "":
        tree1.delete(*tree1.get_children())
        conn = sqlite3.connect("service.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM `ticket` WHERE `tr` LIKE ? OR `issue` LIKE ? OR `notes` LIKE ?", ('%'+str(SEARCH.get())+'%', '%'+str(SEARCH.get())+'%', '%'+str(SEARCH.get())+'%'))
        fetch = cursor.fetchall()
        for data in fetch:
            tree1.insert('', 'end', values=(data))
        cursor.close()
        conn.close()  

##------------Main Window Function clear the search textbox and the treeview and restore all records-----
##------------to the treeview----------------------------------------------------------------------------
def EndSrch():
    tree1.delete(*tree1.get_children())
    srch_txt.delete(0, tk.END)
    DisplayData()
    
##------------Main Window Labels---------------------------------------------------
##---------------------------------------------------------------------------------
date_lbl = tk.Label(frame1, text="Date: *", anchor="w", font=40)
date_lbl.place(relx=0.023, rely=0.01, relwidth=0.1, relheight=0.03)
tr_lbl = tk.Label(frame1, text="Tracking  #: *", anchor="w", font=40)
tr_lbl.place(relx=0.23, rely=0.01, relwidth=0.3, relheight=0.03)
wo_lbl = tk.Label(frame1, text="WO/PO: ", font=40, anchor="w")
wo_lbl.place(relx=0.62, rely=0.01, relwidth=0.355, relheight=0.03)
    
cust_lbl = tk.Label(frame1, text="Customer: *", font=40, anchor="w")
cust_lbl.place(relx=0.023, rely=0.075, relwidth=0.425, relheight=0.04)
addr_lbl = tk.Label(frame1, text="Address: *", font=40, anchor="w")
addr_lbl.place(relx=0.5, rely=0.075, relwidth=0.475, relheight=0.04)
        
issue_lbl = tk.Label(frame1, text="Issue: *", font=40, anchor="w")
issue_lbl.place(relx=0.023, rely=0.15, relwidth=0.95, relheight=0.04)
    
notes_lbl = tk.Label(frame1, text="Notes / Parts Used / Parts Ordered: *", font=40)
notes_lbl.place(rely=0.225, relwidth=1, relheight=0.04)
    
hist_lbl = tk.Label(frame1d, text="Get the History of the selected Address ", font=40, anchor="w")
hist_lbl.place(relx=0.023, rely=0.2, relwidth=0.4, relheight=0.15)
    
srch_lbl = tk.Label(frame1d, text="Search the fields (TR#, Issue and Notes) ", font=40, anchor="w")
srch_lbl.place(relx=0.023, rely=0.55,relwidth=0.4, relheight=0.15)

copyright_lbl = tk.Label(frame1d, text="June 2021 Created by Paul Higginbotham as Free to Use Software")
copyright_lbl.place(rely=0.85,relwidth=1, relheight=0.15)
    
##------------Main Window Entryboxes | ComboBoxes | Scrolled Textboxes-------------
##---------------------------------------------------------------------------------
date_svar = tk.StringVar()
tr_svar = tk.StringVar()
wo_svar = tk.StringVar()
cust_svar = tk.StringVar()
addr_svar = tk.StringVar()
    
issue_svar = tk.StringVar()
notes_svar = tk.StringVar()
    
SEARCH = tk.StringVar()
    
cal_txt = DateEntry(frame1, font=40, year=2021, textvariable=date_svar)
cal_txt.place(relx=0.023, rely=0.04, relwidth=0.1, relheight=0.03)
    
tr_txt = tk.Entry(frame1, font=40, textvariable=tr_svar)
tr_txt.place(relx=0.23, rely=0.04, relwidth=0.3, relheight=0.03)
    
wo_txt = tk.Entry(frame1, font=40, textvariable=wo_svar)
wo_txt.place(relx=0.62, rely=0.04, relwidth=0.355, relheight=0.03)
    
cust_cbo = ttk.Combobox(frame1, font=40, textvariable=cust_svar)
cust_cbo.place(relx=0.023, rely=0.115, relwidth=0.425, relheight=0.04)
    
addr_cbo = ttk.Combobox(frame1, font=40, textvariable=addr_svar)
addr_cbo.place(relx=0.5, rely=0.115, relwidth=0.475, relheight=0.04)
    
fill_custbox()
cust_cbo.bind('<<ComboboxSelected>>', fill_addrbox)
        
issue_txt = tk.Entry(frame1, font=40, textvariable=issue_svar)
issue_txt.place(relx=0.025, rely=0.185, relwidth=0.95, relheight=0.04)
    
notes_txt = scrolledtext.ScrolledText(frame1, wrap='word', font=40)
notes_txt.place(relx=0.025, rely=0.27, relwidth=0.95, relheight=0.28)
    
srch_txt = tk.Entry(frame1d, font=40, textvariable=SEARCH)
srch_txt.place(relx=0.425, rely=0.5, relwidth=0.3, relheight=0.25)
    
##------------Main Window Buttons--------------------------------------------------
##---------------------------------------------------------------------------------
save_btn = tk.Button(frame1b, text="SAVE", font=40, bd=2, command=lambda: SaveRec())
save_btn.place(relx=0.03, rely=0.45, relwidth=0.1, relheight=0.55)
reset_btn = tk.Button(frame1b, text="CLEAR", font=40, bd=2,command=lambda: Reset())
reset_btn.place(relx=0.25, rely=0.45, relwidth=0.1, relheight=0.55) 
delete_btn = tk.Button(frame1b, text="DELETE", font=40, bd=2, command=lambda: DeleteRec())
delete_btn.place(relx=0.36, rely=0.45, relwidth=0.1, relheight=0.55)
exit_btn = tk.Button(frame1b, text="EXIT", font=40, bd=2, command=lambda: CloseApp())
exit_btn.place(relx=0.47, rely=0.45, relwidth=0.1, relheight=0.55)
info_btn = tk.Button(frame1b, text="Info ", font=40,command=lambda: InfoWindow())
info_btn.place(relx=0.73, rely=0.45, relwidth=0.1, relheight=0.55) 
parts_btn = tk.Button(frame1b, text="Inventory ", font=40, command=lambda: PartsChildWindow())
parts_btn.place(relx=0.84, rely=0.45, relwidth=0.1, relheight=0.55)
    
hist_btn = tk.Button(frame1d, text="GET HISTORY", font=40, bd=2, command=lambda: DisplayHistory())
hist_btn.place(relx=0.685, rely=0.155, relwidth=0.16, relheight=0.25)
hist_done_btn = tk.Button(frame1d, text="CLEAR", font=40, bd=2, command=lambda: EndHistory())
hist_done_btn.place(relx=0.865, rely=0.155, relwidth=0.1, relheight=0.25)
    
srch_btn = tk.Button(frame1d, text="SEARCH", font=40, bd=2, command=lambda: SrchTicket())
srch_btn.place(relx=0.745, rely=0.5, relwidth=0.1, relheight=0.25)
srch_done_btn = tk.Button(frame1d, text="CLEAR", font=40, bd=2, command=lambda: EndSrch())
srch_done_btn.place(relx=0.865, rely=0.5, relwidth=0.1, relheight=0.25) 
    
##------------Main Window TreeView-------------------------------------------------
##---------------------------------------------------------------------------------
scroll_y = ttk.Scrollbar(frame1c, orient=tk.VERTICAL)
    
tree1 = ttk.Treeview(frame1c, yscrollcommand=scroll_y.set)
tree1.configure(columns=("ID","Date", "TR", "WO", "Cust", "Addr", "Issue", "Notes"))
scroll_y.configure(command= tree1.yview)
tree1.configure(yscrollcommand=scroll_y.set, selectmode="browse")
    
scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
    
tree1.heading("ID", text="ID", anchor=tk.W)
tree1.heading("Date", text="Date", anchor=tk.W)
tree1.heading("TR", text="TR #", anchor=tk.W)
tree1.heading("WO", text="WO/PO #", anchor=tk.W)
tree1.heading("Cust", text="Cust", anchor=tk.W) 
tree1.heading("Addr", text="Addr", anchor=tk.W) 
    
tree1.heading("Issue", text="Issue", anchor=tk.W) 
tree1.heading("Notes", text="Notes", anchor=tk.W)
    
tree1['show'] = 'headings'
    
tree1.column("ID", width=30)
tree1.column("Date", width=50)
tree1.column("TR", width=50)
tree1.column("WO", width=50)
tree1.column("Cust", width=70)
tree1.column("Addr", width=150)
    
tree1.column("Issue", width=100)
tree1.column("Notes", width=200)        
    
tree1.pack(fill=tk.BOTH, expand=1)
tree1.bind("<ButtonRelease-1>", RecSelected)


        
def PartsChildWindow():
    #######################Child Window 'Inventory'#########################################
    ########################################################################################
    InvChild = tk.Toplevel(window1) # Child window
    # InvChild.iconbitmap('word_pen.ico')
    InvChild.title("Inventory")
    
    # centers the Inventory window to users screen
    WIDTH=1200
    HEIGHT=500
    sc_width = InvChild.winfo_screenwidth()
    sc_height = InvChild.winfo_screenheight()
    x_coordinate = (sc_width/2)-(WIDTH/2)
    y_coordinate = (sc_height/2)-(HEIGHT/2)        
    InvChild.geometry("%dx%d+%d+%d"%(WIDTH, HEIGHT, x_coordinate, y_coordinate))
    
    # was used to outline the frames(, highlightbackground='sky blue', highlightcolor='sky blue', highlightthickness=2)
    # and the textboxes during development
    frame1 = tk.Frame(InvChild)
    frame1.place(relwidth=1, relheight=1)
    
    frame3a = tk.Frame(frame1, bd=10, highlightbackground='sky blue', highlightcolor='sky blue', highlightthickness=2) 
    frame3a.place(relx=0.01, rely=0.01, relwidth=0.99, relheight=0.99)
    frame3b = tk.Frame(frame1, highlightbackground='sky blue', highlightcolor='sky blue', highlightthickness=2)
    frame3b.place(relx=0.5, rely=0.05, relwidth=0.725, relheight=0.45, anchor='n')
    frame3c = tk.Frame(frame1, highlightbackground='sky blue', highlightcolor='sky blue', highlightthickness=2)
    frame3c.place(relx=0.498, rely=0.7, relwidth=0.925, relheight=0.1, anchor='n')   
    
    global inv_rec_id
    
    ##------------Inventory Window Function-----------
    def SaveInvRec():
        var1 = str_pn.get() # textvariables assigned to the Entry boxes
        var2 = str_desc.get()
        var3 = str_qty.get()
    
        cntr = 0
        
        if var1 == '':  # checking for empty text boxes
            cntr = cntr+1
        if var2 == '':
            cntr = cntr+1
        if var3 == '':
            cntr = cntr+1
        if cntr > 0:
            # to keep the child window on top when an error occurs use the 'parent=??'
            tkinter.messagebox.showwarning('', "There must be a part number, description and quantity entered.", parent=InvChild)
        
        if cntr == 0:
            conn = sqlite3.connect("service.db")
            cur = conn.cursor()
            cur.execute("INSERT INTO inventory VALUES(NULL,?,?,?,?)", (site_txt_inv.get(), pn_txt_inv.get(), desc_txt_inv.get(), qty_txt_inv.get()))
            conn.commit()
            DisplayInvData()
            conn.close()
            ResetInv()                    
        
        
    ##------------Inventory Window Function fill treeview with all the records pulled from the database-----------
    def DisplayInvData():
        conn = sqlite3.connect("service.db")
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT * FROM inventory ORDER BY part")
        data = []
        tree2.delete(*tree2.get_children())
        for row in cur.fetchall():             
            #data.append(tree2.insert('', tk.END, values=row)) # this populates the tree in ascending order
            data.append(tree2.insert('', 0, values=row)) # populates tree in decending order
            #tree2.see(data[-1])  # this automatically sends the scrollbar to the last record and it works
        conn.commit()
        conn.close()
        
        FillInvSiteid()
        return
    
    ##------------Inventory Window Function this keeps the site id textbox populated once a-----------
    ##------------site id has been entered------------------------------------------------------------
    def FillInvSiteid():
        conn = sqlite3.connect("service.db")
        cur = conn.cursor()            
        cur.execute("SELECT DISTINCT site FROM inventory")
        data = []
        for row in cur.fetchall():
            data.append(row[0])
            site_txt_inv.insert(tk.END, row[0])
    
        conn.close()  
        return data  
    
   ##------------Inventory Window Function when treeview item is selected all of the information----------- 
   ##------------is entered back into the textboxes of Inventory window and then can be either-------------
   ##------------edited or deleted-------------------------------------------------------------------------
    def InvRecSelected(event):
        ResetInv()
        viewInfo = tree2.focus()
        selected_data = tree2.item(viewInfo)
        row = selected_data['values']
        save_btn_inv['state']='disabled'
        update_btn_inv['state']='normal'
                
        #self.inv_ent_site.insert(0, row[1])  ##is now being handled by its own function                
        pn_txt_inv.insert(0, row[2])            
        desc_txt_inv.insert(0, row[3])
        qty_txt_inv.delete(0, tk.END)
        qty_txt_inv.insert(0, row[4])
        global inv_rec_id
        inv_rec_id = format(row[0])     # must be formatted to a string so the update function can use it
        #tree2.selection_set('')  # to remove the high lighting from the selected record
        return inv_rec_id
    
    ##------------Inventory Window Function-----------
    def UpdateWarning():
        # verify that a record has been selected
        pn_get = pn_txt_inv.get() # must be assigned to a vaiable for the warning box to work
        
        if pn_get == '':
            tkinter.messagebox.showwarning('', "A record needs to have been selected.", parent=InvChild)
        else:
            UpdateInvRec()
        
                      
    ##------------Inventory Window Function if a record has been edited enter changes into the database-----------
    ##------------which in turn will be shown in the treeview-----------------------------------------------------
    def UpdateInvRec():
        global inv_rec_id
        
        qty_get = int(qty_txt_inv.get())
        use_get = int(use_txt_inv.get())
        new_qty = qty_get - use_get
       
        
        conn = sqlite3.connect("service.db")
        cur = conn.cursor()
        #cur.execute("UPDATE inventory SET site=?, part=?, desc=?, qty=? WHERE id=?", \
        #        (site_txt_inv.get(), pn_txt_inv.get(), desc_txt_inv.get(), qty_txt_inv.get(), inv_rec_id,)) 
        
        if use_txt_inv.get() == '0':
            cur.execute("UPDATE inventory SET site=?, part=?, desc=?, qty=? WHERE id=?", \
                    (site_txt_inv.get(), pn_txt_inv.get(), desc_txt_inv.get(), qty_txt_inv.get(), inv_rec_id,))            
        else:     
            cur.execute("UPDATE inventory SET site=?, part=?, desc=?, qty=? WHERE id=?", \
                    (site_txt_inv.get(), pn_txt_inv.get(), desc_txt_inv.get(), new_qty, inv_rec_id,))
           
        cur.execute("UPDATE inventory SET site = '%s'" % (site_txt_inv.get()))
        conn.commit()            
        conn.close()    
        DisplayInvData()
        ResetInv()
        save_btn_inv['state']='normal'
        update_btn_inv['state']='disabled'
        return
    
    ##------------Inventory Window Function empty all the textboxes-----------
    def ResetInv():
        site_txt_inv.delete(0, tk.END)
        pn_txt_inv.delete(0, tk.END)
        desc_txt_inv.delete(0, tk.END)
        qty_txt_inv.delete(0, tk.END)
        qty_txt_inv.insert(tk.END,"0")
        use_txt_inv.delete(0, tk.END)
        use_txt_inv.insert(tk.END, "0")
        update_btn_inv['state']='disabled'
        save_btn_inv['state']='normal'
        FillInvSiteid()
        pn_txt_inv.focus()
        return
    
    ##------------Inventory Window Function verify a selection before deleting is allowed-----------
    def DeleteWarning():
        global inv_rec_id
        viewInfo = tree2.focus()
        selected_data = tree2.item(viewInfo)
        row = selected_data['values']
        
        if len(row) == 0:
            tkinter.messagebox.showwarning('', "A record needs to have been selected.", parent=InvChild)
        else:
            DeleteInvData()
    
    ##------------Inventory Window Function delete record from database and treeview-----------
    def DeleteInvData():
        global inv_rec_id
        conn = sqlite3.connect("service.db")
        cur = conn.cursor()
        cur.execute("DELETE FROM inventory WHERE id=?", (inv_rec_id,))
        conn.commit()
        conn.close()
        DisplayInvData()
        ResetInv()
        return
    
    ##------------Inventory Window Function search for records using string or portion of string-----------
    def InvSrch():
        if SEARCH.get() != "":
            tree2.delete(*tree2.get_children())
            conn = sqlite3.connect("service.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM `inventory` WHERE `part` LIKE ? OR `desc` LIKE ?", ('%'+str(SEARCH.get())+'%', '%'+str(SEARCH.get())+'%'))
            fetch = cursor.fetchall()
            for data in fetch:
                tree2.insert('', 'end', values=(data))
            cursor.close()
            conn.close()
        
    
    ##------------Inventory Window Function empties search from textbox and treeview and-----------
    ##------------restores all records to the treeview---------------------------------------------
    def EndInvSrch():
        srch_txt_inv.delete(0, tk.END)
        site_txt_inv.delete(0, tk.END)
        DisplayInvData()
    
    ##------------Inventory Window Function close the Inventory window-----------
    def ExitInv():
        InvChild.destroy()
        return            
        
        
       
    
    
    #================================Inventory Labels===============================
    #===============================================================================
    
    info1_lbl_inv =tk.Label(frame3a, text='To add a new item to the list, fill in the text boxes and press ADD   To update an item in the above list, select it, make your changes and hit UPDATE')
    info1_lbl_inv.place(relx=0.14, rely=0.3, relwidth=0.7, relheight=0.75)
    info2_lbl_inv =tk.Label(frame3a, text='To update an item in the above list, select it, make your changes and hit UPDATE')
    #info2_lbl_inv.place(relx=0.055, rely=0.4, relwidth=0.3, relheight=0.75)
    site_lbl_inv = tk.Label(frame3a, text="SiteID", font=40)
    site_lbl_inv.place(relx=0.12, rely=0.5, relwidth=0.1, relheight=0.075)
    pn_lbl_inv = tk.Label(frame3a, text="Part Number", font=40)
    pn_lbl_inv.place(relx=0.275, rely=0.5, relwidth=0.1, relheight=0.075)
    desc_lbl_inv = tk.Label(frame3a, text="Description", font=40)
    desc_lbl_inv.place(relx=0.515, rely=0.5, relwidth=0.1, relheight=0.075) 
    qty_lbl_inv = tk.Label(frame3a, text="Qty", font=40)
    qty_lbl_inv.place(relx=0.812, rely=0.5, relwidth=0.05, relheight=0.075)
    use_lbl_inv = tk.Label(frame3a, text="Installed", font=40)
    use_lbl_inv.place(relx=0.891, rely=0.5, relwidth=0.062, relheight=0.075)    
    srch_lbl_inv = tk.Label(frame3a, text="Search: ", font=40)
    srch_lbl_inv.place(relx=0.23, rely=0.87, relwidth=0.06, relheight=0.075)
    copyright_lbl = tk.Label(frame3a, text="June 2021 Created by Paul Higginbotham as Free to Use Software")
    copyright_lbl.place(rely=0.92,relwidth=1, relheight=0.15)    
    
    #================================Inventory Entry Boxes==========================
    #===============================================================================
    str_pn = tk.StringVar()
    str_desc = tk.StringVar()
    str_qty = tk.StringVar()
    str_use = tk.StringVar()
    
    site_txt_inv = tk.Entry(frame3a, font=40)
    site_txt_inv.place(relx=0.14, rely=0.57, relwidth=0.11, relheight=0.075)
    #self.inv_ent_site.insert(END, row[0])
    pn_txt_inv = tk.Entry(frame3a, font=40, textvariable=str_pn)
    pn_txt_inv.place(relx=0.27, rely=0.57, relwidth=0.225, relheight=0.075)
    desc_txt_inv = tk.Entry(frame3a, font=40, textvariable=str_desc)
    desc_txt_inv.place(relx=0.515, rely=0.57, relwidth=0.285, relheight=0.075)
    qty_txt_inv = tk.Entry(frame3a, font=40, textvariable=str_qty)
    qty_txt_inv.place(relx=0.82, rely=0.57, relwidth=0.05, relheight=0.075)
    #qty_txt_inv.bind('<Return>', lambda event=None: SaveInvRec())
    use_txt_inv = tk.Entry(frame3a, font=40, textvariable=str_use)
    use_txt_inv.place(relx=0.89, rely=0.57, relwidth=0.05, relheight=0.075)
    #use_txt_inv.bind('<Return>', lambda event=None: UpdateWarning())    
    srch_txt_inv = tk.Entry(frame3a, font=40, textvariable=SEARCH)
    srch_txt_inv.place(relx=0.29, rely=0.875, relwidth=0.225, relheight=0.075)
    
    #================================Inventory Buttons==============================
    #===============================================================================
    save_btn_inv = tk.Button(frame3c, text=" ADD ", font=40, command=lambda: SaveInvRec())
    save_btn_inv.place(relx=0.045, rely=0.13, relwidth=0.1, relheight=0.75)
    update_btn_inv = tk.Button(frame3c, text="UPDATE", font=40, state='disabled', command=lambda: UpdateWarning())
    update_btn_inv.place(relx=0.16, rely=0.13, relwidth=0.1, relheight=0.75)
    delete_btn_inv = tk.Button(frame3c, text="DELETE", font=40, command=lambda: DeleteWarning())
    delete_btn_inv.place(relx=0.275, rely=0.13, relwidth=0.1, relheight=0.75)
    clear_btn_inv = tk.Button(frame3c, text="CLEAR", font=40, command=lambda: ResetInv())
    clear_btn_inv.place(relx=0.39, rely=0.13, relwidth=0.1, relheight=0.75)        
    
    srch_btn_inv = tk.Button(frame3a, text="SEARCH", font=40, command=lambda: InvSrch())
    srch_btn_inv.place(relx=0.535, rely=0.875, relwidth=0.1, relheight=0.075)
    done_btn_inv = tk.Button(frame3a, text="CLEAR", font=40, command=lambda: EndInvSrch())
    done_btn_inv.place(relx=0.65, rely=0.875, relwidth=0.1, relheight=0.075)
    exit_btn_inv = tk.Button(frame3c, text="EXIT", font=40, command=lambda: ExitInv())
    exit_btn_inv.place(relx=0.85, rely=0.13, relwidth=0.1, relheight=0.75)
    
    #================================Inventory TreeView=============================
    #===============================================================================   
    tree2 = ttk.Treeview(frame3b)
    yscroll = ttk.Scrollbar(frame3b, orient=tk.VERTICAL, command=tree2.yview)
    tree2.configure(yscroll=yscroll.set, selectmode="browse")
    tree2.configure(columns=("ID","SiteID", "Part Number", "Description", "Qty"))
    yscroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    
    tree2.heading("ID", text="ID", anchor=tk.W)
    tree2.heading("SiteID", text="SiteID", anchor=tk.W)
    tree2.heading("Part Number", text="Part Number", anchor=tk.W)
    tree2.heading("Description", text="Description", anchor=tk.W)
    tree2.heading("Qty", text="Qty", anchor=tk.W)
    tree2['show'] = 'headings'
    
    tree2.column("ID", width=5)
    tree2.column("SiteID", width=20)
    tree2.column("Part Number", width=150)
    tree2.column("Description", width=340)
    tree2.column("Qty", width=50)
                
    tree2.pack(fill=tk.BOTH, expand=1) 
    tree2.bind("<ButtonRelease-1>", InvRecSelected) 
    DisplayInvData()
    
def UpdateChildWindow():
    #######################child window 'Update'############################################
    ########################################################################################
    updateChild = tk.Toplevel(window1) # Child window
    # updateChild.iconbitmap('word_pen.ico')
    updateChild.title("Update Record")
    
    # center child window to the user screen
    WIDTH=1200
    HEIGHT=600
    sc_width = updateChild.winfo_screenwidth()
    sc_height = updateChild.winfo_screenheight()
    x_coordinate = (sc_width/2)-(WIDTH/2)
    y_coordinate = (sc_height/2)-(HEIGHT/2)        
    updateChild.geometry("%dx%d+%d+%d"%(WIDTH, HEIGHT, x_coordinate, y_coordinate))
    
    frame1 = tk.Frame(updateChild) # Full Window Frame
    frame1.place(relwidth=1, relheight=1)
    
    frame2a = tk.Frame(frame1)   # Date, TR and WO/PO Labels
    frame2a.place(relx=0.5, rely=0.025, relwidth=0.95, relheight=0.775, anchor='n')
    
    frame2b = tk.Frame(frame1)   # Buttons
    frame2b['relief'] = 'ridge'
    frame2b.place(relx=0.5, rely=0.82, relwidth=0.95, relheight=0.15, anchor='n')
    
##------------Update Window Function-----------
    def UpdateRec():
        
        conn = sqlite3.connect("service.db")
        cur = conn.cursor()
        cur.execute("UPDATE ticket SET date=?, tr=?, wo=?, cust=?, addr=?, issue=?, notes=? WHERE id=?", \
                    (cal_txt_update.get(), tr_txt_update.get(), wo_txt_update.get(), cust_txt_update.get(), addr_txt_update.get(),
                     issue_txt_update.get(), notes_txt_update.get('1.0', tk.END), start_rec_id,))
        conn.commit()
        conn.close()
        DisplayData()
    
        update_var1 = cal_txt_update.get()
        update_var2 = tr_txt_update.get()
        update_var3 = wo_txt_update.get()
        update_var4 = cust_txt_update.get()
        update_var5 = addr_txt_update.get()
        
        update_var6 = issue_txt_update.get()
        update_var7 = notes_txt_update.get('1.0', tk.END)
    
        RefillWindow1(update_var1, update_var2, update_var3, update_var4, update_var5, update_var6, update_var7)
            
        updateChild.destroy()
        return
    
    ##------------Update Window Function-----------
    def CancelUpdate():
        updateChild.destroy()
        return    
    
    ##================================Update Labels==================================
    ##===============================================================================
    date_lbl_update = tk.Label(frame2a, text="Date: ", font=40)
    date_lbl_update.place(relx=0.03, relwidth=0.04, relheight=0.05)
    tr_lbl_update = tk.Label(frame2a, text="Tracking  #: ", font=40)
    tr_lbl_update.place(relx=0.235, relwidth=0.075, relheight=0.05)
    wo_lbl_update = tk.Label(frame2a, text="WO/PO: ", font=40)
    wo_lbl_update.place(relx=0.625, relwidth=0.06, relheight=0.05)
    
    cust_lbl_update = tk.Label(frame2a, text="Customer: ", font=40)
    cust_lbl_update.place(relx=0.03, rely=0.135, relwidth=0.07, relheight=0.05)
    addr_lbl_update = tk.Label(frame2a, text="Address: ", font=40)
    addr_lbl_update.place(relx=0.505, rely=0.135, relwidth=0.07, relheight=0.05)
    
    
    issue_lbl_update = tk.Label(frame2a, text="Issue: ", font=40)
    issue_lbl_update.place(relx=0.03, rely=0.4, relwidth=0.05, relheight=0.05)
    
    notes_lbl_update = tk.Label(frame2a, text="Notes / Parts Used / Parts Ordered: ", font=40)
    notes_lbl_update.place(relx=0.03, rely=0.535, relwidth=0.23, relheight=0.05)
    
    copyright_lbl = tk.Label(frame2b, text="June 2021 Created by Paul Higginbotham as Free to Use Software")
    copyright_lbl.place(rely=0.85,relwidth=1, relheight=0.15)    
    
    ##================================Update Entryboxes==============================
    ##===============================================================================
    update_var1 = tk.StringVar()
    update_var2 = tk.StringVar()
    update_var3 = tk.StringVar()
    update_var4 = tk.StringVar()
    update_var5 = tk.StringVar()
    
    update_var6 = tk.StringVar()
    update_var7 = tk.StringVar()    
    
    cal_txt_update = DateEntry(frame2a, font=40, year=2021, textvariable=update_var1)
    cal_txt_update.place(relx=0.025, rely=0.055, relwidth=0.1, relheight=0.06)
    tr_txt_update = tk.Entry(frame2a, font=40, textvariable=update_var2)
    tr_txt_update.place(relx=0.23, rely=0.055, relwidth=0.3, relheight=0.06)
    wo_txt_update = tk.Entry(frame2a, font=40, textvariable=update_var3)
    wo_txt_update.place(relx=0.62, rely=0.055, relwidth=0.355, relheight=0.06)
    
    cust_txt_update = tk.Entry(frame2a, font=40, textvariable=update_var4)
    cust_txt_update.place(relx=0.025, rely=0.19, relwidth=0.425, relheight=0.06)
    addr_txt_update = tk.Entry(frame2a, font=40, textvariable=update_var5)
    addr_txt_update.place(relx=0.5, rely=0.19, relwidth=0.475, relheight=0.06)
    
    
    issue_txt_update = tk.Entry(frame2a, font=40, textvariable=update_var6)
    issue_txt_update.place(relx=0.025, rely=0.46, relwidth=0.95, relheight=0.06)
    
    notes_txt_update = scrolledtext.ScrolledText(frame2a, wrap='word', font=40)
    notes_txt_update.place(relx=0.025, rely=0.6, relwidth=0.95, relheight=0.375)
    
    ##================================Update Buttons=================================
    ##===============================================================================
    save_btn = tk.Button(frame2b, text="SAVE", font=40, bd=2, command=lambda: UpdateRec())
    save_btn.place(relx=0.03, rely=0.1, relwidth=0.1, relheight=0.4)
    cancel_btn = tk.Button(frame2b, text="Cancel", font=40, bd=2, command=lambda: CancelUpdate())
    cancel_btn.place(relx=0.14, rely=0.1, relwidth=0.1, relheight=0.4)
    
    update_var1 = cal_txt.get()
    cal_txt_update.insert('', update_var1)
    update_var2 = tr_txt.get()
    tr_txt_update.insert(tk.END, update_var2) 
    update_var3 = wo_txt.get()
    wo_txt_update.insert(tk.END, update_var3) 
    update_var4 = cust_cbo.get()
    cust_txt_update.insert(tk.END, update_var4)
    update_var5 = addr_cbo.get()
    addr_txt_update.insert(tk.END, update_var5)
    
    update_var6 = issue_txt.get()
    issue_txt_update.insert(tk.END, update_var6)
    update_var7 = notes_txt.get('1.0', tk.END)
    notes_txt_update.delete('1.0', tk.END)
    notes_txt_update.insert(tk.END, update_var7)    
    
def InfoWindow():
    #######################Child Window 'Information'#######################################
    ########################################################################################
    InfoChild = tk.Toplevel(window1) # Child window
    InfoChild.title("Information")
    
    # centers the Information window to users screen
    WIDTH=1024
    HEIGHT=700
    sc_width = InfoChild.winfo_screenwidth()
    sc_height = InfoChild.winfo_screenheight()
    x_coordinate = (sc_width/2)-(WIDTH/2)
    y_coordinate = (sc_height/2)-(HEIGHT/2)        
    InfoChild.geometry("%dx%d+%d+%d"%(WIDTH, HEIGHT, x_coordinate, y_coordinate))
    
    # was used to outline the frames(, highlightbackground='sky blue', highlightcolor='sky blue', highlightthickness=2)
    # and the textboxes during development
    info_frame1 = tk.Frame(InfoChild)
    info_frame1.place(relwidth=1, relheight=1)
    
    info_frame2 = tk.Frame(info_frame1, bd=10, highlightbackground='sky blue', highlightcolor='sky blue', highlightthickness=2) 
    info_frame2.place(relwidth=1, relheight=0.8)
    info_frame2b = tk.Frame(info_frame1, highlightbackground='sky blue', highlightcolor='sky blue', highlightthickness=2)
    info_frame2b.place(rely=0.81, relwidth=1, relheight=0.1)
    
    cust_name = tk.StringVar()
    cust_notes = tk.StringVar()
    
    ##================================Info Functions=================================
    ##===============================================================================
    
    def get_cust():
        InfoWindow.cust_name = cust_cbo.get()
    get_cust()
    
    def exit_info_window():
        InfoChild.destroy()
    
    def display_info():
        var_notes = tk.StringVar()
        info_cust_notes_txt.delete("1.0", tk.END)
        conn = sqlite3.connect("service.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM `cust_info` WHERE cust_name LIKE ?", (InfoWindow.cust_name,))
        data = []
        fetch = cur.fetchall()
        for row in fetch:
            info_cust_notes_txt.insert(tk.END, row[2])
        cur.close()
        conn.close
        
        var_notes = info_cust_notes_txt.get(1.0, 'end-1c')
        if var_notes == '':
            if info_update_btn['state']=='normal':
                info_update_btn['state']='disabled'
        else:
            info_save_btn['state']='disabled'
            info_update_btn['state']='normal'
    
    def update_cust_info():            
        conn = sqlite3.connect("service.db")
        cur = conn.cursor()
        cur.execute("UPDATE cust_info SET cust_notes = ? WHERE cust_name = ?", (info_cust_notes_txt.get('1.0', tk.END), InfoWindow.cust_name))
        conn.commit()            
        conn.close()            
        display_info()
    
    
        
    def Save_Info():
        
        var1 = info_cust_notes_txt.get(1.0, 'end-1c')
    
        cntr = 0
        
        if var1 == '':  # checking for empty text boxes
            cntr = cntr+1
        
        if cntr > 0:
            # to keep the child window on top when an error occurs use the 'parent=??'
            tkinter.messagebox.showwarning('', "There must be customer information entered into the Notes.", parent=InfoChild)
        
        if cntr == 0:
            conn = sqlite3.connect("service.db")
            cur = conn.cursor()
            cur.execute("INSERT INTO cust_info VALUES(NULL,?,?)", (InfoWindow.cust_name, info_cust_notes_txt.get('1.0', tk.END)))
            conn.commit()
            conn.close
            display_info()
    ##================================Info Labels====================================
    ##===============================================================================    
    info_cust_lbl = tk.Label(info_frame2, text=(InfoWindow.cust_name), font=40)
    info_cust_lbl.place(rely=0.01, relwidth=1, relheight=0.05)
    
    info_cust_notes_txt = scrolledtext.ScrolledText(info_frame2, wrap='word', font=40)
    info_cust_notes_txt.place(relx=0.025, rely=0.17, relwidth=0.95, relheight=0.6)
    
    copyright_lbl = tk.Label(info_frame1, text="June 2021 Created by Paul Higginbotham as Free to Use Software")
    copyright_lbl.place(rely=0.96,relwidth=1, relheight=0.035)  
    
    
    #info_vrfy_btn = tk.Checkbutton(info_frame1, text="Check this box if you want to verify the button selections")
    #info_vrfy_btn.place(rely=0.92, relwidth=1, relheight=0.025)
    
    info_save_btn = tk.Button(info_frame2b, text="SAVE", font=40, bd=2, command=lambda: Save_Info())
    info_save_btn.place(relx=0.025, rely=0.35, relwidth=0.15, relheight=0.5)
    
    info_update_btn = tk.Button(info_frame2b, text="UPDATE", font=40, bd=2, command=lambda: update_cust_info())
    info_update_btn.place(relx=0.225, rely=0.35, relwidth=0.15, relheight=0.5)    
    
    #info_delete_btn = tk.Button(info_frame2b, text="DELETE", font=40, bd=2)
    #info_delete_btn.place(relx=0.425, rely=0.35, relwidth=0.15, relheight=0.5)
    
    info_exit_btn = tk.Button(info_frame2b, text="EXIT", font=40, bd=2, command=lambda: exit_info_window())
    info_exit_btn.place(relx=0.825, rely=0.35, relwidth=0.15, relheight=0.5)
    
    display_info()
    
DisplayData()

window1.mainloop()