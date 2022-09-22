--roms
--delete from model_data where st_id in (select st_id from model_dataset where create_time < date_trunc('day', NOW()+interval'-5 day'));
--delete from model_dataset where create_time < date_trunc('day', NOW()+interval'-5 day');
select ww3_create_table_manager();
