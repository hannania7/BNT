load "$NCARG_ROOT/lib/ncarg/nclscripts/esmf/ESMF_regridding.ncl"

begin
    wgt_file  = "wgt_file_wrf_da_wrfdm1.nc"
    src_file  = "wrfdm1_2019080612_2019080812.nc"
    sfile     = addfile(src_file,"r")

	nt        = 0             ; timestep
    var       = sfile->Tair(nt,:,:)
	
    src_lat   = sfile->lat_rho
    src_lon   = sfile->lon_rho
    dimension = dimsizes(src_lat)
    nlat      = dimension(0)
    nlon      = dimension(1)
    minLat    = min(src_lat)     
    maxLat    = max(src_lat)     
    minLon    = min(src_lon)    
    maxLon    = max(src_lon)
    lat       = fspan(minLat,maxLat,nlat)
    lon       = fspan(minLon,maxLon,nlon)

    Opt                   = True
    Opt@InterpMethod      = "bilinear"
    Opt@WgtFileName       = wgt_file
    Opt@RemovePETLog      = True
    Opt@RemoveSrcFile     = True
    Opt@RemoveDstFile     = True
    Opt@SrcGridLat        = src_lat
    Opt@SrcGridLon        = src_lon
    Opt@SrcRegional       = True
    Opt@DstRegional       = True
    Opt@DstGridType       = "rectilinear"
    Opt@DstGridLat        = lat
    Opt@DstGridLon        = lon
    Opt@SrcGridMask       = where(.not.ismissing(var(:,:)),1,0)
    Opt@ForceOverwrite    = True

    var_regrid            = ESMF_regrid(var,Opt)
end