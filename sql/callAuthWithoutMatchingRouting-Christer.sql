SELECT DISTINCT
    -- A.id AS 'Id',
    -- A.integrationsavtal AS 'Integrationsavtal',
    TK.hsaId AS 'Tjänstekonsument',
    T.namnrymd AS 'Tjänstekontrakt',
    L.hsaId AS 'Logisk adress'
    -- A.fromTidpunkt AS 'Fr.o.m tidpunkt',
    -- A.tomTidpunkt AS 'T.o.m tidpunkt'
FROM
    Anropsbehorighet A
        LEFT JOIN Vagval V ON (A.tjanstekontrakt_id = V.tjanstekontrakt_id AND A.logiskAdress_id = V.logiskAdress_id AND V.deleted IS NOT NULL),
    LogiskAdress L,
    Tjanstekomponent TK,
    Tjanstekontrakt T
WHERE
    V.tjanstekontrakt_id IS NULL
  AND A.deleted IS NOT NULL
  AND A.logiskAdress_id = L.id
  AND A.tjanstekonsument_id = TK.id
  AND A.tjanstekontrakt_id = T.id
ORDER BY A.id;