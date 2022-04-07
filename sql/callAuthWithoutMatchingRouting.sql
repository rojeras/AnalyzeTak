SELECT DISTINCT
    -- A.id AS 'Id',
    -- A.integrationsavtal AS 'Integrationsavtal',
    comp.hsaId AS 'Tjänstekonsument',
    tk.namnrymd AS 'Tjänstekontrakt',
    la.hsaId AS 'Logisk adress'
    -- A.fromTidpunkt AS 'Fr.o.m tidpunkt',
    -- A.tomTidpunkt AS 'T.o.m tidpunkt'
FROM
    Anropsbehorighet ab,
    LogiskAdress la,
    Tjanstekomponent comp,
    Tjanstekontrakt tk
WHERE
  ab.deleted IS NOT NULL
  AND ab.logiskAdress_id = la.id
  AND ab.tjanstekonsument_id = comp.id
  AND ab.tjanstekontrakt_id = tk.id
  AND la.id NOT IN (
      SELECT vv.logiskAdress_id
      FROM Vagval vv
      WHERE
        vv.tjanstekontrakt_id = ab.tjanstekontrakt_id
        AND vv.logiskAdress_id = ab.logiskAdress_id
    )
ORDER BY ab.id
;