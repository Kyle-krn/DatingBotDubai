select v.id,
	   v.user_id,
	   u.tg_username,
	   v.target_user_id,
	   u2.tg_username,
	   r.percent_compatibility ,
	   v.like
from userview v
JOIN usermodel u  ON u.id  = v.user_id
JOIN usermodel u2  ON u2.id  = v.target_user_id
join usersrelations r on (r.user_id = v.user_id and r.target_user_id =v.target_user_id) or (r.user_id = v.target_user_id and r.target_user_id = v.user_id) 
order by r.percent_compatibility desc