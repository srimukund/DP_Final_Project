
import csv
import psycopg2
from psycopg2 import sql
from datetime import datetime, timedelta

# Replace these values with your actual database credentials
DB_NAME = "dfsasuconn"
USER = "naics_unique_loc"
PASSWORD = "naicsUniqueLoc"
HOST = "dsfasuconn01.engr.uconn.edu"
PORT = "5432"

def connect_to_database():
    try:
        connection = psycopg2.connect(
            dbname=DB_NAME,
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT
        )
        return connection
    except Exception as e:
        print(f"Error: Unable to connect to the database - {e}")
        return None

def query_and_write_to_csv(connection, partition_name, csv_writer):
    query = sql.SQL("""
    SELECT utc_date, placekey, location_name, naics_code, street_address, city, state, census_block_group, local_timestamp, A.caid, id_type, top_category, sub_category, brands, zip_code, minimum_dwell, geohash_5
    FROM {} A
    JOIN (
        SELECT DISTINCT caid
        FROM {}
        WHERE CAST(naics_code AS VARCHAR) LIKE '48%' OR 
          CAST(naics_code AS VARCHAR) LIKE '49%'   
    ) B ON A.caid = B.caid
    WHERE location_name = 'home'  
        """).format(sql.SQL(partition_name),sql.SQL(partition_name))

    with connection.cursor() as cursor:
        cursor.execute(query)

        rows = cursor.fetchall()
        for row in rows:
            csv_writer.writerow(row)

def main():
    connection = connect_to_database()
    if connection:
      # Generate the list of year-month pairs
        for y in [2022]:
            for m in [8]:
                
                if m<12:
                    start_date = datetime(y, m, 25).strftime("%Y-%m-%d")
                    end_date = datetime(y, m, 31).strftime("%Y-%m-%d")
                    #end_date = end_date.replace(day=1).strftime("%Y-%m-%d")
                    
                    print(start_date) 
                    print(end_date) 
                    while start_date <= end_date:
                        CSV_FILE = "/shared/veraset/shared/XIBO/transportation/raw_data/trans_home_"+start_date+".csv"
                        with open(CSV_FILE, mode='w', newline='') as csv_file:
                            csv_writer = csv.writer(csv_file)
                            csv_writer.writerow(['utc_date', 'placekey', 'location_name', 'naics_code', 'street_address', 'city', 'state',
                                  'census_block_group', 'local_timestamp', 'caid', 'id_type', 'top_category', 'sub_category', 'brands',
                                   'zip_code', 'minimum_dwell', 'geohash_5'])
                            partition_name = f'partitioned_data."partitioned_data.rawdata_partitioned_p{start_date.replace("-", "_")}"'
                            print(f"Querying for {partition_name}")
                            query_and_write_to_csv(connection, partition_name, csv_writer)
                            # Move to the next date
                            print('finished query in '+start_date+'...')
                            # Define the target CSV file  
                            
    
                        start_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
                else:
                    start_date = datetime(y, m, 1).strftime("%Y-%m-%d")
                    end_date = datetime(y, m, 31).strftime("%Y-%m-%d")
                
                    print(start_date) 
                    print(end_date) 
                    while start_date <= end_date:
                        CSV_FILE = "/shared/veraset/shared/XIBO/transportation/raw_data/trans_home_"+start_date+".csv"
                        with open(CSV_FILE, mode='w', newline='') as csv_file:
                            csv_writer = csv.writer(csv_file)
                            csv_writer.writerow(['utc_date', 'placekey', 'location_name', 'naics_code', 'street_address', 'city', 'state',
                                  'census_block_group', 'local_timestamp', 'caid', 'id_type', 'top_category', 'sub_category', 'brands',
                                   'zip_code', 'minimum_dwell', 'geohash_5','home_cbg'])
                            partition_name = f'partitioned_data."partitioned_data.rawdata_partitioned_p{start_date.replace("-", "_")}"'
                            print(f"Querying for {partition_name}")
                            query_and_write_to_csv(connection, partition_name, csv_writer)
                            # Move to the next date
                            print('finished query in '+start_date+'...')
                            
                        start_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
                        
    connection.close()

if __name__ == "__main__":
    main()
