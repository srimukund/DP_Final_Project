This folder includes Veraset visits to POIs in industry 48 and 49 from 2022-08-25 to 2022-08-31 in the US and 
home location of these visitors during this time period.  

### Primary data: trans_2022-08-** ##
This set of data includes daily device level visits to POIs in NAICS 48-49 during 2022-08-25 to 2022-08-31 in the US
data structure: 'utc_date', 'placekey', 'location_name', 'naics_code', 'street_address', 'city', 'state', 
'census_block_group', 'local_timestamp', 'caid', 'id_type', 'top_category', 'sub_category', 'brands',
 'zip_code', 'minimum_dwell', 'geohash_5'
query code: query_naics48.py

## home location of visitors to these POIs: trans_home_2022-08-** ##
This set of data includes home location (CBG) of each device (caid) if the user visited the above POIs and also observed when the users was at home in a given day. It is worth noting that it is likely that the user are not observed at home but visited the above POIs. In this case, the home location of this user is missing in a given day.
data structure:  'utc_date', 'placekey', 'location_name', 'naics_code', 'street_address', 'city', 'state', 
'census_block_group', 'local_timestamp', 'caid', 'id_type', 'top_category', 'sub_category', 'brands',
 'zip_code', 'minimum_dwell', 'geohash_5'
query code: query_naics48_device.py

## imputed home location of these visitors: trans_home_panel_202208 ##
To address the missing home location during this period, I combine information before and after the study time period and interpolate/extrapolate the home location information of a device depending on the available information. The basic rule is to impute forward. For example, a user was observed at home in 2022-07-01 and 2022-09-01 but not the study period. The home location in 2022-07-01 is CBG A and the same location in 2022-09-01, I assign the home location in the study period to CBG A. If the home locations are different, I assign the location to CBG A, assuming that the user move their home to CBG B in 2022-09-01.
query code: query_home_panel.py








