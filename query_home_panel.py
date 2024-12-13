from datetime import datetime, timedelta
import pandas as pd
import logging

# Set up logging configuration
logging.basicConfig(filename='/shared/veraset/shared/XIBO/transportation/data_processing.log',
                    level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
                    
### merge the data and get the unique caid ###
final = pd.DataFrame()

for i in range(25,32):
  data = pd.read_csv(r'/shared/veraset/shared/XIBO/transportation/raw_data/trans_2022-08-'+str(i)+'.csv')

  final = pd.concat([final,data],axis=0)
  print('append data in 2022 08 '+str(i)+'...')

print(final.columns)
final = final.groupby('caid')['utc_date'].agg('first').reset_index()
final.to_csv(r'/shared/veraset/shared/XIBO/transportation/cleaned_data/trans_202208_caid.csv',index=False)



caid = pd.read_csv(r'/shared/veraset/shared/XIBO/transportation/cleaned_data/trans_202208_caid.csv')

for y in [2022]:
  for m in [8]:
    df = pd.read_csv(r'/shared/veraset/shared/XIBO/transportation/cleaned_data/trans_'+str(y)+'0'+str(m)+'_caid.csv')
    df['year']=2022
    df['mon']=8
    final = pd.DataFrame()
    for i in range(0,32):
        data = pd.read_csv(r'/shared/veraset/shared/XIBO/migration/cleaned_data/home_panel_stats_v'+str(i)+'.csv')
        print(data.shape)
        data = data.merge(caid.caid.to_frame(), on='caid')
        print(data.shape)
        df2 = df.merge(data, on=['caid','year','mon'])
        final = pd.concat([final,df2],axis=0)
        print('append data in '+str(i)+'th set...')
        logging.info(f'Appended data in {i}th set, current final shape: {final.shape}')
        print(final.shape)
        final.to_csv(r'/shared/veraset/shared/XIBO/transportation/cleaned_data/trans_home_panel_'+str(y)+'0'+str(m)+'.csv',index=False)
