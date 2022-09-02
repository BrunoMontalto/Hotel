import tkinter
from tkinter.simpledialog import askstring
from tkcalendar import Calendar, DateEntry
import tkinter.font as font
from tkinter import messagebox
import mysql.connector
import random, time


mydb = mysql.connector.connect(host = "localhost", username = "root", password = "")
cursor = mydb.cursor()
cursor.execute("USE Hotel")




# Add test booking
cursor.execute("SELECT CURDATE()")
date = cursor.fetchone()[0].strftime("%Y/%m/%d")

cursor.execute("SELECT INTERVAL 7 DAY + CURDATE()")
enddate = cursor.fetchone()[0].strftime("%Y/%m/%d")


query = "INSERT INTO Soggiorno(data_prenotazione, data_inizio, data_fine, colazione, pranzo, cena, servizio_in_camera) VALUES('2022/08/30','" + date +"', '" + enddate + "', true, false, false, false)"
cursor.execute(query)

cursor.execute("INSERT INTO Soggiorno_Cliente VALUES((SELECT MAX(id) FROM Soggiorno),100)")
cursor.execute("INSERT INTO Soggiorno_Camera VALUES((SELECT MAX(id) FROM Soggiorno),25)")



photo = None

def replaceTags(query, qargs, values):
    assert len(qargs) == len(values)
    i = 0
    res = query[::]
    for a in qargs:
        res = res.replace(a, values[i])
        i += 1
    return res


def fixList(t):
    for i in range(len(t)):
        t[i] = t[i][0]


def labelTable(parent, columns, colors = ("#5FAF64", "#559B5E")):
    table = tkinter.Frame(parent)
    res = []
    i = 0
    for c in columns:
        col = tkinter.Frame(table, bg = ("white" if i%2 == 0 else "#E5E5E5"))
        col.grid(row = 0, column = i)
        tkinter.Label(col, text = c, bg = (colors[0] if i%2 == 0 else colors[1]), fg= "white").pack()
        res.append(col)
        i += 1
    return table, res

def labelTableInsert(columns, values):
    #assert len(columns) == len(values)
    for i in range(len(values)):
        tkinter.Label(columns[i], text = values[i], fg = "#262626", bg = ("white" if i%2 == 0 else "#E5E5E5") ).pack()


def widgetRow(widgets, pad = 3):    
    i = 0
    for w in widgets:
        w.pack(side = tkinter.LEFT, padx= pad)
        i += 1

# --- Entra functioms ---
def checkExpiredBooking():
    
    cursor.execute("UPDATE Soggiorno SET data_annullamento = CURDATE() WHERE data_annullamento IS NULL AND check_in IS NULL AND check_out IS NULL AND CURDATE() > data_inizio")
    
def recordCheckin(booking_id):
    global gui
    

    cursor.execute("SELECT NOW()")
    date = cursor.fetchone()[0].strftime("%d/%m/%Y %H:%M:%S")

    data, ore = date.split(" ")
    ore = ore[:-3]

    res = messagebox.askquestion("Conferma registrazione check in", "Registrare il checkin per la prenotazione con codice(" + str(booking_id) + ") per la data " + data + " alle ore " + ore +"?", icon='question')
    
  
    if res == "yes":
        cursor.execute("UPDATE Soggiorno SET check_in ='" + date + "' WHERE Soggiorno.id = " + str(booking_id))
        gui.refreshBooking()
        gui.refreshActiveStays()
        gui.refreshRooms()
        gui.refreshClients()


def recordCheckout(stay_id):
    global gui
    

    cursor.execute("SELECT NOW()")
    date_ = cursor.fetchone()[0]
    date = date_.strftime("%d/%m/%Y %H:%M:%S")

    data, ore = date.split(" ")
    ore = ore[:-3]

    res = messagebox.askquestion("Conferma registrazione check out", "Registrare il checkout per il soggiorno con codice(" + str(stay_id) + ") per la data " + data + " alle ore " + ore +"?", icon='question')
    
  
    if res == "yes":
        cursor.execute("UPDATE Soggiorno SET check_out ='" + date_.strftime("%Y/%m/%d %H:%M:%S") + "' WHERE Soggiorno.id = " + str(stay_id))
        gui.refreshActiveStays()
        gui.refreshPastStays()
        gui.refreshRooms()
        gui.refreshClients()


def recordPayment(stay_id):
    global gui
    cursor.execute("SELECT importo FROM Pagamento WHERE id_soggiorno = " + str(stay_id))
    paym = cursor.fetchone()[0]
    cid = askstring("Registra pagamento per il soggiorno con codice(" + str(stay_id) + ")", "Inserire l'identificativo numerico del cliente da associare al pagamento.")

    try:
        if cid == None: return
        temp = int(cid)
        cursor.execute("SELECT id FROM Cliente WHERE id = " + cid)
        res = cursor.fetchall()
    except:
        res = []
        
    
    while len(res) != 1:
        cid = askstring("Registra pagamento per il soggiorno con codice(" + str(stay_id) + ")", "Cliente inesistente!\n Inserire nuovamente l'identificativo numerico del cliente da associare al pagamento.")

        try:
            if cid == None: return
            temp = int(cid)
            cursor.execute("SELECT id FROM Cliente WHERE id = " + cid)
            res = cursor.fetchall()
        except:
            res = []

    cursor.execute("SELECT nazionalità, nome, cognome, genere FROM Cliente WHERE id = " + cid)
    client = cursor.fetchone()
    ok = messagebox.askquestion("Cliente trovato!", "nazionalità: " + client[0] + "\nnome: " + client[1] + "\ncognome: " + client[2] + "\ngenere: " + client[3] + "\n\nAssociare il pagamento di " + str(paym) + "€ per il soggiorno con codice("+str(stay_id)+") a questo cliente?", icon = "question")
    if ok == "yes":
        cursor.execute("UPDATE Pagamento SET id_cliente = " + cid + ", data_e_ora = NOW()")
        gui.refreshPayments()


def insertService(cf, service, room):
    global gui
    res = messagebox.askquestion("Conferma", "Inserire servizio?", icon = "question")
    if res != "yes": return
    room = "'" + room + "'"
    if room == "'-'": room = "NULL"
    query = "INSERT INTO Servizio_Cameriere(codice_cameriere, tipo, numero_camera, data_e_ora) VALUES ('" + cf + "', '" + service + "', " + room +", NOW())"
    cursor.execute(query)
    gui.refreshServices()


def insertSalary(cf, amount, date):
    global gui
    date = date.strftime("%Y/%m/%d") 
    try:
        temp = int(amount)
    except: return
    res = messagebox.askquestion("Conferma", "Inserire stipendio?", icon = "question")
    if res != "yes": return
    cursor.execute("INSERT INTO Stipendio_Cameriere(codice_cameriere, retribuzione, data) VALUES('" + cf + "'," + amount + ",'"+date+"')")
    gui.refreshSalaries()  


def insertSalaryE(amount, date):
    global gui
    date = date.strftime("%Y/%m/%d") 
    try:
        temp = int(amount)
    except: return
    res = messagebox.askquestion("Conferma", "Vuoi davvero registrare lo stipendio di " + str(amount) + "€ per TUTTI i camerieri alla data " + date + "?", icon = "warning")
    if res != "yes": return
    cursor.execute("SELECT codice_fiscale FROM Cameriere")
    maids = cursor.fetchall()
    for m in maids:
        cursor.execute("INSERT INTO Stipendio_Cameriere(codice_cameriere, retribuzione, data) VALUES('" + m[0] + "'," + amount + ",'"+date+"')")
    gui.switch_to_page(8)
    
class HotelGUI:
    def __init__(self):
        global photo
        
        self.window = tkinter.Tk()
        self.window.geometry('874x540')
        self.window.resizable(False, False)
        self.window.wm_title("Interfaccia Hotel")
        self.window.iconbitmap(r'src/hotel.ico')
        self.window.config(background = "#E5E5E5")

        

        self.myfont = font.Font(family='Consolas', size = 10)
        self.myfont1 = font.Font(family='Consolas', size = 4)
        self.myfont2 = font.Font(family='Consolas', size = 14)
        

        photo = tkinter.PhotoImage(file = r"src/registra.png", width = 82, height = 15)

        
        #s = tkinter.Scrollbar(self.pages[0])
        #s.config(command = self.pages[0].yview)
        #s.pack(side = tkinter.RIGHT, fill = tkinter.Y)

        

        tkinter.Label(self.window,  text = "\n\n\n\n\n", font = self.myfont1, bg = "#E5E5E5").pack()
        self.menu = [(tkinter.Button(self.window, text = "Prenotazioni", command = lambda: self.switch_to_page(0), fg = "white",activebackground="#4A875B", activeforeground = "white",highlightthickness = 3, bd = 0), [0,0]),
                     (tkinter.Button(self.window, text = "Soggiorni in corso", command = lambda: self.switch_to_page(1), fg = "white",activebackground="#4A875B", activeforeground = "white",highlightthickness = 3, bd = 0), [95,0]),
                     (tkinter.Button(self.window, text = "Soggiorni passati", command = lambda: self.switch_to_page(2), fg = "white",activebackground="#4A875B", activeforeground = "white", highlightthickness = 3, bd = 0), [230,0]),
                     (tkinter.Button(self.window, text = "Camere", command = lambda: self.switch_to_page(3), fg = "white",activebackground="#4A875B", activeforeground = "white", highlightthickness = 3, bd = 0), [357,0]),
                     (tkinter.Button(self.window, text = "Clienti", command = lambda: self.switch_to_page(4), fg = "white",activebackground="#4A875B", activeforeground = "white", highlightthickness = 3, bd = 0), [408,0]),
                     (tkinter.Button(self.window, text = "Pagamenti", command = lambda: self.switch_to_page(5), fg = "white",activebackground="#4A875B", activeforeground = "white", highlightthickness = 3, bd = 0), [467,0]),
                     (tkinter.Button(self.window, text = "Camerieri", command = lambda: self.switch_to_page(6), fg = "white",activebackground="#4A875B", activeforeground = "white", highlightthickness = 3, bd = 0), [539,0]),
                     (tkinter.Button(self.window, text = "Servizi Camerieri", command = lambda: self.switch_to_page(7), fg = "white",activebackground="#4A875B", activeforeground = "white", highlightthickness = 3, bd = 0), [611,0]),
                     (tkinter.Button(self.window, text = "Stipendi Camerieri", command = lambda: self.switch_to_page(8), fg = "white",activebackground="#4A875B", activeforeground = "white", highlightthickness = 3, bd = 0), [739,0])
        ]



        self.curr_page = 0

        self.pages = []
        self.canvases = []
        self.cframes = []


        
        
        self.initPages()
        

        
        

        #for p in range(1,9):
        #    for i in range(p*10): tkinter.Label(self.cframes[p], text = "lol"+str(i)).pack(anchor = "center")
        

        for i in range(len(self.menu)):
            self.menu[i][0].config(font = self.myfont)
            if i > 0:
                self.menu[i][0].config(bg = ("#5FAF64" if i%2==0 else "#559B5E"))
            self.menu[i][0].place(x = self.menu[i][1][0], y = self.menu[i][1][1])
        
        #load page content
        #for i in range(9):
        #    self.switch_to_page(8-i)
        self.refreshBooking()
        self.refreshActiveStays()
        self.refreshPastStays()
        self.refreshRooms()
        self.refreshClients()
        self.refreshPayments()
        self.refreshMaids()
        self.refreshServices()
        self.refreshSalaries()

        


        self.switch_to_page(0)




    def start(self):
        self.window.mainloop()


    def foo(self):
        cursor.execute("INSERT into soggiorno_cliente (id_soggiorno, id_cliente) VALUES('1','2');")
        mydb.commit()
        self.refreshBooking()
        
    def initPages(self):
        self.booking_index = 0
        cursor.execute("SELECT id FROM Soggiorno WHERE check_in IS NULL ORDER BY data_inizio")
        self.booking = cursor.fetchall()
        fixList(self.booking)
        for i in range(9):
            
            # --- create canvas with scrollbar ---
            page_frame = tkinter.Frame(self.window, bg = "#E5E5E5")
            self.pages.append(page_frame)

            if i == 0:
                wframe0 = tkinter.Frame(self.pages[0], bg = "#E5E5E5")
                self.searchEntry0 = tkinter.Entry(wframe0)
                widgetRow([tkinter.Label(wframe0, text = "Cerca per codice (lasciare vuoto per visualizzare tutte)", font = self.myfont, bg = "#E5E5E5", fg = "#262626"),self.searchEntry0,
                           tkinter.Button(wframe0, text = "Cerca", font = self.myfont, command = lambda: self.refreshBooking())])
                wframe0.pack(pady = 3)

            elif i == 1:
                wframe1 = tkinter.Frame(self.pages[1], bg = "#E5E5E5")
                self.searchEntry1 = tkinter.Entry(wframe1)
                widgetRow([tkinter.Label(wframe1, text = "Cerca per codice (lasciare vuoto per visualizzare tutti)", font = self.myfont, bg = "#E5E5E5", fg = "#262626"),self.searchEntry1,
                           tkinter.Button(wframe1, text = "Cerca", font = self.myfont, command = lambda: self.refreshActiveStays())])
                wframe1.pack(pady = 3)

            elif i == 2:
                wframe2 = tkinter.Frame(self.pages[2], bg = "#E5E5E5")
                self.searchEntry2 = tkinter.Entry(wframe2)
                widgetRow([tkinter.Label(wframe2, text = "Cerca per codice (lasciare vuoto per visualizzare tutti)", font = self.myfont, bg = "#E5E5E5", fg = "#262626"),self.searchEntry2,
                           tkinter.Button(wframe2, text = "Cerca", font = self.myfont, command = lambda: self.refreshPastStays())])
                wframe2.pack(pady = 3)
                
            elif i == 4:
                wframe4 = tkinter.Frame(self.pages[4], bg = "#E5E5E5")
                self.searchEntry4 = tkinter.Entry(wframe4)
                widgetRow([tkinter.Label(wframe4, text = "Cerca per id (lasciare vuoto per visualizzare tutti)", font = self.myfont, bg = "#E5E5E5", fg = "#262626"),self.searchEntry4,
                           tkinter.Button(wframe4, text = "Cerca", font = self.myfont, command = lambda: self.refreshClients())])
                wframe4.pack(pady = 3)

            elif i == 5:
                wframe5 = tkinter.Frame(self.pages[5], bg = "#E5E5E5")
                self.searchEntry5 = tkinter.Entry(wframe5)
                widgetRow([tkinter.Label(wframe5, text = "Cerca per codice soggiorno (lasciare vuoto per visualizzare tutti)", font = self.myfont, bg = "#E5E5E5", fg = "#262626"),self.searchEntry5,
                           tkinter.Button(wframe5, text = "Cerca", font = self.myfont, command = lambda: self.refreshPayments())])
                wframe5.pack(pady = 3)

            elif i == 6:
                scrollbar2 = tkinter.Scrollbar(page_frame, orient='horizontal')
                scrollbar2.pack(side = tkinter.BOTTOM, fill='x')

            elif i == 7:
                cursor.execute("SELECT codice_fiscale, nome, cognome FROM Cameriere")
                options = cursor.fetchall()
                for j in range(len(options)):
                    options[j] = options[j][0] + " (" + options[j][1] + " " + options[j][2] + ")"

                
                wframe = tkinter.Frame(self.pages[7], bg = "#E5E5E5")
                
                self.maids_var = tkinter.StringVar(wframe)
                self.maids_var.set(options[0])
                maids_menu = tkinter.OptionMenu(wframe, self.maids_var, *options)

                self.serv_var = tkinter.StringVar(wframe)
                self.serv_var.set("pulizia camera")
                serv_menu = tkinter.OptionMenu(wframe, self.serv_var, "pulizia camera", "servizio in camera", "lavanderia")

                self.room_var = tkinter.StringVar(wframe)
                self.room_var.set("-")

                cursor.execute("SELECT COUNT(*) FROM Camera")
                n_rooms = cursor.fetchone()[0]
                room_menu = tkinter.OptionMenu(wframe, self.room_var, "-",*[str(i) for i in range(1,n_rooms + 1)])


                widgetRow((tkinter.Label(wframe, text = "Cameriere:", font = self.myfont, bg = "#E5E5E5"), maids_menu,
                           tkinter.Label(wframe, text = "Servizio:", font = self.myfont, bg = "#E5E5E5"), serv_menu,
                           tkinter.Label(wframe, text = "Camera(opzionale):", font = self.myfont, bg = "#E5E5E5"), room_menu,
                           tkinter.Button(wframe, text = "Inserisci", font = self.myfont, command = lambda: insertService(self.maids_var.get().split(" ")[0],self.serv_var.get(), self.room_var.get()))
                           ))
                wframe.pack()

            elif i == 8:
                cursor.execute("SELECT codice_fiscale, nome, cognome FROM Cameriere")
                options = cursor.fetchall()
                for j in range(len(options)):
                    options[j] = options[j][0] + " (" + options[j][1] + " " + options[j][2] + ")"

                wframe8 = tkinter.Frame(self.pages[8], bg = "#E5E5E5")
                self.searchEntry8 = DateEntry(wframe8)
                widgetRow([tkinter.Label(wframe8, text = "Cerca per data", font = self.myfont, bg = "#E5E5E5", fg = "#262626"),self.searchEntry8,
                           tkinter.Button(wframe8, text = "Cerca", font = self.myfont, command = lambda: self.refreshSalaries(False)),
                           tkinter.Button(wframe8, text = "Mostra tutti", font = self.myfont, command = lambda: self.refreshSalaries())])
                wframe8.pack(pady = 3)

                
                wframe = tkinter.Frame(self.pages[8], bg = "#E5E5E5")
                
                self.maids_var2 = tkinter.StringVar(wframe)
                self.maids_var2.set(options[0])
                maids_menu = tkinter.OptionMenu(wframe, self.maids_var2, *options)

                self.salary_entry = tkinter.Entry(wframe)

                self.date_entry = DateEntry(wframe)


                widgetRow((maids_menu,
                           tkinter.Label(wframe, text = "Stipendio:", font = self.myfont, bg = "#E5E5E5"), self.salary_entry,
                           tkinter.Label(wframe, text = "Data:", font = self.myfont, bg = "#E5E5E5"), self.date_entry,
                           tkinter.Button(wframe, text = "Inserisci", font = self.myfont, command = lambda: insertSalary(self.maids_var2.get().split(" ")[0], self.salary_entry.get(), self.date_entry.get_date())),
                           tkinter.Button(wframe, text = "Inserisci per tutti", font = self.myfont, command = lambda: insertSalaryE(self.salary_entry.get(), self.date_entry.get_date()))
                           ))
                wframe.pack()
            

                
                
            canvas = tkinter.Canvas(page_frame, width=800, height=460)
            canvas.pack(side=tkinter.LEFT)
            self.canvases.append(canvas)
            

            scrollbar = tkinter.Scrollbar(page_frame, command=canvas.yview)
            scrollbar.pack(side=tkinter.RIGHT, fill='y')
        
            
            canvas.configure(yscrollcommand = scrollbar.set)
            if i == 6:
                canvas.configure(xscrollcommand = scrollbar2.set)
                scrollbar2.configure(command=canvas.xview)

            
        
            
                
            #canvas.bind("<Configure>", lambda event, c=canvas: c.configure(scrollregion= c.bbox('all') ))

            # update scrollregion after starting 'mainloop'
            # when all widgets are in canvas
            
            

            # --- put frame in canvas ---
            cframe = tkinter.Frame(canvas, bg = "#F0F0F0")
            canvas.create_window((0,0), window=cframe, anchor='nw')
            
            canvas.yview_moveto('1.0')

            self.cframes.append(cframe)
            


            
            
            
            
        
        #for i in range(9):
        #    self.pages.append(tkinter.Frame(self.window, bg = "#E5E5E5"))
        #    tkinter.Label(self.pages[i],  text = "\naaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", bg = "#E5E5E5").pack()
             
             
            
    def switch_to_page(self, page):
        if page == 0:
            self.refreshBooking()
        elif page == 1:
            self.refreshActiveStays()
        elif page == 2:
            self.refreshPastStays()
        elif page == 3:
            self.refreshRooms()
        elif page == 4:
            self.refreshClients()
        elif page == 5:
            self.refreshPayments()
        elif page == 6:
            self.refreshMaids()
        elif page == 7:
            self.refreshServices()
        elif page == 8:
            self.refreshSalaries()

        self.menu[self.curr_page][0].config(bg = ("#5FAF64" if self.curr_page%2==0 else "#559B5E"), fg = "white", activeforeground = "white", activebackground = "#4A875B")
        self.pages[self.curr_page].pack_forget()
        self.menu[page][0].config(bg = "#E5E5E5", fg = "#262626", activeforeground = "#262626", activebackground = "#B5B5B5")
        self.pages[page].pack()

 
        self.curr_page = page


    def clearPage(self, page_index, save = 0):
        p = self.cframes[page_index]
        widgets = p.winfo_children()
        for i in range(save,len(widgets)):
            widgets[i].destroy()

    # --- BOOKING --- #
    
        
    def refreshBooking(self):
        filter_id = self.searchEntry0.get()
        filt = True
        try:
            filter_id = int(filter_id)
        except:
            filt = False
            
        self.clearPage(0, 0)
        if filt:
            cursor.execute("SELECT id FROM Soggiorno WHERE id = " + str(filter_id) + " AND check_in IS NULL ORDER BY data_annullamento, data_inizio")
        else:
            cursor.execute("SELECT id FROM Soggiorno WHERE check_in IS NULL ORDER BY data_annullamento, data_inizio")
        self.booking = cursor.fetchall()
        
        fixList(self.booking)
        #print("prenotazioni:",self.booking)


        self.bookingLabels()
            
        self.canvases[0].configure(scrollregion = self.canvases[0].bbox("all"))

    def bookingLabels(self):
        global cursor
        cursor.execute("SELECT NOW()")
        date = cursor.fetchone()[0].strftime("%d/%m/%Y")
        for booking_id in self.booking:
            booking_label = tkinter.Frame(self.cframes[0], bg = "#D1D1D1")

            #estrai id della prenotazione e trova le altre informazioni su di essa
            #booking_id = self.booking[self.booking_index]
            cursor.execute("SELECT data_prenotazione, data_inizio, data_fine, data_annullamento FROM Soggiorno WHERE Soggiorno.id = " + str(booking_id))
            booking = cursor.fetchone()
            #print("prenotazione da visualizzare:", booking)
            #trova tutti i clienti associati alla prenotazione
            query = "SELECT id_cliente, nazionalità,nome, cognome, email, cellulare FROM soggiorno_cliente, cliente WHERE soggiorno_cliente.id_cliente = cliente.id AND soggiorno_cliente.id_soggiorno = {id_soggiorno}"
            query = replaceTags(query, ["{id_soggiorno}"], [str(booking_id)])
            cursor.execute(query)
            clients = cursor.fetchall()
            #print("clienti prenotazione",booking_id,":",clients)

            #trova tutte le camere associate alla prenotazione
            query = "SELECT numero_camera, tipo FROM soggiorno_camera, camera WHERE soggiorno_camera.numero_camera = camera.numero AND soggiorno_camera.id_soggiorno = {id_soggiorno}"
            query = replaceTags(query, ["{id_soggiorno}"], [str(booking_id)])
            cursor.execute(query)
            rooms = cursor.fetchall()

            
            if booking[3] != None:
                colorss = ("#D8113C", "#BA0E3F")
            else:
                colorss = ("#5FAF64", "#559B5E")if booking[1].strftime('%d/%m/%Y') == date else ("#3D85C7", "#366DAF")
            
            #visualizza dati prenotazione
            tkinter.Label(booking_label, font = self.myfont2, text = "Codice Prenotazione: " + str(booking_id) + " - inizio: " + booking[1].strftime('%d/%m/%Y') + " - fine: " + booking[2].strftime('%d/%m/%Y'), fg = "white", bg = colorss[0]).pack()

            #Clienti
            tkinter.Label(booking_label, bg = "#D1D1D1",font = self.myfont, text = ("Clienti(" + str(len(clients)) + ")" if len(clients) > 1 else "Cliente"), fg = "#262626").pack()
            table, cols = labelTable(booking_label, ("  id  ", " nazionalità ", "     nome    ", "     cognome     ", "                             email                             ", "            cellulare            "), colors = colorss)
            for c in clients: 
                labelTableInsert(cols, c)
            table.pack()

            tkinter.Label(booking_label, bg = "#D1D1D1",font = self.myfont, text = ("Camere(" + str(len(rooms)) if len(rooms) > 1 else "Camera"), fg = "#262626").pack()
            tabler, cols = labelTable(booking_label, ("   numero   ", "      tipo      "), colors = colorss)
            for r in rooms: 
                labelTableInsert(cols, r)
            tabler.pack(pady = 5)

            #tkinter.Label(booking_label,text="Registra check in (formato: aa/mm/gg ore:minuti)\nLasciare vuoto per registrare data e ora correnti)", font = self.myfont,bg = "#D1D1D1", fg = "#262626").pack()
            

            button_r = tkinter.Button(booking_label,text ="registra check in", state = (tkinter.DISABLED if date != booking[1].strftime('%d/%m/%Y') or booking[3] != None else tkinter.NORMAL))
            button_r.pack()
            #button_r.config(command = lambda: self.recordCheckin(1, entry.get()))
            exec("button_r.config(command = lambda: recordCheckin(" + str(booking_id) + "))" , )


            
            tkinter.Label(booking_label,text="Prenotazione effettuata in data " + booking[0].strftime('%d/%m/%Y') +(", annullata in data: " + booking[3].strftime('%d/%m/%Y')  if booking[3] != None else ""), font = self.myfont,bg = "#D1D1D1", fg = "#262626").pack()
            
            #self.pages[0].append(tkinter.Label(self.window, text = "", bg = "#E5E5E5", font = self.myfont1))
            
            booking_label.pack()
            tkinter.Label(self.cframes[0],text=" ", bg = "#F0F0F0").pack()
            

            #self.switch_to_page(0)

    # --- ACTIVE STAYS --- #
    def refreshActiveStays(self):
        filter_id = self.searchEntry1.get()
        filt = True
        try:
            filter_id = int(filter_id)
        except:
            filt = False
            
        self.clearPage(1, 0)
        if filt:
            cursor.execute("SELECT id FROM Soggiorno WHERE id = " + str(filter_id) +" AND check_in IS NOT NULL AND check_out IS NULL ORDER BY data_fine")
        else:
            cursor.execute("SELECT id FROM Soggiorno WHERE check_in IS NOT NULL AND check_out IS NULL ORDER BY data_fine")
        self.a_stays = cursor.fetchall()
        
        fixList(self.a_stays)
        #print("soggiorni attivi:",self.a_stays)


        self.activeStaysLabels()
            
        self.canvases[1].configure(scrollregion = self.canvases[1].bbox("all"))


    def activeStaysLabels(self):
        cursor.execute("SELECT NOW()")
        date = cursor.fetchone()[0].strftime("%d/%m/%Y")
        for stay_id in self.a_stays:
            stay_label = tkinter.Frame(self.cframes[1], bg = "#D1D1D1")

            #estrai id della soggiorno e trova le altre informazioni su di esso
            #booking_id = self.booking[self.booking_index]
            cursor.execute("SELECT data_prenotazione, data_inizio, data_fine, colazione, pranzo, cena, servizio_in_camera FROM Soggiorno WHERE Soggiorno.id = " + str(stay_id))
            stay = cursor.fetchone()

            #trova tutti i clienti associati al soggiorno
            query = "SELECT id_cliente, nazionalità,nome, cognome, email, cellulare FROM soggiorno_cliente, cliente WHERE soggiorno_cliente.id_cliente = cliente.id AND soggiorno_cliente.id_soggiorno = {id_soggiorno}"
            query = replaceTags(query, ["{id_soggiorno}"], [str(stay_id)])
            cursor.execute(query)
            clients = cursor.fetchall()

            #trova tutte le camere associate al soggiorno
            query = "SELECT numero_camera, tipo FROM soggiorno_camera, camera WHERE soggiorno_camera.numero_camera = camera.numero AND soggiorno_camera.id_soggiorno = {id_soggiorno}"
            query = replaceTags(query, ["{id_soggiorno}"], [str(stay_id)])
            cursor.execute(query)
            rooms = cursor.fetchall()
            
            
            #visualizza dati soggiorno
            tkinter.Label(stay_label, font = self.myfont2, text = "Codice Soggiorno: " + str(stay_id) + " - inizio: " + stay[1].strftime('%d/%m/%Y') + " - fine: " + stay[2].strftime('%d/%m/%Y'), fg = "white", bg = "#5FAF64").pack()
            
            #Clienti
            tkinter.Label(stay_label, bg = "#D1D1D1",font = self.myfont, text = ("Clienti(" + str(len(clients)) + ")" if len(clients) > 1 else "Cliente"), fg = "#262626").pack()
            table, cols = labelTable(stay_label, ("  id  ", " nazionalità ", "     nome    ", "     cognome     ", "                             email                             ", "            cellulare            "))
            for c in clients: 
                labelTableInsert(cols, c)
            table.pack()

            #Stanze
            tkinter.Label(stay_label, bg = "#D1D1D1",font = self.myfont, text = ("Camere(" + str(len(rooms)) if len(rooms) > 1 else "Camera"), fg = "#262626").pack()
            tabler, cols = labelTable(stay_label, ("   numero   ", "      tipo      "))
            for r in rooms: 
                labelTableInsert(cols, r)
            tabler.pack(pady = 5)


            #Servizi
            tkinter.Label(stay_label, bg = "#D1D1D1",font = self.myfont, text = "Servizi aggiuntivi", fg = "#262626").pack()
            tables, cols = labelTable(stay_label, ("      colazione      ", "         pranzo         ", "          cena          ", "servizio in camera"))
            labelTableInsert(cols, (("" if stay[3] else "non ")+"acquistato", ("" if stay[4] else "non ")+"acquistato",("" if stay[5] else "non ")+"acquistato",("" if stay[6] else "non ")+"acquistato"))
            tables.pack(pady=5)
            #tkinter.Label(booking_label,text="Registra check in (formato: aa/mm/gg ore:minuti)\nLasciare vuoto per registrare data e ora correnti)", font = self.myfont,bg = "#D1D1D1", fg = "#262626").pack()
            

            button_r = tkinter.Button(stay_label,text ="registra check out")
            button_r.pack()
            #button_r.config(command = lambda: self.recordCheckin(1, entry.get()))

            exec("button_r.config(command = lambda: recordCheckout(" + str(stay_id) + "))" , )


            
            tkinter.Label(stay_label,text="Prenotazione effettuata in data " + stay[0].strftime('%d/%m/%Y') , font = self.myfont,bg = "#D1D1D1", fg = "#262626").pack()
            
            #self.pages[0].append(tkinter.Label(self.window, text = "", bg = "#E5E5E5", font = self.myfont1))
            
            stay_label.pack()
            tkinter.Label(self.cframes[1],text=" ", bg = "#F0F0F0").pack()


    # --- PAST STAYS --- #
    def refreshPastStays(self):
        filter_id = self.searchEntry2.get()
        filt = True
        try:
            filter_id = int(filter_id)
        except:
            filt = False
            
        self.clearPage(2, 0)
        if filt:
            cursor.execute("SELECT id FROM Soggiorno WHERE id = " + str(filter_id) + " AND check_out IS NOT NULL ORDER BY data_fine DESC")
        else:
            cursor.execute("SELECT id FROM Soggiorno WHERE check_out IS NOT NULL ORDER BY data_fine DESC")
        self.p_stays = cursor.fetchall()
        
        fixList(self.p_stays)
        #print("soggiorni passati:",self.p_stays)


        self.pastStaysLabels()
            
        self.canvases[2].configure(scrollregion = self.canvases[2].bbox("all"))


    def pastStaysLabels(self):
        cursor.execute("SELECT NOW()")
        date = cursor.fetchone()[0].strftime("%d/%m/%Y")
        for stay_id in self.p_stays:
            stay_label = tkinter.Frame(self.cframes[2], bg = "#D1D1D1")

            #estrai id della prenotazione e trova le altre informazioni su di essa
            #booking_id = self.booking[self.booking_index]
            cursor.execute("SELECT data_prenotazione, data_inizio, data_fine, colazione, pranzo, cena, servizio_in_camera, check_out FROM Soggiorno WHERE Soggiorno.id = " + str(stay_id))
            stay = cursor.fetchone()

            #trova tutti i clienti associati alla prenotazione
            query = "SELECT id_cliente, nazionalità,nome, cognome, email, cellulare FROM soggiorno_cliente, cliente WHERE soggiorno_cliente.id_cliente = cliente.id AND soggiorno_cliente.id_soggiorno = {id_soggiorno}"
            query = replaceTags(query, ["{id_soggiorno}"], [str(stay_id)])
            cursor.execute(query)
            clients = cursor.fetchall()

            #trova tutte le camere associate alla prenotazione
            query = "SELECT numero_camera, tipo FROM soggiorno_camera, camera WHERE soggiorno_camera.numero_camera = camera.numero AND soggiorno_camera.id_soggiorno = {id_soggiorno}"
            query = replaceTags(query, ["{id_soggiorno}"], [str(stay_id)])
            cursor.execute(query)
            rooms = cursor.fetchall()
            
            
            #visualizza dati prenotazione
            tkinter.Label(stay_label, font = self.myfont2, text = "Codice Soggiorno: " + str(stay_id) + " - inizio: " + stay[1].strftime('%d/%m/%Y') + " - fine: " + stay[2].strftime('%d/%m/%Y'), fg = "white", bg = "#5FAF64").pack()
            
            #Clienti
            tkinter.Label(stay_label, bg = "#D1D1D1",font = self.myfont, text = ("Clienti(" + str(len(clients)) + ")" if len(clients) > 1 else "Cliente"), fg = "#262626").pack()
            table, cols = labelTable(stay_label, ("  id  ", " nazionalità ", "     nome    ", "     cognome     ", "                             email                             ", "            cellulare            "))
            for c in clients: 
                labelTableInsert(cols, c)
            table.pack()

            #Stanze
            tkinter.Label(stay_label, bg = "#D1D1D1",font = self.myfont, text = ("Camere(" + str(len(rooms)) if len(rooms) > 1 else "Camera"), fg = "#262626").pack()
            tabler, cols = labelTable(stay_label, ("   numero   ", "      tipo      "))
            for r in rooms: 
                labelTableInsert(cols, r)
            tabler.pack(pady = 5)


            #Servizi
            tkinter.Label(stay_label, bg = "#D1D1D1",font = self.myfont, text = "Servizi aggiuntivi", fg = "#262626").pack()
            tables, cols = labelTable(stay_label, ("      colazione      ", "         pranzo         ", "          cena          ", "servizio in camera"))
            labelTableInsert(cols, (("" if stay[3] else "non ")+"acquistato", ("" if stay[4] else "non ")+"acquistato",("" if stay[5] else "non ")+"acquistato",("" if stay[6] else "non ")+"acquistato"))
            tables.pack(pady=5)
            #tkinter.Label(booking_label,text="Registra check in (formato: aa/mm/gg ore:minuti)\nLasciare vuoto per registrare data e ora correnti)", font = self.myfont,bg = "#D1D1D1", fg = "#262626").pack()
            



            
            tkinter.Label(stay_label,text="Prenotazione effettuata in data " + stay[0].strftime('%d/%m/%Y') , font = self.myfont,bg = "#D1D1D1", fg = "#262626").pack()
            tkinter.Label(stay_label,text="Check out effettuato in data " + stay[7].strftime('%d/%m/%Y') + " alle ore " + stay[7].strftime('%H:%M:%S') , font = self.myfont,bg = "#D1D1D1", fg = "#262626").pack()
            
            #self.pages[0].append(tkinter.Label(self.window, text = "", bg = "#E5E5E5", font = self.myfont1))
            
            stay_label.pack()
            tkinter.Label(self.cframes[2],text=" ", bg = "#F0F0F0").pack()

            
    # --- ROOMS --- #
    def refreshRooms(self):
        self.clearPage(3)
        cursor.execute("SELECT numero, tipo, bagno, balcone FROM Camera c WHERE EXISTS(SELECT id_soggiorno FROM Soggiorno, Soggiorno_Camera WHERE Soggiorno.id = Soggiorno_Camera.id_soggiorno AND numero_camera = c.numero AND Soggiorno.data_annullamento IS NULL AND Soggiorno.check_in IS NOT NULL AND Soggiorno.check_out IS NULL)")
        self.rooms_o = cursor.fetchall()
        cursor.execute("SELECT numero, tipo, bagno, balcone FROM Camera c WHERE NOT EXISTS(SELECT id_soggiorno FROM Soggiorno, Soggiorno_Camera WHERE Soggiorno.id = Soggiorno_Camera.id_soggiorno AND numero_camera = c.numero AND Soggiorno.data_annullamento IS NULL AND Soggiorno.check_in IS NOT NULL AND Soggiorno.check_out IS NULL)")
        self.rooms_f = cursor.fetchall()
        self.roomLabels()
        reg = self.canvases[3].bbox("all")
        #print("reg:", reg)
        
        self.canvases[3].configure(scrollregion = reg)
        


    def roomLabels(self):
        tkinter.Label(self.cframes[3], font = self.myfont, text = "Camere attualmente occupate", bg = "#F0F0F0").pack()
        table, cols = labelTable(self.cframes[3], ("   numero   ", "      tipo      ", "      bagno      ", "      balcone      "))
        for r in self.rooms_o:
            row = (r[0], r[1], "presente" if r[2] == 1 else "assente", "presente" if r[3] == 1 else "assente")
            labelTableInsert(cols, row)
        table.pack()
        
        tkinter.Label(self.cframes[3], font = self.myfont, text = "Camere attualmente libere", bg = "#F0F0F0").pack()
        table, cols = labelTable(self.cframes[3], ("   numero   ", "      tipo      ", "      bagno      ", "      balcone      "))
        for r in self.rooms_f:
            row = (r[0], r[1], "presente" if r[2] == 1 else "assente", "presente" if r[3] == 1 else "assente")
            labelTableInsert(cols, row)
        table.pack()
        

    # --- Clients --- #
    def refreshClients(self):
        filter_id = self.searchEntry4.get()
        filt = True
        try:
            filter_id = int(filter_id)
        except:
            filt = False
            
        self.clearPage(4)
        if filt:
            cursor.execute("SELECT id, nazionalità, nome, cognome, genere, email, cellulare, data_di_nascita FROM Cliente c WHERE id = "+ str(filter_id) +" AND EXISTS(SELECT id_soggiorno FROM Soggiorno, Soggiorno_Cliente WHERE Soggiorno.id = Soggiorno_Cliente.id_soggiorno AND id_cliente = c.id AND check_in IS NOT NULL AND check_out IS NULL)")
        else:
            cursor.execute("SELECT id, nazionalità, nome, cognome, genere, email, cellulare, data_di_nascita FROM Cliente c WHERE EXISTS(SELECT id_soggiorno FROM Soggiorno, Soggiorno_Cliente WHERE Soggiorno.id = Soggiorno_Cliente.id_soggiorno AND id_cliente = c.id AND check_in IS NOT NULL AND check_out IS NULL)")
        self.clients_in = cursor.fetchall()

        if filt:
            cursor.execute("SELECT id, nazionalità, nome, cognome, genere, email, cellulare, data_di_nascita FROM Cliente c WHERE id = " + str(filter_id) +" AND NOT EXISTS(SELECT id_soggiorno FROM Soggiorno, Soggiorno_Cliente WHERE Soggiorno.id = Soggiorno_Cliente.id_soggiorno AND id_cliente = c.id AND check_in IS NOT NULL AND check_out IS NULL)")
        else:
            cursor.execute("SELECT id, nazionalità, nome, cognome, genere, email, cellulare, data_di_nascita FROM Cliente c WHERE NOT EXISTS(SELECT id_soggiorno FROM Soggiorno, Soggiorno_Cliente WHERE Soggiorno.id = Soggiorno_Cliente.id_soggiorno AND id_cliente = c.id AND check_in IS NOT NULL AND check_out IS NULL)")
        self.clients_out = cursor.fetchall()

        

        self.clientLabels()
        self.canvases[4].configure(scrollregion =  self.canvases[4].bbox("all"))

    def clientLabels(self):
        tkinter.Label(self.cframes[4], font = self.myfont, text = "Clienti attualmente in soggiorno", bg = "#F0F0F0").pack()
        table, cols = labelTable(self.cframes[4], ("   id   ", " nazionalità ", "         nome         ", "      cognome      ", "        genere        ", "                               email                               ", "         cellulare         ", "data di nascita"))
        for c in self.clients_in:
            row = list(c)
            row[-1] = row[-1].strftime('%d/%m/%Y')
            labelTableInsert(cols, row)
        table.pack(anchor = "w")
        
        tkinter.Label(self.cframes[4], font = self.myfont, text = "Clienti passati", bg = "#F0F0F0").pack()
        table, cols = labelTable(self.cframes[4], ("   id   ", " nazionalità ", "         nome         ", "      cognome      ", "        genere        ", "                               email                               ", "         cellulare         ", "data di nascita"))
        for c in self.clients_out:
            row = list(c)
            row[-1] = row[-1].strftime('%d/%m/%Y')
            labelTableInsert(cols, row)
        table.pack(anchor = "w")

    # --- PAYMENTS --- #
    def refreshPayments(self):
        filter_id = self.searchEntry5.get()
        filt = True
        try:
            filter_id = int(filter_id)
        except:
            filt = False
            
        self.clearPage(5)
        if filt:
            cursor.execute("SELECT id_soggiorno, importo FROM Pagamento WHERE id_soggiorno = " + str(filter_id) + " AND data_e_ora IS NULL")
        else:
            cursor.execute("SELECT id_soggiorno, importo FROM Pagamento WHERE data_e_ora IS NULL")
        self.paym_pending = cursor.fetchall()

        if filt:
            cursor.execute("SELECT id_soggiorno, id_cliente, importo, data_e_ora FROM Pagamento WHERE id_soggiorno = " + str(filter_id) +" AND data_e_ora IS NOT NULL")
        else:
            cursor.execute("SELECT id_soggiorno, id_cliente, importo, data_e_ora FROM Pagamento WHERE data_e_ora IS NOT NULL")
        self.paym_done = cursor.fetchall()

        self.paymentLabels()
        self.canvases[5].configure(scrollregion =  self.canvases[5].bbox("all"))


    def paymentLabels(self):
        tkinter.Label(self.cframes[5], font = self.myfont, text = "Soggiorni ancora non pagati", bg = "#F0F0F0").pack()
        table, cols = labelTable(self.cframes[5], ("codice soggiorno", "importo", "         registra         "))
        for p in self.paym_pending:
            row = list(p)
            row[1] = str(row[1])+"€"
            labelTableInsert(cols, row)
            
            but = tkinter.Button(cols[-1], text = "registra", image = photo)
            exec("but.config(command = lambda: recordPayment(" + str(row[0]) + "))")
            but.pack()
        table.pack()

        tkinter.Label(self.cframes[5], font = self.myfont, text = "Pagamenti passati", bg = "#F0F0F0").pack()
        table, cols = labelTable(self.cframes[5], ("codice soggiorno", "id cliente associato","importo", "data e ora pagamento"))
        for p in self.paym_done:
            row = list(p)
            row[2] = str(row[2])+"€"
            row[-1] = row[-1].strftime("%d/%m/%Y %H:%M:%S")
            labelTableInsert(cols, row)
            

        table.pack()


    # --- MAIDS --- #
    def refreshMaids(self):
        self.clearPage(6)
        cursor.execute("SELECT codice_fiscale, nazionalità, nome, cognome, genere, email, cellulare, data_di_nascita, data_assunzione, data_dismissione, numero_servizi FROM Cameriere")
        self.maids = cursor.fetchall()

        self.maidLabels()
        self.canvases[6].configure(scrollregion =  self.canvases[6].bbox("all"))


    def maidLabels(self):
        table, cols = labelTable(self.cframes[6], ("         codice fiscale         ", " nazionalità ", "         nome         ", "      cognome      ", "        genere        ", "                                    email                                    ", "         cellulare         ", "data di nascita", "data assunzione", "data dismissione", "numero di servizi"))
        for m in self.maids:
            row = list(m)
            row[-2] = row[-2].strftime('%d/%m/%Y') if row[-2] != None else "-"
            row[-3] = row[-3].strftime('%d/%m/%Y')
            row[-4] = row[-4].strftime('%d/%m/%Y')
            labelTableInsert(cols, row)
        table.pack(anchor = "w")


    # --- SERVICES --- #
    def refreshServices(self):
        self.clearPage(7)
        cursor.execute("SELECT Servizio_Cameriere.id, codice_cameriere, nome, cognome, tipo, numero_camera, data_e_ora FROM Servizio_Cameriere, Cameriere WHERE Servizio_Cameriere.codice_cameriere = Cameriere.codice_fiscale ORDER BY data_e_ora DESC")
        self.services = cursor.fetchall()

        self.serviceLabels()
        self.canvases[7].configure(scrollregion =  self.canvases[7].bbox("all"))

    def serviceLabels(self):
        table, cols = labelTable(self.cframes[7], ("id servizio", "         codice fiscale         ", "         nome         ", "      cognome      ", "        servizio svolto        ", "camera interessata", "         data e ora         "))
        for s in self.services:
            row = list(s)
            row[-1] = row[-1].strftime("%d/%m/%Y %H:%M:%S")
            row[5] = "-" if row[5] == None else row[5]
            labelTableInsert(cols, row)
        table.pack(anchor = "w")


    # --- SALARIES --- #
    def refreshSalaries(self, showall = True):
        filter_date = self.searchEntry8.get_date().strftime("%Y/%m/%d")
        self.clearPage(8)
        if showall:
            cursor.execute("SELECT id, codice_cameriere, nome, cognome, retribuzione, data FROM Stipendio_Cameriere, Cameriere WHERE Cameriere.codice_fiscale = Stipendio_Cameriere.codice_cameriere")
        else:
            cursor.execute("SELECT id, codice_cameriere, nome, cognome, retribuzione, data FROM Stipendio_Cameriere, Cameriere WHERE data = '"+ filter_date +"' AND Cameriere.codice_fiscale = Stipendio_Cameriere.codice_cameriere")
        self.salaries = cursor.fetchall()
        self.salaryLabels()
        self.canvases[8].configure(scrollregion =  self.canvases[8].bbox("all"))

    def salaryLabels(self):
        table, cols = labelTable(self.cframes[8], ("id stipendio", "         codice fiscale         ", "         nome         ", "      cognome      ", "        retribuzione        ", "         data         "))
        for s in self.salaries:
            row = list(s)
            row[-1] = row[-1].strftime("%d/%m/%Y")
            row[-2] = str(row[-2]) + "€"
            labelTableInsert(cols, row)
        table.pack(anchor = "w")


checkExpiredBooking()
gui = HotelGUI()
gui.start()

mydb.commit()
cursor.close()
mydb.close()

















