async def sort_array_func():
    sql = '''CREATE OR REPLACE FUNCTION array_sort (ANYARRAY)
             RETURNS ANYARRAY LANGUAGE SQL
             AS $$
             SELECT ARRAY(SELECT unnest($1) ORDER BY 1)
             $$;'''
    return sql


async def place_user_func():
    sql = '''CREATE OR REPLACE FUNCTION "public".check_place_user(user_dubai boolean,
                                                                  user_moving_to_dubai boolean, 
                                                                  place_str text)
            RETURNS boolean AS
            $$ 
            BEGIN 
                CASE when place_str = '1' and user_dubai is true
                    then return true; 
                    when place_str = '1_2' and (user_dubai is true or user_moving_to_dubai is true)
                    then return true;
                    when place_str = '1_3' and (user_moving_to_dubai is false or user_moving_to_dubai is null)
                    then RETURN true;
                    when place_str = '2' and (user_moving_to_dubai is true)
                    then RETURN true;
                    when place_str = '2_3' and (user_dubai is false)
                    then RETURN true;
                    when place_str = '3' and (user_dubai is false and (user_moving_to_dubai is false or user_moving_to_dubai is null))
                    then RETURN true;
                else return false;
                end case; 
            END; 
            $$ 
            LANGUAGE plpgsql;'''
    return sql


async def target_place_condition():
    sql = '''CREATE OR REPLACE FUNCTION "public".check_target_place_condition(target_user_interest_place integer[],
																              condition_number int)
             RETURNS boolean AS
             $$ 
             BEGIN 	 
                 CASE WHEN condition_number = 1 THEN
                             IF ARRAY[1] = array_sort(target_user_interest_place) 
                                 or 
                                 ARRAY[1,2] = array_sort(target_user_interest_place)
                                 or
                                 ARRAY[1,2,3] = array_sort(target_user_interest_place)
                                 or
                                 ARRAY[1,3] = array_sort(target_user_interest_place)
                             THEN return true; 
                             ELSE return false; 
                             END IF;
                     WHEN condition_number = 2 THEN
                             IF ARRAY[2] = array_sort(target_user_interest_place) 
                                 or 
                                 ARRAY[1,2] = array_sort(target_user_interest_place)
                                 or
                                 ARRAY[1,2,3] = array_sort(target_user_interest_place)
                                 or
                                 ARRAY[2,3] = array_sort(target_user_interest_place)
                             THEN return true; 
                             ELSE return false; 
                             END IF;
                     WHEN condition_number = 3 THEN
                             IF ARRAY[3] = array_sort(target_user_interest_place) 
                                 or 
                                 ARRAY[1,3] = array_sort(target_user_interest_place)
                                 or
                                 ARRAY[1,2,3] = array_sort(target_user_interest_place)
                                 or
                                 ARRAY[2,3] = array_sort(target_user_interest_place)
                             THEN return true; 
                             ELSE return false; 
                             END IF;
                             
                 ELSE RETURN false;
                 END CASE;
             END; 
             $$ 
             LANGUAGE plpgsql;'''
    return sql