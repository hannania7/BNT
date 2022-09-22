CREATE OR REPLACE FUNCTION yes3k_create_table_manager()
 RETURNS text LANGUAGE plpgsql AS $function$ DECLARE nextday date;
BEGIN -- 내일 테이블을 미리 만듦
nextday := current_date + 1;

execute format('CREATE TABLE IF NOT EXISTS model_yes3k_dataset_%s'||'(LIKE model_yes3k_dataset INCLUDING ALL,'||'unique(create_time, pred_time)'||') INHERITS(model_yes3k_dataset)',to_char(nextday,'YYYYMMDD'), nextday::timestamp);

execute format('CREATE TABLE IF NOT EXISTS model_yes3k_data_%s'||'(LIKE model_yes3k_data INCLUDING ALL'||') INHERITS(model_yes3k_data)',to_char(nextday,'YYYYMMDD'), nextday::timestamp);

return 'success';

EXCEPTION
WHEN undefined_table THEN raise notice '%, %', SQLSTATE, SQLERRM;
return '';

END;
$function$
;