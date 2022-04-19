--

SELECT
    comp.id,
    comp.hsaId,
    comp.beskrivning
FROM
    Tjanstekomponent comp
WHERE
    comp.deleted = 0
    AND comp.id NOT IN (
        SELECT
           ad.tjanstekomponent_id
        FROM
            Vagval vv,
            AnropsAdress ad
        WHERE
            ad.id = vv.anropsAdress_id
            AND vv.deleted = 0
            AND ad.deleted = 0
        )
    AND comp.id NOT IN (
        SELECT
            ab.tjanstekonsument_id
        FROM
            Anropsbehorighet ab
        WHERE
            ab.deleted = 0
    )