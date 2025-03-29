import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import os
import requests
import aralia.schema as schema



class AraliaError(Exception):
    """Base class for exceptions in Aralia."""
    pass

class InvalidRequestMethodError(AraliaError):
    """Exception raised for invalid request methods."""
    def __init__(self, method):
        self.message = f"Invalid request method: {method}"
        super().__init__(self.message)

class APIRequestError(AraliaError):
    """Exception raised for API request errors."""
    def __init__(self, status_code, reason):
        self.message = f"HTTP Error {status_code}: {reason}"
        super().__init__(self.message)


class Aralia():
    def __init__(self):
        self.baseurl = os.environ['ARALIA_ENDPOINT']
        self.token = os.environ["ARALIA_TOKEN"] 

    def request(self, method, url, query={}, data_return_direct=False, baseurl=None):
        if baseurl is None:
            baseurl = self.baseurl
        
        method = method.upper()
        if method not in ["GET","POST"]:
            raise InvalidRequestMethodError(method)
        
        # Define the Authorization header
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            # Send the request
            if method == "GET":
                response = requests.get(baseurl + url, headers=headers, params=query, timeout=10)
            elif method == "POST":
                response = requests.post(baseurl + url, headers=headers, json=query, timeout=10)
            
            if not response.ok:
                raise APIRequestError(response.status_code, response.reason)
             
            # Return the desired portion of the response
            if data_return_direct:
                return response.json()  # Return the full JSON response
            data = response.json().get("data")
            return data if data.get("list") is None else data.get("list")
        except requests.exceptions.Timeout:
            raise TimeoutError("Request timed out.")
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Connection error occurred.")
        except requests.exceptions.RequestException as e:
            raise AraliaError(f"An unexpected error occurred: {e}")
          
    def SearchDatasets(self,keyword: str):
        try:
            response = self.request(
                "GET",
                "/galaxy/dataset", 
                {"keyword": keyword,"pageSize": 10}
            )
        except AraliaError as e:
            raise AraliaError(f"Error searching datasets for keyword '{keyword}': {e}")

        for item in response:
            item['sourceURL'], _, _ = item['sourceURL'].partition('/admin')
            item['sourceURL'] += '/api'
        return response
    
    def GetColumnInfo(self,dataset: schema.Dataset):
        try:
            response = self.request(
                "GET",
                "/dataset/" + dataset['id'], baseurl=dataset['sourceURL']
            )
        except AraliaError as e:
            raise AraliaError(f"Error getting column info for dataset '{dataset['name']}': {e}")
    
        return response['columns']

    def XAxisValidation(self, x: schema.XAxis, columns: list[schema.Column]):
        for c in columns:
            if x['columnID'] == c['id']:
                if x['column_name'] != c['name']:
                    return {"status": "fail", "message": f"XAxis column_name '{x['column_name']}' does not match with columnID '{x['columnID']}' in dataset."}
                if x['type'] != c['type']:
                    return {"status": "fail", "message": f"XAxis type '{x['type']}' for column '{x['column_name']}' does not match expected type '{c['type']}' in dataset."}
                if x.get("country") and x['country'] not in ["Taiwan"]:
                    return {"status": "fail", "message": f"XAxis country '{x['country']}' is invalid. Expected 'Taiwan'."}
                if x['language'] not in ["zh-tw", "zh-cn", "en"]:
                    return {"status": "fail", "message": f"XAxis language '{x['language']}' is invalid. Expected one of ['zh-tw', 'zh-cn', 'en']."}
                if x['type'] in ["date", "datetime"] and x["format"] not in ["year", "quarter", "month", "week", "date", "day", "weekday", "year_month", "year_quarter", "year_week", "month_day", "day_hour", "hour", "minute", "second", "hour_minute", "time"]:
                    return {"status": "fail", "message": f"XAxis format '{x['format']}' is invalid for type '{x['type']}'. Expected one of ['year', 'quarter', 'month', 'week', ...]."}
                if x['type'] == "space" and x["format"] not in schema.admin_level[x['country']][x['language']]:
                    return {"status": "fail", "message": f"XAxis format '{x['format']}' is not valid based on admin_level for country '{x['country']}' and language '{x['language']}'."}
                return {"status": "success"}
        return {"status": "fail", "message": f"XAxis columnID '{x['columnID']}' not found in dataset columns."}


    def YAxisValidation(self, y: schema.YAxis, columns: list[schema.Column]):
        for c in columns:
            if y['columnID'] == c['id']:
                if y['column_name'] != c['name']:
                    return {"status": "fail", "message": f"YAxis column_name '{y['column_name']}' does not match with columnID '{y['columnID']}' in dataset."}
                if y['type'] != c['type']:
                    return {"status": "fail", "message": f"YAxis type '{y['type']}' for column '{y['column_name']}' does not match expected type '{c['type']}' in dataset."}
                if y["calculation"] not in ["count", "sum", "avg", "min", "max", "distinct_count"]:
                    return {"status": "fail", "message": f"YAxis calculation '{y['calculation']}' is invalid. Expected one of ['count', 'sum', 'avg', 'min', 'max', 'distinct_count']."}
                if y['type'] in ["nominal", "ordinal"] and y["calculation"] not in ["count", "distinct_count"]:
                    return {"status": "fail", "message": f"YAxis calculation '{y['calculation']}' is not valid for type '{y['type']}'. Expected one of ['count', 'distinct_count']."}
                if y['type'] in ["date", "datetime"] and y["calculation"] not in ["count", "min", "max", "distinct_count"]:
                    return {"status": "fail", "message": f"YAxis calculation '{y['calculation']}' is not valid for type '{y['type']}'. Expected one of ['count', 'min', 'max', 'distinct_count']."}
                return {"status": "success"}
        return {"status": "fail", "message": f"YAxis columnID '{y['columnID']}' not found in dataset columns."}


    def QueryValidation(self, query: schema.Query, dataset: list[schema.Dataset]):
        for d in dataset:
            if query['dataset_id'] == d['id']:
                if query['sourceURL'] != d['sourceURL']:
                    return {"status": "fail", "message": f"Query sourceURL '{query['sourceURL']}' does not match dataset sourceURL '{d['sourceURL']}'."}
                
                if query['dataset_name'] != d['name']:
                    return {"status": "fail", "message": f"Query dataset_name '{query['dataset_name']}' does not match dataset name '{d['name']}'."}
                
                for x in query['x']:
                    x_valid = self.XAxisValidation(x, d['columns'])
                    if x_valid['status'] == "fail":
                        return x_valid
                for y in query['y']:
                    y_valid = self.YAxisValidation(y, d['columns'])
                    if y_valid['status'] == "fail":
                        return y_valid
                return {"status": "success"}

        return {"status": "fail", "message": f"Dataset with ID '{query['dataset_id']}' not found in provided datasets."}

       

    def QueryPlanet(self, query: schema.Query):
        start = 1
        total_response = []
        try:
            while True:
                url = f"/exploration/{query['dataset_id']}?start={start}"
                response = self.request(
                    "POST",
                    url,
                    query,
                    baseurl=query['sourceURL']
                )
                total_response.extend(response)
                if len(response) == 1000:
                    if start > 10000:
                        break
                    else:
                        start += 1000
                else:
                    break
        except AraliaError as e:
            raise AraliaError(f"Error in QueryPlanet for dataset '{query['dataset_name']}': {e}")


        x_cols = [x_axis['column_name'] for x_axis in query['x']]
        y_cols = [y_axis['column_name'] for y_axis in query['y']]

        result = {
            "dataset_name": query['dataset_name'],
            "x": ','.join(x_cols),
            "y": ','.join(y_cols),
            "charts_data": total_response[-500:]
        }
        return result



if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv("../.env")
    aralia = Aralia()
    
    # Test the SearchDatasets method
    print("Testing SearchDatasets method...")
    result = aralia.SearchDatasets(["空氣品質","空污"])
    print(result)

    # Test the GetColumnInfo method
    print("Testing GetColumnInfo method...")
    dataset = {'id': 'dnT3tXLZuxggmFdXGFLpHt',
               'name': '每小時空氣品質監測',
               'description': '此數據集記錄自2023年10月起全台各測站每小時空氣數據，涵蓋多項空氣品質指標與基本氣象參數。',
               'sourceType': 'x_planet',
               'siteName': '生活空氣指南星球',
               'sourceURL': 'https://tw-air.araliadata.io/api'}
    columns = aralia.GetColumnInfo(dataset)
    print(columns)


    # Test the QueryPlanet method
    print("Testing QueryPlanet method...")
    query = {"sourceURL": "https://tw-entertainment.araliadata.io/api",
   "dataset_id": "6h7D2wyfsxx6BUadPAyxHp",
   "dataset_name": "電影票房資料",
   "x": [{"columnID": "4dPMMB7EdpRRd4iUqqFev9",
     "column_name": "製作國家",
     "type": "nominal",
     "country": "Taiwan",
     "language": "zh-tw"}],
   "y": [{"columnID": "dToiKESLfXpqJTmqS5AjwE",
     "column_name": "銷售金額",
     "type": "float",
     "calculation": "avg"}]}
    result = aralia.QueryPlanet(query)
    print(result)
