from requests import request


async def filter_place_func():
    sql = '''CREATE OR REPLACE FUNCTION "public".check_place(user_dubai boolean,
     												 user_moving_to_dubai boolean,
     												 user_interest_place integer[],
     												 target_user_dubai boolean,
     												 target_user_moving_to_dubai boolean,
     												 target_user_interest_place integer[])
             RETURNS boolean AS
            $$ 
            BEGIN 	 -- 1,4                               1,4; 1,4,5; 1,4,5,6 ; 1,4,6
                CASE WHEN ((SELECT check_place_user(user_dubai, user_moving_to_dubai, '1')) AND ARRAY[1] = array_sort(user_interest_place)) 
                        AND 
                        ((SELECT check_place_user(target_user_dubai, target_user_moving_to_dubai, '1')) AND (SELECT check_target_place_condition(target_user_interest_place, 1)))
                    THEN RETURN true;
                    -- 1,4,5                            1,4; 1,4,5; 1,4,5,6 ; 1,4,6; 2,4; 2,4,5; 2,4,5,6 ; 2,4,6
                    WHEN ((SELECT check_place_user(user_dubai, user_moving_to_dubai, '1')) AND ARRAY[1,2] = array_sort(user_interest_place)) 
                        AND 
                        ((SELECT check_place_user(target_user_dubai, target_user_moving_to_dubai, '1_2')) AND (SELECT check_target_place_condition(target_user_interest_place, 1)))
                    THEN RETURN true;
                    -- 1,4,5,6                         1,4; 1,4,5; 1,4,5,6 ; 1,4,6; 2,4; 2,4,5; 2,4,5,6 ; 2,4,6; 3,4; 3,4,5; 3,4,5,6 ; 3,4,6 
                    WHEN ((SELECT check_place_user(user_dubai, user_moving_to_dubai, '1')) AND ARRAY[1,2,3] = array_sort(user_interest_place))
                        AND
                        (SELECT check_target_place_condition(target_user_interest_place, 1))
                    THEN RETURN true;
                    -- 1,4,6                            1,4; 1,4,5; 1,4,5,6 ; 1,4,6; 3,4; 3,4,5; 3,4,5,6 ; 3,4,6
                    WHEN ((SELECT check_place_user(user_dubai, user_moving_to_dubai, '1')) AND ARRAY[1,3] = array_sort(user_interest_place))
                        AND
                        ((SELECT check_place_user(target_user_dubai, target_user_moving_to_dubai, '1_3')) AND (SELECT check_target_place_condition(target_user_interest_place, 1)))
                    THEN RETURN true;
                    -- 1,5                               2,4; 2,4,5; 2,4,5,6 ; 2,4,6
                    WHEN ((SELECT check_place_user(user_dubai, user_moving_to_dubai, '1')) AND ARRAY[2] = array_sort(user_interest_place))
                        AND
                        ((SELECT check_place_user(target_user_dubai, target_user_moving_to_dubai, '2')) AND (SELECT check_target_place_condition(target_user_interest_place, 1)))
                    THEN RETURN true;
                    -- 1,5,6                            2,4; 2,4,5; 2,4,5,6 ; 2,4,6; 3,4; 3,4,5; 3,4,5,6 ; 3,4,6
                    WHEN ((SELECT check_place_user(user_dubai, user_moving_to_dubai, '1')) AND ARRAY[2,3] = array_sort(user_interest_place))
                        AND
                        ((SELECT check_place_user(target_user_dubai, target_user_moving_to_dubai, '2_3')) AND (SELECT check_target_place_condition(target_user_interest_place, 1)))
                    THEN RETURN true;
                    -- 1,6                               3,4; 3,4,5; 3,4,5,6 ; 3,4,6
                    WHEN ((SELECT check_place_user(user_dubai, user_moving_to_dubai, '1')) AND ARRAY[3] = array_sort(user_interest_place))
                        AND
                        ((SELECT check_place_user(target_user_dubai, target_user_moving_to_dubai, '3')) AND (SELECT check_target_place_condition(target_user_interest_place, 1)))
                    THEN RETURN true;
                    
                    
                    -- 2,4                               1,5; 1,4,5; 1,4,5,6 ; 1,5,6
                    WHEN ((SELECT check_place_user(user_dubai, user_moving_to_dubai, '2')) AND ARRAY[1] = array_sort(user_interest_place))
                        AND
                        ((SELECT check_place_user(target_user_dubai, target_user_moving_to_dubai, '1')) AND (SELECT check_target_place_condition(target_user_interest_place, 2)))
                    THEN RETURN true;
                    -- 2,4,5                            1,5; 1,4,5; 1,4,5,6 ; 1,5,6; 2,5; 2,4,5; 2,4,5,6 ; 2,5,6
                    WHEN ((SELECT check_place_user(user_dubai, user_moving_to_dubai, '2')) AND ARRAY[1,2] = array_sort(user_interest_place))
                        AND
                        ((SELECT check_place_user(target_user_dubai, target_user_moving_to_dubai, '1_2')) AND (SELECT check_target_place_condition(target_user_interest_place, 2)))
                    THEN RETURN true;
                    -- 2,4,5,6                         1,5; 1,4,5; 1,4,5,6 ; 1,5,6; 2,5; 2,4,5; 2,4,5,6 ; 2,5,6; 3,5; 3,4,5; 3,4,5,6 ; 3,5,6
                    WHEN ((SELECT check_place_user(user_dubai, user_moving_to_dubai, '2')) AND ARRAY[1,2,3] = array_sort(user_interest_place))
                        AND
                        (SELECT check_target_place_condition(target_user_interest_place, 2))
                    THEN RETURN true;
                    -- 2,4,6                           1,5; 1,4,5; 1,4,5,6 ; 1,5,6; 3,5; 3,4,5; 3,4,5,6 ; 3,5,6
                    WHEN ((SELECT check_place_user(user_dubai, user_moving_to_dubai, '2')) AND ARRAY[2,3] = array_sort(user_interest_place))
                        AND
                        ((SELECT check_place_user(target_user_dubai, target_user_moving_to_dubai, '1_3')) AND (SELECT check_target_place_condition(target_user_interest_place, 2)))
                    THEN RETURN true;
                    -- 2,5                              2,5; 2,4,5; 2,4,5,6 ; 2,5,6
                    WHEN ((SELECT check_place_user(user_dubai, user_moving_to_dubai, '2')) AND ARRAY[2] = array_sort(user_interest_place))
                        AND
                        ((SELECT check_place_user(target_user_dubai, target_user_moving_to_dubai, '2')) AND (SELECT check_target_place_condition(target_user_interest_place, 2)))
                    THEN RETURN true;
                    -- 2,5,6                           2,5; 2,4,5; 2,4,5,6 ; 2,5,6; 3,5; 3,4,5; 3,4,5,6 ; 3,5,6
                    WHEN ((SELECT check_place_user(user_dubai, user_moving_to_dubai, '2')) AND ARRAY[2,3] = array_sort(user_interest_place))
                        AND
                        ((SELECT check_place_user(target_user_dubai, target_user_moving_to_dubai, '2_3')) AND (SELECT check_target_place_condition(target_user_interest_place, 2)))
                    THEN RETURN true;
                    -- 2,6                              3,5; 3,4,5; 3,4,5,6 ; 3,5,6
                    WHEN ((SELECT check_place_user(user_dubai, user_moving_to_dubai, '2')) AND ARRAY[3] = array_sort(user_interest_place))
                        AND
                        ((SELECT check_place_user(target_user_dubai, target_user_moving_to_dubai, '3')) AND (SELECT check_target_place_condition(target_user_interest_place, 2)))
                    THEN RETURN true;
                    -- 3,4                              1,6; 1,4,6; 1,4,5,6 ; 1,5,6
                    WHEN ((SELECT check_place_user(user_dubai, user_moving_to_dubai, '3')) AND ARRAY[1] = array_sort(user_interest_place))
                        AND
                        ((SELECT check_place_user(target_user_dubai, target_user_moving_to_dubai, '1')) AND (SELECT check_target_place_condition(target_user_interest_place, 3)))
                    THEN RETURN true;
                    -- 3,4,5                           1,6; 1,4,6; 1,4,5,6 ; 1,5,6; 2,6; 2,4,6; 2,4,5,6 ; 2,5,6
                    WHEN ((SELECT check_place_user(user_dubai, user_moving_to_dubai, '3')) AND ARRAY[1,2] = array_sort(user_interest_place))
                        AND
                        ((SELECT check_place_user(target_user_dubai, target_user_moving_to_dubai, '1_2')) AND (SELECT check_target_place_condition(target_user_interest_place, 3)))
                    THEN RETURN true;
                    -- 3,4,6                           1,6; 1,4,6; 1,4,5,6 ; 1,5,6; 3,6; 3,4,6; 3,4,5,6 ; 3,5,6
                    WHEN ((SELECT check_place_user(user_dubai, user_moving_to_dubai, '3')) AND ARRAY[1,3] = array_sort(user_interest_place))
                        AND
                        ((SELECT check_place_user(target_user_dubai, target_user_moving_to_dubai, '1_3')) AND (SELECT check_target_place_condition(target_user_interest_place, 3)))
                    THEN RETURN true;
                    -- 3,5                              2,6; 2,4,6; 2,4,5,6 ; 2,5,6
                    WHEN ((SELECT check_place_user(user_dubai, user_moving_to_dubai, '3')) AND ARRAY[2] = array_sort(user_interest_place))
                        AND
                        ((SELECT check_place_user(target_user_dubai, target_user_moving_to_dubai, '2')) AND (SELECT check_target_place_condition(target_user_interest_place, 3)))
                    THEN RETURN true;
                    -- 3,5,6                           2,6; 2,4,6; 2,4,5,6 ; 2,5,6; 3,6; 3,4,6; 3,4,5,6 ; 3,5,6
                    WHEN ((SELECT check_place_user(user_dubai, user_moving_to_dubai, '3')) AND ARRAY[2,3] = array_sort(user_interest_place))
                        AND
                        ((SELECT check_place_user(target_user_dubai, target_user_moving_to_dubai, '2_3')) AND (SELECT check_target_place_condition(target_user_interest_place, 3)))
                    THEN RETURN true;
                    -- 3,6                              3,6; 3,4,6; 3,4,5,6 ; 3,5,6
                    WHEN ((SELECT check_place_user(user_dubai, user_moving_to_dubai, '3')) AND ARRAY[3] = array_sort(user_interest_place))
                        AND
                        ((SELECT check_place_user(target_user_dubai, target_user_moving_to_dubai, '3')) AND (SELECT check_target_place_condition(target_user_interest_place, 3)))
                    THEN RETURN true;
                    ELSE RETURN false;
                END CASE; 
            END; 
            $$ 
            LANGUAGE plpgsql;'''
    return sql


async def filter_purp():
    sql = ''' CREATE OR REPLACE FUNCTION "public".check_purp(user_male boolean,
											 	user_purp integer[], 
											 	target_user_male boolean,
											 	target_user_purp integer[])
                RETURNS boolean AS
                $$ 
                BEGIN 
                    IF (ARRAY[2] = user_purp or ARRAY[2] = target_user_purp) AND (user_male=target_user_male)
                    THEN RETURN false;
                    ELSE RETURN user_purp && target_user_purp;
                    END IF;
                    
                END; 
                $$ 
                LANGUAGE plpgsql;'''
    return sql


async def filter_min_max_age_children():
    sql = '''
            CREATE OR REPLACE FUNCTION "public".check_min_max_children_age(user_children_age jsonb,
                                                                            min_age integer, 
                                                                            max_age integer)
            RETURNS boolean AS
            $$ 
            BEGIN
                IF user_children_age IS NOT null AND JSONB_ARRAY_LENGTH(user_children_age) > 0 THEN return min_age <= (select min(t.children_array) -- дети собес
                                                                                from (select jsonb_array_elements(user_children_age)::integer as children_array) 
                                                                                as t) and 
                                                                                (select max(t.children_array) 
                                                                                from (select jsonb_array_elements(user_children_age)::integer as children_array) 
                                                                                as t) <= max_age;
                                                            ELSE return true; 
                END IF;
            END; 
            $$ 
            LANGUAGE plpgsql;
            '''
    return sql