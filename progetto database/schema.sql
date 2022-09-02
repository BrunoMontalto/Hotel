DROP DATABASE IF EXISTS Hotel;
CREATE SCHEMA Hotel;
USE Hotel;

DROP TABLE IF EXISTS Cliente;
CREATE TABLE Cliente(
    id bigint NOT NULL AUTO_INCREMENT,
    nome varchar(32) NOT NULL,
    cognome varchar(32) NOT NULL,
    genere ENUM("maschio", "femmina", "non specificato") NOT NULL,
    email varchar(128) NOT NULL,
    cellulare varchar(20),
    data_di_nascita date NOT NULL,
    nazionalità varchar(16),

    PRIMARY KEY(id)
);

DROP TABLE IF EXISTS Camera;
CREATE TABLE Camera(
    numero smallint NOT NULL,
    tipo ENUM("singola", "doppia", "tripla", "quadrupla") NOT NULL,
    bagno boolean,
    balcone boolean,

    PRIMARY KEY(numero)
);

DROP TABLE IF EXISTS Soggiorno;
CREATE TABLE Soggiorno(
    id bigint NOT NULL AUTO_INCREMENT,

    data_prenotazione date NOT NULL,
    data_annullamento date,

    data_inizio date NOT NULL,
    data_fine date NOT NULL,
    check_in datetime,
    check_out datetime,

    colazione boolean NOT NULL,
    pranzo boolean NOT NULL,
    cena boolean NOT NULL,
    servizio_in_camera boolean NOT NULL,

    

    PRIMARY KEY(id)
);

DROP TABLE IF EXISTS Soggiorno_Cliente;
CREATE TABLE Soggiorno_Cliente(
    id_soggiorno bigint NOT NULL,
    id_cliente bigint NOT NULL,

    FOREIGN KEY(id_soggiorno) REFERENCES Soggiorno(id),
    FOREIGN KEY(id_cliente) REFERENCES Cliente(id),
    PRIMARY KEY(id_soggiorno, id_cliente)
);

DROP TABLE IF EXISTS Soggiorno_Camera;
CREATE TABLE Soggiorno_Camera(
    id_soggiorno bigint NOT NULL,
    numero_camera smallint NOT NULL,

    FOREIGN KEY(id_soggiorno) REFERENCES Soggiorno(id),
    FOREIGN KEY(numero_camera) REFERENCES Camera(numero),
    PRIMARY KEY(id_soggiorno, numero_camera)
);

    
DROP TABLE IF EXISTS Pagamento;
CREATE TABLE Pagamento(
	id_soggiorno bigint NOT NULL,
    id_cliente bigint,
    importo int NOT NULL,
    data_e_ora datetime,

    PRIMARY KEY(id_soggiorno),
    FOREIGN KEY(id_soggiorno) REFERENCES Soggiorno(id),
    FOREIGN KEY(id_cliente) REFERENCES Cliente(id)
);

DROP TABLE IF EXISTS Cameriere;
CREATE TABLE Cameriere(
    codice_fiscale varchar(16) NOT NULL,
    nome varchar(16) NOT NULL,
    cognome varchar(16) NOT NULL,
    genere ENUM("maschio", "femmina", "non specificato") NOT NULL,
    email varchar(128) NOT NULL,
    cellulare varchar(20),
    data_di_nascita date NOT NULL,
    nazionalità varchar(16) NOT NULL,
    
    data_assunzione date NOT NULL,
    data_dismissione date,

    numero_servizi int NOT NULL DEFAULT 0,

    PRIMARY KEY(codice_fiscale)
);

DROP TABLE IF EXISTS Servizio_Cameriere;
CREATE TABLE Servizio_Cameriere(
    id int NOT NULL AUTO_INCREMENT,
    codice_cameriere varchar(16) NOT NULL,
    tipo ENUM("pulizia camera", "servizio in camera", "lavanderia") NOT NULL,
    numero_camera smallint,
    data_e_ora datetime NOT NULL,

    PRIMARY KEY(id),
    FOREIGN KEY(codice_cameriere) REFERENCES Cameriere(codice_fiscale),
    FOREIGN KEY(numero_camera) REFERENCES Camera(numero)
);

DROP TABLE IF EXISTS Stipendio_Cameriere;
CREATE TABLE Stipendio_Cameriere(
    id int NOT NULL AUTO_INCREMENT,
    codice_cameriere varchar(16) NOT NULL,
    retribuzione int NOT NULL,
    data date NOT NULL,

    PRIMARY KEY(id),
    FOREIGN KEY(codice_cameriere) REFERENCES Cameriere(codice_fiscale)
);

DROP TABLE IF EXISTS Prezzo_Camera_Stagione;
CREATE TABLE Prezzo_Camera_Stagione(
	stagione ENUM("bassa", "media", "alta") NOT NULL,
	singola int NOT NULL,
	doppia int NOT NULL,
	tripla int NOT NULL,
	quadrupla int NOT NULL,

	PRIMARY KEY(stagione)
);

INSERT INTO Prezzo_Camera_Stagione(stagione, singola, doppia, tripla, quadrupla) VALUES
("bassa", 40, 60, 70, 85),
("media", 70, 100, 110, 140),
("alta", 90, 130, 145, 185);


DROP TABLE IF EXISTS Prezzo_Servizi;
CREATE TABLE Prezzo_Servizi(
	servizio ENUM("colazione", "pranzo", "cena", "servizio in camera") NOT NULL,
	prezzo int NOT NULL,

	PRIMARY KEY(servizio)
);

INSERT INTO Prezzo_Servizi(servizio, prezzo) VALUES
("colazione", 10),
("pranzo", 30),
("cena", 30),
("servizio in camera", 4);



















