SELECT DISTINCT vv.id            AS 'Vagval ID',
                la.hsaId         AS 'Logisk adress',
                la.beskrivning   AS 'Logisk adress beskrivning',
                tk.namnrymd      AS 'Tjänstekontrakt namnrymd',
                comp.hsaId       AS 'Tjänsteproducentens HSA-id',
                comp.beskrivning AS 'Tjänsteproducentens beskrivning'
FROM Vagval vv,
     LogiskAdress la,
     Tjanstekomponent comp,
     Tjanstekontrakt tk,
     AnropsAdress aa
WHERE vv.deleted IS NOT NULL
  AND vv.logiskAdress_id = la.id
  AND vv.anropsAdress_id = aa.id
  AND aa.tjanstekomponent_id = comp.id
  AND vv.tjanstekontrakt_id = tk.id
  AND vv.tjanstekontrakt_id NOT IN (SELECT DISTINCT ab.tjanstekontrakt_id
                                    FROM Anropsbehorighet ab,
                                         LogiskAdress la2
                                    WHERE ab.deleted IS NOT NULL
                                      AND ab.tjanstekontrakt_id = vv.tjanstekontrakt_id
                                      AND ab.logiskAdress_id = la2.id
                                      AND (
                                                ab.logiskAdress_id = vv.logiskAdress_id
                                            OR la2.hsaId =  '*'
                                            OR la2.hsaId = 'SE'))


ORDER BY vv.id
;