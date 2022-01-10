def createFunctions(conn, cursor, schemaName):
    cursor.execute(
        """
            CREATE OR REPLACE FUNCTION {0}.row_estimator_adm(
                objectid bigint)
                RETURNS bigint
                LANGUAGE 'sql'
                COST 100
                VOLATILE PARALLEL UNSAFE
            AS $BODY$
            SELECT count(*) FROM {0}.adm_hierarchy h WHERE h.parentobjid = $1 AND h.isactive = 1;
            $BODY$;
            ALTER FUNCTION {0}.row_estimator_adm(bigint)
                OWNER TO postgres;
            

            CREATE OR REPLACE FUNCTION {0}.row_estimator_mun(
                objectid bigint)
                RETURNS bigint
                LANGUAGE 'sql'
                COST 100
                VOLATILE PARALLEL UNSAFE
            AS $BODY$
            SELECT count(*) FROM {0}.mun_hierarchy h WHERE h.parentobjid = $1 AND h.isactive = 1;
            $BODY$;
            ALTER FUNCTION {0}.row_estimator_mun(bigint)
                OWNER TO postgres;""".format(schemaName)
    )
    conn.commit()
    cursor.execute(
        """CREATE OR REPLACE FUNCTION {0}.genealogy_adm(
            objectid integer)
            RETURNS TABLE(objectid bigint, name character varying, typename character varying, level character varying) 
            LANGUAGE 'sql'
            COST 100
            VOLATILE PARALLEL UNSAFE
            ROWS 1000
            AS $BODY$
            WITH RECURSIVE obj(objectid, name, typename, level, parentobjid) AS (
                SELECT o.objectid,
                    o.name,
                    o.typename,
                    o.level,
                    ah.parentobjid
                FROM {0}.adm_hierarchy ah
                JOIN {0}.addr_obj o ON ah.objectid = o.objectid
                WHERE o.objectid = $1 AND o.isactual = 1 AND o.isactive = 1 AND ah.isactive = 1
            UNION
                SELECT o.objectid,
                    o.name,
                    o.typename,
                    o.level,
                    ah.parentobjid
                FROM obj, {0}.adm_hierarchy ah
                JOIN {0}.addr_obj o ON ah.objectid = o.objectid
                WHERE o.isactual = 1 AND o.isactive = 1 AND ah.isactive = 1 AND obj.parentobjid = o.objectid
            )
            SELECT obj.objectid, obj.name, t.name AS typename, obj.level 
            FROM obj
            JOIN {0}.addr_obj_types t ON t.shortname = obj.typename
            WHERE t.level = obj.level::integer;
            $BODY$;
            ALTER FUNCTION {0}.genealogy_adm(integer)
                OWNER TO postgres;
            

            CREATE OR REPLACE FUNCTION {0}.genealogy_mun(
                objectid integer)
                RETURNS TABLE(objectid bigint, name character varying, typename character varying, level character varying) 
                LANGUAGE 'sql'
                COST 100
                VOLATILE PARALLEL UNSAFE
                ROWS 1000
            AS $BODY$
            WITH RECURSIVE obj(objectid, name, typename, level, parentobjid) AS (
                SELECT o.objectid,
                    o.name,
                    o.typename,
                    o.level,
                    ah.parentobjid
                FROM {0}.mun_hierarchy ah
                JOIN {0}.addr_obj o ON ah.objectid = o.objectid
                WHERE o.objectid = $1 AND o.isactual = 1 AND o.isactive = 1 AND ah.isactive = 1
            UNION
                SELECT o.objectid,
                    o.name,
                    o.typename,
                    o.level,
                    ah.parentobjid
                FROM obj, {0}.mun_hierarchy ah
                JOIN {0}.addr_obj o ON ah.objectid = o.objectid
                WHERE o.isactual = 1 AND o.isactive = 1 AND ah.isactive = 1 AND obj.parentobjid = o.objectid
            )
            SELECT obj.objectid, obj.name, t.name AS typename, obj.level 
            FROM obj
            JOIN {0}.addr_obj_types t ON t.shortname = obj.typename
            WHERE t.level = obj.level::integer;
            $BODY$;
            ALTER FUNCTION {0}.genealogy_mun(integer)
                OWNER TO postgres;
            

            CREATE OR REPLACE FUNCTION {0}.getchildren_adm(
                objectid integer)
                RETURNS TABLE(objectid bigint, name character varying, typename character varying, level integer, children bigint) 
                LANGUAGE 'sql'
                COST 100
                VOLATILE PARALLEL UNSAFE
                ROWS 1000
            AS $BODY$
                SELECT o.objectid,
                    o.name,
                    o.typename,
                    o.level::integer,
                    {0}.row_estimator_adm(o.objectid) AS children
                FROM {0}.adm_hierarchy h
                    JOIN (SELECT o.objectid,
                            o.name,
                            t.name AS typename,
                            o.level
                        FROM {0}.addr_obj o
                            JOIN {0}.addr_obj_types t ON t.shortname = o.typename
                        WHERE	t.level = o.level::integer AND o.isactual = 1 AND o.isactive = 1) o ON h.objectid = o.objectid
                WHERE h.parentobjid::text = $1::text AND h.isactive = 1
            UNION
                SELECT s.objectid,
                    s.number AS name,
                    'Земельный участок' AS typename,
                    9 AS level,
                    {0}.row_estimator_adm(s.objectid) AS children
                FROM {0}.adm_hierarchy h
                    JOIN {0}.steads s ON s.objectid = h.objectid
                WHERE h.isactive = 1 AND s.isactual = 1 AND s.isactive = 1 AND h.parentobjid::text = $1::text 
            UNION
                SELECT h.objectid,
                    h.number AS name,
                    h.typename,
                    10 AS level,
                    {0}.row_estimator_adm(h.objectid) AS children
                FROM {0}.adm_hierarchy a
                    JOIN (SELECT h.objectid,
                            (CASE
                                WHEN h.housenum IS NOT NULL AND h.addnum1 IS NULL AND h.addnum2 IS NULL THEN h.housenum
                                WHEN h.housenum IS NOT NULL AND h.addnum1 IS NOT NULL AND h.addnum2 IS NULL THEN h.housenum || '/' || h.addnum1
                                WHEN h.housenum IS NOT NULL AND h.addnum1 IS NOT NULL AND h.addnum2 IS NOT NULL THEN h.housenum || '/' || h.addnum1 || '/' || h.addnum2
                            END) AS number,
                            (CASE
                                WHEN h.housetype IS NOT NULL AND h.addtype1 IS NULL AND h.addtype2 IS NULL THEN t.name
                                WHEN h.housetype IS NOT NULL AND h.addtype1 IS NOT NULL AND h.addtype2 IS NULL THEN t.name || '/' || t1.name
                                WHEN h.housetype IS NOT NULL AND h.addtype1 IS NOT NULL AND h.addtype2 IS NOT NULL THEN t.name || '/' || t1.name || '/' || t2.name
                            END) AS typename
                        FROM {0}.houses h
                            JOIN {0}.house_types t ON t.id = h.housetype
                            LEFT JOIN {0}.house_types t1 ON t1.id = h.addtype1
                            LEFT JOIN {0}.house_types t2 ON t2.id = h.addtype2
                        WHERE h.isactual = 1 AND h.isactive = 1) h ON h.objectid = a.objectid
                WHERE a.isactive = 1 AND a.parentobjid::text = $1::text 
            ORDER BY level, name;
            $BODY$;
            ALTER FUNCTION {0}.getchildren_adm(integer)
                OWNER TO postgres;
            
            
            CREATE OR REPLACE FUNCTION {0}.getchildren_mun(
                objectid integer)
                RETURNS TABLE(objectid bigint, name character varying, typename character varying, level integer, children bigint) 
                LANGUAGE 'sql'
                COST 100
                VOLATILE PARALLEL UNSAFE
                ROWS 1000
            AS $BODY$
                SELECT o.objectid,
                    o.name,
                    o.typename,
                    o.level::integer,
                    {0}.row_estimator_mun(o.objectid)
                FROM {0}.mun_hierarchy h
                    JOIN (SELECT o.objectid,
                            o.name,
                            t.name AS typename,
                            o.level
                        FROM {0}.addr_obj o
                            JOIN {0}.addr_obj_types t ON t.shortname = o.typename
                        WHERE	t.level = o.level::integer AND o.isactual = 1 AND o.isactive = 1) o ON h.objectid = o.objectid
                WHERE h.parentobjid::text = $1::text AND h.isactive = 1
            UNION
                SELECT s.objectid,
                    s.number AS name,
                    'Земельный участок' AS typename,
                    9 AS level,
                    {0}.row_estimator_mun(s.objectid)
                FROM {0}.mun_hierarchy h
                    JOIN {0}.steads s ON s.objectid = h.objectid
                WHERE h.isactive = 1 AND  h.parentobjid::text = $1::text 
            UNION
                SELECT h.objectid,
                    h.number AS name,
                    h.typename,
                    10 AS level,
                    {0}.row_estimator_mun(h.objectid)
                FROM {0}.mun_hierarchy a
                    JOIN (SELECT h.objectid,
                            (CASE
                                WHEN h.housenum IS NOT NULL AND h.addnum1 IS NULL AND h.addnum2 IS NULL THEN h.housenum
                                WHEN h.housenum IS NOT NULL AND h.addnum1 IS NOT NULL AND h.addnum2 IS NULL THEN h.housenum || '/' || h.addnum1
                                WHEN h.housenum IS NOT NULL AND h.addnum1 IS NOT NULL AND h.addnum2 IS NOT NULL THEN h.housenum || '/' || h.addnum1 || '/' || h.addnum2
                            END) AS number,
                            (CASE
                                WHEN h.housetype IS NOT NULL AND h.addtype1 IS NULL AND h.addtype2 IS NULL THEN t.name
                                WHEN h.housetype IS NOT NULL AND h.addtype1 IS NOT NULL AND h.addtype2 IS NULL THEN t.name || '/' || t1.name
                                WHEN h.housetype IS NOT NULL AND h.addtype1 IS NOT NULL AND h.addtype2 IS NOT NULL THEN t.name || '/' || t1.name || '/' || t2.name
                            END) AS typename
                        FROM {0}.houses h
                            JOIN {0}.house_types t ON t.id = h.housetype
                            LEFT JOIN {0}.house_types t1 ON t1.id = h.addtype1
                            LEFT JOIN {0}.house_types t2 ON t2.id = h.addtype2) h ON h.objectid = a.objectid
                WHERE a.isactive = 1 AND  a.parentobjid::text = $1::text 
            ORDER BY level, name;
            $BODY$;
            ALTER FUNCTION {0}.getchildren_mun(integer)
                OWNER TO postgres;
            
            
            CREATE OR REPLACE FUNCTION {0}.gethousechildren(
                objectid integer)
                RETURNS TABLE(objectid bigint, name character varying, typename character varying, level integer, children bigint) 
                LANGUAGE 'sql'
                COST 100
                VOLATILE PARALLEL UNSAFE
                ROWS 1000
            AS $BODY$
            SELECT c.objectid,
                c.number AS name,
                'машино-место' AS typename,
                17 AS level,
                {0}.row_estimator_adm(c.objectid)
            FROM {0}.adm_hierarchy h
                JOIN {0}.carplaces c ON c.objectid = h.objectid
            WHERE h.isactive = 1 AND c.isactual = 1 AND c.isactive = 1 AND h.parentobjid = $1
            UNION
            SELECT a.objectid,
                a.number AS name,
                a.typename,
                11 AS level,
                {0}.row_estimator_adm(a.objectid)
            FROM {0}.adm_hierarchy h
                JOIN (SELECT a.objectid,
                        a.number,
                        t.name AS typename
                    FROM {0}.apartments a
                        JOIN {0}.apartment_types t ON t.id = a.aparttype
                    WHERE a.isactual = 1 AND a.isactive = 1) a ON a.objectid = h.objectid
            WHERE h.isactive = 1 AND h.parentobjid = $1
            ORDER BY level, name;
            $BODY$;
            ALTER FUNCTION {0}.gethousechildren(integer)
                OWNER TO postgres;
            
            
            CREATE OR REPLACE FUNCTION {0}.getrooms(
                objectid integer)
                RETURNS TABLE(objectid bigint, name character varying, typename character varying, level integer, children bigint) 
                LANGUAGE 'sql'
                COST 100
                VOLATILE PARALLEL UNSAFE
                ROWS 1000
            AS $BODY$
            SELECT r.objectid,
                r.number AS name,
                r.typename,
                12 AS level,
                {0}.row_estimator_adm(r.objectid)
            FROM {0}.adm_hierarchy h
                JOIN (SELECT r.objectid,
                        r.number,
                        t.name AS typename
                    FROM {0}.rooms r
                        JOIN {0}.room_types t ON t.id = r.roomtype
                    WHERE r.isactual = 1 AND r.isactive = 1) r ON r.objectid = h.objectid
            WHERE h.isactive = 1 AND h.parentobjid = $1
            ORDER BY name;
            $BODY$;
            ALTER FUNCTION {0}.getrooms(integer)
                OWNER TO postgres;
            """.format(schemaName))
    conn.commit()
    print('--- Функции созданы ---')