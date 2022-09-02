-- Operazione 1 (ESEMPIO)
INSERT INTO soggiorno(data_prenotazione , data_inizio, data_fine, colazione, pranzo, cena, servizio_in_camera) VALUES
("2022/05/15", "2022/08/02", "2022/08/09", false, false, false, false);


-- Operazione 2 (ESEMPIO)
INSERT INTO soggiorno_cliente VALUES(1, 2);


-- Operazione 3 (ESEMPIO)
INSERT INTO soggiorno_camera VALUES(4, 1);


-- Operazione 4 (nel file trigger e procedure.sql)
-- Operazione 5 (nel file trigger e procedure.sql)
-- Operazione 6 (nel file trigger e procedure.sql)

-- Operazione 7
SELECT Soggiorno_Cliente.id_soggiorno, SoggiornoCliente.id_cliente
FROM Soggiorno_Cliente, Soggiorno
WHERE Soggiorno_Cliente.id_soggiorno = Soggiorno.id  AND Soggiorno.data_annullamento IS NULL
AND (Soggiorno.check_in IS NOT NULL AND Soggiorno.check_out IS NULL) 
OR (Soggiorno.check_in = false)


-- Operazione 8
SELECT numero, tipo, bagno, balcone 
FROM Camera WHERE EXISTS(
    SELECT id_soggiorno 
    FROM Soggiorno, Soggiorno_Camera 
    WHERE Soggiorno.id = Soggiorno_Camera.id_soggiorno AND Soggiorno.data_annullamento IS NULL 
    AND Soggiorno.check_in IS NOT NULL AND Soggiorno.check_out IS NULL
)


-- Operazione 9
SELECT Soggiorno.id
FROM Soggiorno, Pagamento
WHERE Soggiorno.id = Pagamento.id_soggiorno AND Soggiorno.check_in IS NOT NULL AND Pagamento.data IS NULL


-- Operazione 11 (nel file trigger e procedure.sql)


-- Operazione 12
UPDATE Soggiorno
SET data_annullamento = CURDATE() 
WHERE data_annullamento IS NULL 
AND check_in IS NULL 
AND check_out IS NULL 
AND CURDATE() > data_inizio


-- Operazione 13 (ESEMPIO)
INSERT INTO Servizio_Cameriere() VALUES("BNTVGL78E48D612Z", "pulizia camera", 3, NOW())


-- Operazione 14 (ESEMPIO)
SELECT numero_servizi FROM Cameriere WHERE codice_fiscale = "BNTVGL78E48D612Z"


-- Operazione 15 (nel file trigger e procedure.sql)

