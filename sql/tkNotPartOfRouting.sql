-- Lista av tjänstekontrakt som inte ingår i något vägval

SELECT
    tk.id,
    tk.namnrymd
FROM
    Tjanstekontrakt tk
WHERE
    tk.deleted = 0
    AND tk.id NOT IN (
        SELECT
           vv.tjanstekontrakt_id
        FROM
           Vagval vv
        WHERE
            vv.deleted = 0
        )
;