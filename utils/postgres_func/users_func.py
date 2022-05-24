

async def sql_query_get_user_func():
    sql = '''create or REPLACE FUNCTION "public".get_user(arg_user_id integer, many_rows boolean) RETURNS table(
																		   id int,
																		   tg_id bigint,
																		   tg_username text,
																		   dubai boolean,
																		   moving_to_dubai boolean,
																		   male boolean,
																		   birthday date,
																		   children boolean,
																		   children_age jsonb,
																		   verification boolean,
																		   end_registration boolean,
																		   ban bool,
																		   purp integer[],
																		   hobbies integer[],
																		   interest_place integer[],
																		   settings_male boolean,
																		   settings_min_age integer,
																		   settings_max_age integer,
																		   settings_children boolean,
																		   settings_children_min_age integer,
																		   settings_children_max_age integer)
    AS $$ 
    select t1.id,
    	   t1.tg_id,
    	   t1.tg_username,
    	   t1.dubai,
    	   t1.moving_to_dubai,
    	   t1.male,
    	   t1.birthday,
    	   t1.children,
    	   t1.children_age,
    	   t1.verification,
    	   t1.end_registration,
    	   t1.ban,
    	   t1.purp,
    	   t2.hobbies,
    	   t3.interest_place,
    	   t4.male,
    	   t4.min_age,
    	   t4.max_age,
    	   t4.children,
    	   t4.children_min_age,
    	   t4.children_max_age
from users u
join (select u.*, array_agg(up.purposeofdating_id) as purp
	  from users u 
	  left join users_purps up on u.id = up.users_id
	  where case when many_rows is false then u.id = arg_user_id else u.id != arg_user_id end 
	  group by u.id) as t1 ON t1.id = u.id
join (select u.id, array_agg(uh.hobbies_id) as hobbies
	  from users u 
	  left join users_hobbies uh  on u.id = uh.users_id
	  where case when many_rows is false then u.id = arg_user_id else u.id != arg_user_id end 
	  group by u.id) as t2 ON t2.id = u.id
join (select u.id, array_agg(ipu.datinginterestplace_id) as interest_place 
	  from users u
	  left join users_places ipu on u.id = ipu.users_id
	  where case when many_rows is false then u.id = arg_user_id else u.id != arg_user_id end 
	  group by u.id, ipu.users_id) as t3 ON t3.id = u.id
join (select u.id, s.male, s.min_age, s.max_age, s.children, s.children_min_age, s.children_max_age 
	  from users u
	  left join users_settings s ON u.id = s.user_id 
	  where case when many_rows is false then u.id = arg_user_id else u.id != arg_user_id end ) as t4 ON t4.id = u.id;
    $$
    LANGUAGE SQL;
        '''
    return sql


async def get_users_func():
    sql = '''
-- Берем 1 юзера если true, множество false
create or REPLACE FUNCTION "public".get_users(arg_user_id int, 
											  arg_target_user_id int) RETURNS table(
																				   target_id int,
																				   target_tg_id bigint,
																				   target_tg_username text,
																				   target_dubai boolean,
																				   target_moving_to_dubai boolean,
																				   target_male boolean,
																				   target_birthday date,
																				   target_children boolean,
																				   target_children_age jsonb,
																				   target_verification boolean,
																				   target_end_registration boolean,
																				   target_ban boolean,
																				   target_purp integer[],
																				   target_hobbies integer[],
																				   target_interest_place integer[],
																				   target_settings_male boolean,
																				   target_settings_min_age integer,
																				   target_settings_max_age integer,
																				   target_settings_children boolean,
																				   target_settings_children_min_age integer,
																				   target_settings_children_max_age integer,
																				   id int,
																				   tg_id bigint,
																				   tg_username text,
																				   dubai boolean,
																				   moving_to_dubai boolean,
																				   male boolean,
																				   birthday date,
																				   children boolean,
																				   children_age jsonb,
																				   verification boolean,
																				   end_registration boolean,
																				   purp integer[],
																				   hobbies integer[],
																				   interest_place integer[],
																				   settings_male boolean,
																				   settings_min_age integer,
																				   settings_max_age integer,
																				   settings_children boolean,
																				   settings_children_min_age integer,
																				   settings_children_max_age integer,
																				   view_like boolean,
																				   view_superlike boolean,
																				   view_dislike boolean,
																				   view_count integer,
																				   target_view_like boolean,
																				   target_view_superlike boolean,
																				   target_view_dislike boolean,
																				   target_view_count integer
																				   )
    AS $$ 
DECLARE
        target_user_id integer := arg_target_user_id;
        many_rows boolean := true;
BEGIN
  IF target_user_id is null 
	 THEN target_user_id = arg_user_id;
	 ELSE many_rows = false;
  END IF;
RETURN QUERY
		select t.*
		from(
		select tu.id as target_id,
			   tu.tg_id as target_tg_id,
			   tu.tg_username as target_tg_username,
			   tu.dubai as target_dubai,
			   tu.moving_to_dubai as target_moving_to_dubai,
			   tu.male as target_male,
			   tu.birthday as target_birthday,
			   tu.children as target_children,
			   tu.children_age as target_children_age,
			   tu.verification as target_verification,
			   tu.end_registration as target_end_registration,
			   tu.ban as target_ban,
			   tu.purp as target_purp,
			   tu.hobbies as target_hobbies,
			   tu.interest_place as target_interest_place,
			   tu.settings_male as target_settings_male,
			   tu.settings_min_age as target_settings_min_age,
			   tu.settings_max_age as target_settings_max_age,
			   tu.settings_children as target_settings_children,
			   tu.settings_children_min_age as target_settings_children_min_age,
			   tu.settings_children_max_age as target_settings_children_max_age,
			   u.id as id,
			   u.tg_id as tg_id,
			   u.tg_username as tg_username,
			   u.dubai as dubai,
			   u.moving_to_dubai as moving_to_dubai,
			   u.male as male,
			   u.birthday as birthday,
			   u.children as children,
			   u.children_age as children_age,
			   u.verification as verification,
			   u.end_registration as end_registration,
			   u.purp as purp,
			   u.hobbies as hobbies,
			   u.interest_place as interest_place,
			   u.settings_male as settings_male,
			   u.settings_min_age as settings_min_age,
			   u.settings_max_age as settings_max_age,
			   u.settings_children as settings_children,
			   u.settings_children_min_age as settings_children_min_age,
			   u.settings_children_max_age as settings_children_max_age,
			   uv.like as view_like,
			   uv.superlike as view_superlike,
			   uv.dislike as view_dislike,
			   uv.count_view as view_count,
			   tuv.like as target_view_like,
			   tuv.superlike as view_superlike,
			   tuv.dislike as view_dislike,
			   tuv.count_view as view_count
		from get_user(arg_user_id => target_user_id, many_rows => many_rows) as tu
		CROSS JOIN get_user(arg_user_id => arg_user_id, many_rows => false) as u
		left join users_views as uv on uv.user_id = u.id and uv.target_user_id = tu.id
		left join users_views as tuv on tuv.user_id = tu.id and tuv.target_user_id = u.id) as t;
END;
    $$
    LANGUAGE plpgsql;'''
    return sql



async def calculation_users():
    sql = '''create or REPLACE FUNCTION "public".calculation_users(arg_user_id int, 
											  		  arg_target_user_id int,
											  		  arg_like_catalog bool) RETURNS table(target_id int,
											  		  									    general_percent int)
    AS $$ 
			BEGIN
			RETURN QUERY
					SELECT * FROM (
					SELECT users_table.target_id,
						calculation_general_percent(percent_age => calculation_age(extract(year from AGE(CURRENT_DATE, users_table.birthday))::integer, 
																				extract(year from AGE(CURRENT_DATE, users_table.target_birthday))::integer),
												percent_children => calculation_children(users_table.children, 
																						users_table.children_age, 
																						users_table.target_children, 
																						users_table.target_children_age),
												percent_hobbies => calculation_hobbies(users_table.hobbies,
																						users_table.target_hobbies)
												) as general_percent
			from get_users(arg_user_id => arg_user_id, arg_target_user_id => arg_target_user_id) as users_table
			WHERE users_table.target_verification is true
				AND
				users_table.target_end_registration is true
				AND
				users_table.target_ban is false
				AND
					(select check_place(users_table.dubai,				-- проверяем по местположению
									users_table.moving_to_dubai,
									users_table.interest_place,
									users_table.target_dubai,
									users_table.target_moving_to_dubai,
									users_table.target_interest_place)) is true
				AND
					(select check_purp(users_table.male,
									users_table.purp,
									users_table.target_male,
									users_table.target_purp))	-- цель знакомтсва
				AND
					(users_table.settings_min_age <= extract(year from AGE(CURRENT_DATE, users_table.target_birthday))
					and 
					extract(year from AGE(CURRENT_DATE, users_table.target_birthday)) <= users_table.settings_max_age) -- возраст собес
				AND
					(users_table.target_settings_min_age <= extract(year from AGE(CURRENT_DATE, users_table.birthday)) 
					and 
					extract(year from AGE(CURRENT_DATE, users_table.birthday)) <= users_table.target_settings_max_age)	-- свой возраст
				AND
					CASE WHEN users_table.settings_male is not null 
						THEN users_table.settings_male = users_table.target_male 
						ELSE true END -- гендер собес
				AND
					CASE WHEN users_table.target_settings_male is not null 
						THEN users_table.male = users_table.target_settings_male 
						ELSE true END -- мой гендер
				AND
					CASE WHEN users_table.settings_children is not null and users_table.target_children is not null 
						THEN users_table.settings_children = users_table.target_children 
						ELSE true END -- дети собес
				AND 
					CASE WHEN users_table.target_settings_children is not null and users_table.children is not null 
						THEN users_table.children = users_table.target_settings_children 
						ELSE true END -- мои дети
				AND
					(SELECT check_min_max_children_age(users_table.target_children_age, 
													users_table.settings_children_min_age, 
													users_table.settings_children_max_age)) -- min max возраст детей собес	
				AND
					(select check_min_max_children_age(users_table.children_age, 
													users_table.target_settings_children_min_age, 
													users_table.target_settings_children_max_age)) -- min max возраст детей мои 
				AND 
					CASE WHEN arg_like_catalog is false 
						THEN (users_table.view_like is null or users_table.view_like is false) -- нет лайка
						ELSE (users_table.target_view_like is true and (users_table.view_like is null or users_table.view_like is false)) 
						END
			ORDER BY view_count DESC,
					general_percent DESC) as t
			WHERE t.general_percent > 0;
			END;
				$$
				LANGUAGE plpgsql;'''
    return sql