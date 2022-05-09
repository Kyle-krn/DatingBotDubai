from tortoise import Tortoise


async def rowsql_likes(user_id: int) -> dict:
    conn = Tortoise.get_connection("default")
    sql_query = f'''select v1.id 
                    from userview v1
                    join usermodel t_u on v1.target_user_id  = t_u.id
                    join usersrelations r on (r.user_id = v1.user_id and r.target_user_id =v1.target_user_id) 
						                     or 
						                     (r.user_id = v1.target_user_id and r.target_user_id = v1.user_id)
                    where v1.user_id = {user_id}
                    and r.percent_compatibility > 0
                    and t_u.verification = true
                    and t_u.ban = false
                    and v1.target_user_id in (select v.user_id
                    						  from userview v
                    						  where v.target_user_id = {user_id} 
                    						  and v."like" = true
                    						  and v.user_id not in (select v.target_user_id
                    												from userview v
                    												where v.user_id = {user_id}
                    							 					and v.like = true))
                     order by v1.dislike, 
                    		  v1.count_view, 
                              r.percent_compatibility desc'''
    user_likes_id = await conn.execute_query_dict(sql_query)
    return user_likes_id