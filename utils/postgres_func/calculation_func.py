

import re


async def calculation_age_func():
    sql = '''
             CREATE OR REPLACE FUNCTION "public".calculation_age(integer, integer)
                     RETURNS integer AS
             $BODY$
                     select (select dp."percent" 
                             from dating_percent dp 
                             where dp.id = 2) - (ABS($1 - $2) * (SELECT dp."percent" 
                                                                 FROM dating_percent dp 
                                                                 WHERE dp.id = 3));
             $BODY$
                     LANGUAGE 'sql' volatile;'''
    return sql


async def calculation_children_func():
    sql = '''
            CREATE OR REPLACE FUNCTION "public".calculation_children(user_children boolean,
                                                                    user_children_age jsonb,
                                                                    target_user_children boolean,
                                                                    target_user_children_age jsonb)
            RETURNS integer AS
            $$ 
            DECLARE
            percent_children integer = 0;
            array_user_children_age integer[] := (SELECT ARRAY_AGG(value) FROM jsonb_array_elements(user_children_age));
            array_target_user_children_age integer[] := (SELECT ARRAY_AGG(value) FROM jsonb_array_elements(target_user_children_age));
            i integer;
            i2 integer;
            BEGIN
                IF (user_children is not null and target_user_children is not null) and (user_children = target_user_children) 
                    THEN percent_children = 20;
                    ELSE RETURN 0;
                END IF;
                IF (jsonb_array_length(user_children_age) > 0 and jsonb_array_length(target_user_children_age) > 0)
                THEN FOREACH i IN ARRAY array_user_children_age
                        LOOP
                            FOREACH i2 IN ARRAY array_target_user_children_age
                            LOOP
                                IF ABS(i - i2) <= 2 THEN
                                percent_children = percent_children + (select "percent" from dating_percent where id = 4);
                                END IF;
                            END LOOP;
                        END LOOP;
                END IF;
                RETURN percent_children;
            END; 
            $$ 
            LANGUAGE plpgsql; '''
    return sql


async def calculation_hobbies_func():
    sql = '''CREATE OR REPLACE FUNCTION "public".calculation_hobbies(user_hobbies integer[],
 													    target_user_hobbies integer[])
            RETURNS integer AS
            $$ 
            DECLARE
            percent_hobbies integer = 0;
            i integer;
            i2 integer;
            BEGIN
                IF array_length(array_remove(user_hobbies, null), 1) is not null and array_length(array_remove(target_user_hobbies, null), 1) is not null
                THEN FOREACH i in ARRAY user_hobbies
                        LOOP
                        FOREACH i2 in ARRAY target_user_hobbies
                            LOOP
                            IF i = i2 THEN percent_hobbies = percent_hobbies + (SELECT percent FROM dating_percent WHERE id = 6);
                            END IF;
                            END LOOP;
                        END LOOP;
                END IF;
                RETURN percent_hobbies;
            END; 
            $$ 
            LANGUAGE plpgsql;'''
    return sql


async def calculation_general_func():
    sql = '''CREATE OR REPLACE FUNCTION "public".calculation_general_percent(percent_age integer,
 													    		percent_children integer,
 													    		percent_hobbies integer)
            RETURNS integer AS
            $$ 
            BEGIN
                RETURN percent_age + percent_children + percent_hobbies + (select percent from dating_percent where id = 1);
            END; 
            $$ 
            LANGUAGE plpgsql;   
            '''
    return sql