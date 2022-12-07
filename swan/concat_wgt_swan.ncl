load "$NCARG_ROOT/lib/ncarg/nclscripts/esmf/ESMF_regridding.ncl"

begin
	; Get start datetime.
	filepath			= fpath
	fname_no_ext		= systemfunc("basename "+filepath+" .nc")
	strs				= str_split(fname_no_ext, "_")
	datetime			= strs(2)
	
	; Get src file.
	src_file			= "/DATA/PYTHON+NCL/output/swan/concat_swan_" + \
						  datetime + "_" + \
						  variable + ".nc"
    sfile				= addfile(src_file,"r")
    src_name_no_ext		= systemfunc("basename "+src_file+" .nc")

	; Do the regridding using a weight file.
    var					= sfile->$variable$
	wgt_file			= "/DATA/PYTHON+NCL/source/weight_files/wgt_file_SWAN.nc"
	Opt					= False
    var_regrid			= ESMF_regrid_with_weights(var, wgt_file, Opt)
	
	; Remove missing value.
    delete(var_regrid@missing_value)
	
	; Change time dimension name.
    var_regrid!0		= "time"
    var_regrid@time		= "time"

	; Remove regridded file if it already exists.
	output_path			= "/DATA/PYTHON+NCL/output/swan/"
    rgrdFileName		= output_path+src_name_no_ext+"_regrid.nc"
    system("rm -f " + rgrdFileName)
	
	; Write the regridded variable to a file.
	; Coordinate arrays will be written automatically.
    rgrd_nc				= addfile(rgrdFileName,"c")
    rgrd_nc->$variable$ = var_regrid
	
	; Remove the src file.
    system("rm -f " + src_file)	
end