-- Lista av logiska adresser som inte ingår i någon anropsbehörighet
-- OBS, detta kan vara ok om standardbehörighet används

SELECT
    la.id,
    la.hsaId,
    la.beskrivning
FROM
    LogiskAdress la
WHERE
    la.deleted = 0
    AND la.id NOT IN (
        SELECT
           ab.logiskAdress_id
        FROM
           Anropsbehorighet ab
        WHERE
            ab.deleted = 0
        )
;