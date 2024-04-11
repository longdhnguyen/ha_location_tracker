import json
import pymysql

from geopy.distance import geodesic

class LocationManager:
    def __init__(self, mysql_host, mysql_user,  mysql_password, mysql_db):
        self.connection = pymysql.connect(
            host=mysql_host,
            user=mysql_user, 
            password=mysql_password, 
            database=mysql_db
        )

    def retrieve_location_data(self, entity_id, from_timestamp=0):
        cursor = self.connection.cursor()

        sql = f"""
            SELECT 
                ROUND(last_updated_ts) AS timestamp, 
                json_extract(sa.shared_attrs, "$.latitude") AS latitude, 
                json_extract(sa.shared_attrs, "$.longitude") AS longitude 
            FROM `states` 
            INNER JOIN state_attributes sa USING(attributes_id)
            LEFT JOIN states_meta sm USING(metadata_id) 
            WHERE sm.entity_id = '{entity_id}'
                AND ROUND(last_updated_ts) > {from_timestamp}
            ORDER BY 1 DESC;
        """
        cursor.execute(sql)
        return [{
            "timestamp": row[0], 
            "latitude": row[1], 
            "longitude": row[2]
        } for row in cursor.fetchall()]
        
    def point_history(self, entity_id, latitude, longitude, threshold_miles):
        location_data = self.retrieve_location_data(entity_id)
        reference_point = (float(latitude), float(longitude), )

        # Filter the data down to threshold_miles:
        filtered_rows = []
        for row in location_data:
            if not (row['latitude'] and row['longitude']):
                continue
            current_point = (float(row['latitude']), float(row['longitude']), )
            distance = geodesic(reference_point, current_point).miles
            if distance < threshold_miles:
                row['distance'] = distance
                filtered_rows.append(row)

        return filtered_rows