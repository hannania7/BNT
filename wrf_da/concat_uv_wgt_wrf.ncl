load "$NCARG_ROOT/lib/ncarg/nclscripts/esmf/ESMF_regridding.ncl"

begin
	; Get wrfdm num (wrfdm1 or wrfdm2).
	filepath			= fpath
	fname_no_ext		= systemfunc("basename "+filepath+" .nc")
	strs				= str_split(fname_no_ext, "_")
	wrfdm_num			= strs(0)
	
	; Get modelname (wrf, wrf_da, wrf_um).
	parent_dirpath		= systemfunc("dirname "+filepath)
	parent_dirname		= systemfunc("basename "+parent_dirpath)
	modelname			= str_lower(parent_dirname)
	
	; Get datetime in YYYYMMDDHH format.
	a					= addfile(filepath,"r")
	time				= a->ocean_time
	yyyymmddhh			= cd_calendar(time(0), -2)
	
	; Get src file.
	src_file			= "/DATA/PYTHON+NCL/output/wrf_da/concat_" + \
						  modelname + "_" + \
						  wrfdm_num + "_" + \
						  yyyymmddhh + \
						  "_uv.nc"
    sfile				= addfile(src_file,"r")
	src_name_no_ext		= systemfunc("basename "+src_file+" .nc")
	
	; Regrid using a weight file.
	u_var				= sfile->Uwind
    v_var				= sfile->Vwind
	wgt_file			= "/DATA/PYTHON+NCL/source/weight_files/wgt_file_" + \
						  modelname + "_" + \
						  wrfdm_num + ".nc"
    Opt					= False
    u_var_regrid		= ESMF_regrid_with_weights(u_var, wgt_file, Opt)
	v_var_regrid		= ESMF_regrid_with_weights(v_var, wgt_file, Opt)
	
	; Remove missing value.
    delete(u_var_regrid@missing_value)
	delete(v_var_regrid@missing_value)
	
	; Change time dimension name.
    u_var_regrid!0		= "time"
	v_var_regrid!0		= "time"
    u_var_regrid@time	= "time"
	v_var_regrid@time	= "time"

	; Remove regridded file if it already exists.
	output_path			= "/DATA/PYTHON+NCL/output/wrf_da/"
    rgrdFileName		= output_path+src_name_no_ext+"_regrid.nc"
    system("rm -f " + rgrdFileName)
	
	; Write the regridded variable to a file.
	; Coordinate arrays will be written automatically.
    rgrd_nc				= addfile(rgrdFileName,"c")
    rgrd_nc->u			= u_var_regrid
    rgrd_nc->v			= v_var_regrid
	
	; Remove the src file.
    system("rm -f " + src_file)
end