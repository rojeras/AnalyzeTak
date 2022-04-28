SELECT DISTINCT
    -- aa.id,
    -- aa.adress,
    -- tk.hsaId
    COUNT(*) AS count
FROM
    AnropsAdress aa,
    Tjanstekomponent tk
WHERE
    aa.deleted IS NOT NULL
    AND tk.deleted IS NOT NULL
    AND aa.tjanstekomponent_id = tk.id
    AND aa.id NOT IN (
        SELECT
           vv.anropsAdress_id
        FROM Vagval vv
        WHERE
            vv.deleted IS NOT NULL
    )
ORDER BY aa.adress
;