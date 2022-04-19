SELECT DISTINCT
    aa.id,
    aa.adress
FROM
    AnropsAdress aa
WHERE
    aa.deleted IS NOT NULL
    AND aa.id NOT IN (
        SELECT
           vv.anropsAdress_id
        FROM Vagval vv
        WHERE
            vv.deleted IS NOT NULL
    )
ORDER BY aa.adress