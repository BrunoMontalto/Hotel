import random
from codicefiscale import codicefiscale
from faker import Faker
import phonenumbers
nomi = ["Antonio", "Claudio", "Paolo", "Luca", "Andrea", "Mario", "Giovanni", "Fabio" ,"Lucia", "Chiara", "Francesca"]
cognomi = ["Rossi", "Di Stefano", "Oliveri", "Montalto", "Catania", "Lo Faro", "Platania", "Bianchi"]

citta = ["Catania", "Palermo", "Torino", "Roma", "Milano", "Firenze"]
tipocamera = ["singola","doppia","tripla","quadrupla"]
tipo_camera = ["singola","singola", "doppia","doppia","doppia", "tripla", "tripla","quadrupla","quadrupla"]

fakes = {("Italia","it_IT") : Faker("it_IT"),
            ("Stati Uniti","en_US") : Faker("en_US"),
            ("Francia","fr_FR") : Faker("fr_FR"),
            ("Spagna", "es_ES") : Faker("es_ES"),
            ("Giappone", "ja_JP") : Faker("ja_JP"),
            ("Cina","zh_CN") : Faker("zh_CN"),
            ("Germania","de") : Faker("de"),
            ("Russia","ru_RU") : Faker("ru_RU")
}

def randomdate(dd, dd2, mm, mm2, aa, aa2):
    return str(random.randint(aa, aa2)) + "/" + str(random.randint(mm, mm2)) + "/" + str(random.randint(dd, dd2))

def phonenumber(locale, fake):
    if len(locale) > 2: locale = locale[-2:]
    locale = locale.upper()
    number = fake.phone_number()
    num_obj = phonenumbers.parse(number, locale)
    
    p = phonenumbers.format_number(num_obj, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    #print("prima",p)
    if "ext." in p:
        p = p.split("ext.")[0][:-1]
    #print("dopo",p)
    return p

def cliente(n = 100):
    random.seed(0)
    res = "INSERT INTO CLIENTE(nome, cognome, genere, email, cellulare, data_di_nascita, nazionalità) VALUES\n"
    for i in range(n):
        bdate = randomdate(1,28, 1,12 ,1970, 2000)
        nationality = random.choice(list(fakes.keys()))
        gender = random.choice(['"maschio"' ,'"femmina"', '"maschio"' ,'"femmina"','"maschio"' ,'"femmina"','"non specificato"'])
        f = fakes[nationality]
        phone = phonenumber(nationality[1], f)
        if gender == '"femmina"':
            n = f.first_name_female()
        else: n = f.first_name()
        c = f.last_name()

        res += '("' + n + '", "' + c + '", ' + gender + ', "' + (f.unique.ascii_free_email() if nationality[0] in ("Giappone", "Cina", "Russia") else(n+c).lower()+"@"+f.domain_name()) + '", "' + phone + '", "' + bdate + '", "' + nationality[0] + '"),\n'


    return res[:-2] + ";"



def camera(n = 30):
    res = "INSERT INTO CAMERA(numero, tipo, bagno, balcone) VALUES\n"
    capienza_totale = 0
    for i in range(n):
        tipo = random.choice(tipo_camera)
        tipo = tipocamera.index(tipo)
        numero_letti = tipo + 1
        bagno = "true" if tipo > 0 else random.choice(["true", "true","true","false"])                
        capienza_totale += numero_letti
        
        res += '(' + str(i + 1) + ', "' + tipocamera[tipo] + '", ' + bagno + ', ' + random.choice(["true", "false"]) + '),\n'


    return res[:-2] + ";"



def cameriere(n = 16):
    res = "INSERT INTO CAMERIERE(codice_fiscale, nome, cognome, genere, email, cellulare, data_di_nascita, nazionalità, data_assunzione) VALUES\n"
    for i in range(n):
        bdate = randomdate(1,28, 1,12 ,1970, 2000)
        nationality = list(fakes.keys())[0]
        gender = random.choice(['"maschio"' ,'"femmina"', '"maschio"' ,'"femmina"','"maschio"' ,'"femmina"','"non specificato"'])
        f = fakes[nationality]
        phone = phonenumber(nationality[1], f)
        if gender == '"femmina"':
            n = f.first_name_female()
        else: n = f.first_name()
        c = f.last_name()

        res += '("' + codicefiscale.encode(c, n, ("F" if gender == '"femmina"' else "M"), bdate, random.choice(citta)) + '", "' + n + '", "' + c + '", ' + gender + ', "' + (n+c).lower()+"@"+f.domain_name() + '", "' + phone + '", "' + bdate + '", "' + nationality[0] + '", "' + randomdate(1,28, 1,12 ,2020, 2021) + '"),\n'


    return res[:-2] + ";"




while True:
    ans = input("Scegliere query da generare:\n\t1 - Clienti\n\t2 - Camere\n\t3 - Camerieri\n")
    if ans == "1":
        ans = input("Quanti clienti si desidera generare?\n")
        try:
            print(cliente(int(ans)))
        except:
            print("Errore, numero non valido.")
    elif ans == "2":
        ans = input("Quante camere si desidera generare?\n")
        try:
            print(camera(int(ans)))
        except:
            print("Errore, numero non valido.")
    elif ans == "3":
        ans = input("Quanti camerieri si desidera generare?\n")
        try:
            print(cameriere(int(ans)))
        except:
            print("Errore, numero non valido.")
    else:
        print("Inserire un numero valido!")
    print("\n")
        

