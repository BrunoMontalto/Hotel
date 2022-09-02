-- TRIGGERS

-- Operazione 11
DROP TRIGGER IF EXISTS Calcola_Conto_Soggiorno;
DELIMITER $$
CREATE TRIGGER Calcola_Conto_Soggiorno AFTER UPDATE ON Soggiorno 
FOR EACH ROW
BEGIN
    DECLARE conto int;
    DECLARE numero_singole int;
    DECLARE numero_doppie int;
    DECLARE numero_triple int;
    DECLARE numero_quadruple int;
    DECLARE stag ENUM("bassa", "media", "alta");
    

    IF (NEW.check_in IS NOT NULL AND NEW.check_out IS NULL AND NEW.data_annullamento IS NULL) THEN
        SET numero_singole = (SELECT COUNT(*) FROM Soggiorno_Camera, Camera WHERE Soggiorno_Camera.numero_camera = Camera.numero AND Soggiorno_Camera.id_soggiorno = New.id AND Camera.tipo = "singola");
        
        SET numero_doppie = (SELECT COUNT(*) FROM Soggiorno_Camera, Camera WHERE Soggiorno_Camera.numero_camera = Camera.numero AND Soggiorno_Camera.id_soggiorno = New.id AND Camera.tipo = "doppia");
        SET numero_triple = (SELECT COUNT(*) FROM Soggiorno_Camera, Camera WHERE Soggiorno_Camera.numero_camera = Camera.numero AND Soggiorno_Camera.id_soggiorno = New.id AND Camera.tipo = "tripla");
        SET numero_quadruple = (SELECT COUNT(*) FROM Soggiorno_Camera, Camera WHERE Soggiorno_Camera.numero_camera = Camera.numero AND Soggiorno_Camera.id_soggiorno = New.id AND Camera.tipo = "quaadrupla");

        
        IF (MONTH(NEW.data_inizio) IN (1, 2, 8) )THEN
            SET stag = "bassa";
        END IF;
        IF (MONTH(NEW.data_inizio) IN (3, 7, 11, 12) )THEN
            SET stag = "media";
        END IF;
        IF (MONTH(NEW.data_inizio) IN (4, 5, 6, 9 , 10) )THEN
            SET stag = "alta";
        END IF;
        
        

        
        SET conto = (DATEDIFF(New.data_fine, NEW.data_inizio) * (
          numero_singole * (SELECT singola FROM Prezzo_Camera_Stagione WHERE stagione = stag) 
        + numero_doppie * (SELECT doppia FROM Prezzo_Camera_Stagione WHERE stagione = stag) 
        + numero_triple * (SELECT tripla FROM Prezzo_Camera_Stagione WHERE stagione = stag) 
        + numero_quadruple * (SELECT quadrupla FROM Prezzo_Camera_Stagione WHERE stagione = stag) 
        + NEW.colazione * (SELECT prezzo FROM Prezzo_Servizi WHERE servizio = "colazione")
        + NEW.pranzo * (SELECT prezzo FROM Prezzo_Servizi WHERE servizio = "pranzo")
        + NEW.cena * (SELECT prezzo FROM Prezzo_Servizi WHERE servizio = "cena")
        + NEW.servizio_in_camera * (SELECT prezzo FROM Prezzo_Servizi WHERE servizio = "servizio in camera") * (numero_singole + numero_doppie + numero_triple + numero_quadruple)

        ));

        INSERT INTO Pagamento(id_soggiorno, importo) VALUES (New.id, conto);
    END IF;
END$$
DELIMITER ;


-- Si collega alle operazioni 13 e 14
DROP TRIGGER IF EXISTS Aggiorna_Numero_Servizi_Cameriere;
DELIMITER $$
CREATE TRIGGER Aggiorna_Numero_Servizi_Cameriere AFTER INSERT ON Servizio_Cameriere
FOR EACH ROW
BEGIN
    UPDATE Cameriere
    SET numero_servizi = numero_servizi + 1
    WHERE codice_fiscale = NEW.codice_cameriere;
END$$
DELIMITER ;


DROP TRIGGER IF EXISTS Verifica_Sovrapposizione_Prenotazioni;
DELIMITER $$
CREATE TRIGGER Verifica_Sovrapposizione_Prenotazioni BEFORE INSERT ON Soggiorno
FOR EACH ROW
BEGIN
    DECLARE ids bigint;
    SET ids = (
        SELECT id FROM Soggiorno s
        WHERE s.data_annullamento IS NULL AND s.data_inizio <= NEW.data_fine AND s.data_fine >= NEW.data_inizio
        AND EXISTS(
            SELECT numero_camera FROM Soggiorno_Camera 
            WHERE Soggiorno_Camera.id_soggiorno = NEW.id
            AND numero_camera in (
                SELECT numero_camera AS nc FROM Soggiorno_Camera
                WHERE Soggiorno_Camera.id_soggiorno = s.id
            )
        )
        LIMIT 1
    );
    IF (ids IS NOT NULL) THEN
        DELETE FROM Soggiorno WHERE id = NEW.id;
    END IF;
END$$
DELIMITER ;


DROP TRIGGER IF EXISTS Verifica_Cliente_Un_Soggiorno_Alla_Volta;
DELIMITER $$
CREATE TRIGGER Verifica_Cliente_Un_Soggiorno_Alla_Volta AFTER INSERT ON Soggiorno_Cliente
FOR EACH ROW
BEGIN
    IF EXISTS(
        SELECT id FROM Soggiorno s
        WHERE id <> NEW.id_soggiorno AND data_annullamento IS NULL AND check_in IS NOT NULL AND check_out IS NULL
        AND EXISTS(
            SELECT id_cliente FROM Soggiorno_Cliente sc
            WHERE s.id = sc.id_soggiorno AND id_cliente = NEW.id_cliente
        )
    ) 
    THEN
        DELETE FROM Soggiorno_Cliente WHERE id_soggiorno = NEW.id_soggiorno AND id_cliente = NEW.id_cliente;
    END IF;
END$$
DELIMITER ;

-- PROCEDURE

-- Operazione 4
DROP PROCEDURE IF EXISTS Trova_Clienti_Soggiorno;
DELIMITER $$
CREATE PROCEDURE Trova_Clienti_Soggiorno(IN id_soggiorno bigint)
BEGIN
    SELECT id, nazionalità, nome, cognome, email, cellulare
    FROM Soggiorno_Cliente sc, Cliente c
    WHERE sc.id_cliente = c.id AND sc.id_soggiorno = id_soggiorno;
END $$
DELIMITER ;


-- Operazione 5
DROP PROCEDURE IF EXISTS Trova_Camere_Soggiorno;
DELIMITER $$
CREATE PROCEDURE Trova_Camere_Soggiorno(IN id_soggiorno bigint)
BEGIN
    SELECT numero_camera, tipo
    FROM Soggiorno_Camera sc, Camera c
    WHERE sc.numero_camera = c.numero AND sc.id_soggiorno = id_soggiorno;
END $$
DELIMITER ;


-- Operazione 6
DROP PROCEDURE IF EXISTS Trova_Camere_Prenotabili;
DELIMITER $$
CREATE PROCEDURE Trova_Camere_Prenotabili (IN data_inizio date, IN data_fine date, IN tipo_camera ENUM("singola", "doppia", "triple", "quadrupla"))
BEGIN

    SELECT numero FROM Camera c
    WHERE tipo = tipo_camera AND NOT EXISTS(
        SELECT numero_camera
        FROM Soggiorno s, Soggiorno_Camera sc
        WHERE s.id = sc.id_soggiorno AND sc.numero_camera = c.numero
        AND s.data_annullamento IS NULL
        AND s.data_inizio <= data_fine AND s.data_fine >= data_inizio
    );
END$$
DELIMITER ;


-- Operazione 15
DROP FUNCTION IF EXISTS Calcola_Profitto;
DELIMITER $$
CREATE FUNCTION Calcola_Profitto(dalla_data date, alla_data date)
RETURNS INT
BEGIN
    RETURN(
        SELECT entrate - uscite 
        FROM (SELECT SUM(Pagamento.importo) AS entrate FROM Pagamento WHERE CAST(Pagamento.data_e_ora as date) BETWEEN dalla_data AND alla_data) a,
        (SELECT SUM(Stipendio_Cameriere.retribuzione) AS uscite FROM Stipendio_Cameriere WHERE Stipendio_Cameriere.data BETWEEN dalla_data AND alla_data)b
    );
END$$
DELIMITER ;
