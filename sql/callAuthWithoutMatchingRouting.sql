-- "authorization_without_a_matching_routing",
-- "Anropsbehörigheter till icke existerande vägval",

SELECT DISTINCT
    ab.id AS 'Anropsbehorighet ID',
    comp.hsaId AS 'Tjänstekonsument HSA-id',
    comp.beskrivning AS 'Tjänstekonsument beskrivning',
    la.hsaId AS 'Logisk adress',
    la.beskrivning AS 'Logisk adress beskrivning',
    tk.namnrymd AS 'Tjänstekontrakt namnrymd'
FROM
    Anropsbehorighet ab,
    LogiskAdress la,
    Tjanstekomponent comp,
    Tjanstekontrakt tk
WHERE
    ab.id = 1652 and

    ab.deleted IS NOT NULL
  AND ab.tomTidpunkt > CURDATE()
  AND ab.logiskAdress_id = la.id
  AND la.hsaId <> '*'
  AND la.hsaId <> 'SE'
  AND ab.tjanstekonsument_id = comp.id
  AND ab.tjanstekontrakt_id = tk.id
  AND la.id NOT IN (
    SELECT vv.logiskAdress_id
    FROM Vagval vv
    WHERE
        vv.deleted IS NOT NULL
      AND vv.tomTidpunkt > CURDATE()
      AND vv.tjanstekontrakt_id = ab.tjanstekontrakt_id
      AND vv.logiskAdress_id = ab.logiskAdress_id
)
ORDER BY ab.id
;