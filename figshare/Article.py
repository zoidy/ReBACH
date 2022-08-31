import json
import math
import sys
import time
import requests
from Log import Log
from Config import Config
import hashlib

class Article:
    api_endpoint = ""
    api_token = ""

    """
    Class constructor.
    Defined requried variables that will be used in whole class.
    """
    def __init__(self):
        self.config_obj = Config()
        figshare_config = self.config_obj.figshare_config()
        self.system_config = self.config_obj.system_config()
        self.api_endpoint = figshare_config["url"]
        self.api_token = figshare_config["token"]
        self.retries = int(figshare_config["retries"]) if figshare_config["retries"] != None else 3
        self.retry_wait = int(figshare_config["retries_wait"]) if figshare_config["retries_wait"] != None else 10
        self.logs = Log()
        self.errors = []

    """
    This function is sending requests to 'account/institution/articles api.
    Static params given for pagination as page, page_size, no_of_pages.
    On successful response from above mentioned API, __get_article_versions will be called with article param. 
    No. of tries implemented in while loop, loop will exit if API is not giving 200 response after no. of tries defined in config file. 
    """
    def get_articles(self):
        articles_api = self.api_endpoint + 'account/institution/articles' if self.api_endpoint[-1] == "/" else self.api_endpoint + "/account/institution/articles"
        retries = 1
        success = False
        while not success and retries <= int(self.retries):
            try:
                # pagination implemented. 
                page = 1
                page_size = 3
                total_articles = 5
                no_of_pages = math.ceil(total_articles / page_size)
                while(page <= no_of_pages):
                    params = {'page': page, 'page_size': page_size}
                    get_response = requests.get(articles_api,
                    headers={'Authorization': 'token '+self.api_token},
                    params=params
                    )
                    if (get_response.status_code == 200):
                        articles = get_response.json()
                        article_data = []
                        for article in articles:
                            if(article['published_date'] != None or article['published_date'] != ''):
                                article_data.append({str(article['id']): self.__get_article_versions(article)})
                        
                        success = True
                        # return article_data
                    else:    
                        retries = self.retries_if_error(f"API is not reachable. Retry {retries}", get_response.status_code, retries)
                        if(retries > self.retries):
                            break
                    page += 1
                    
            except Exception as e:
                retries = self.retries_if_error(e, 500, retries)
                if(retries > self.retries):
                    break
                

    """
    This function will send request to fetch article versions. 
    :param article object. 
    On successful response from '/versions' API, __get_article_metadata_by_version will be called with version param. 
    No. of tries implemented in while loop, loop will exit if API is not giving 200 response after no. of tries defined in config file. 
    """
    def __get_article_versions(self, article):
        retries = 1
        success = False
        while not success and retries <= int(self.retries):
            try:
                if(article):
                    print(article['id'])
                    public_url = article['url_public_api']
                    version_url = public_url + "/versions"
                    get_response = requests.get(version_url)
                    if (get_response.status_code == 200):
                        versions = get_response.json()
                        metadata = []
                        if(len(versions) > 0):
                            for version in versions:
                                version_data = self.__get_article_metadata_by_version(version, article['id'])
                                metadata.append(version_data)
                            success = True
                            return metadata
                        else:
                            self.logs.write_log_in_file("info", f"{article['id']} - Entity not found: ArticleVersion")
                            break
                    else:
                        retries = self.retries_if_error(f"Public verion URL is not reachable. Retry {retries}", get_response.status_code, retries)
                        if(retries > self.retries):
                            break
            except requests.exceptions.RequestException as e:
                retries = self.retries_if_error(e, 500, retries)
                if(retries > self.retries):
                    break

    """
    Fetch article metadata by version url.
    :param version object value. 
    :param article_id int value. 
    On successful response from url_public_api API, metadata array will be setup for response. 
    If files doesn't found and size is > 0 in public API response then private api will be called for files.
    No. of tries implemented in while loop, loop will exit if API is not giving 200 response after no. of tries defined in config file. 
    If files > 0 then __download_files will be called 
    """
    def __get_article_metadata_by_version(self, version, article_id):
        retries = 1
        success = False
        while not success and retries <= int(self.retries):
            try:
                if(version):
                    public_url = version['url']
                    get_response = requests.get(public_url)
                    if (get_response.status_code == 200):
                        version_data = get_response.json()
                        total_file_size = version_data['size']
                        files = []
                        error = ""
                        private_version_no = 0
                        if(total_file_size > 0 and 'files' not in version_data):
                            get_response = requests.get(version_data['url_private_api'], headers={'Authorization': 'token '+self.api_token})
                            file_len = 0
                            if (get_response.status_code == 200):
                                version_data_private = get_response.json()
                                # checking curation_status from article's private api
                                if (version_data_private['curation_status'] == "approved"):
                                    file_len = len(version_data_private['files'])
                                    files = version_data_private['files']
                                    private_version_no = version_data_private['version']
                                    error = f"{version_data['id']} - This item had a file embargo. The files are from version {str(private_version_no)}."
                                    self.logs.write_log_in_file("info", f"{error}", True)
                                else:
                                    error = f"{version_data['id']} - This item’s curation_status was not 'approved'"
                                    self.logs.write_log_in_file("info", f"{error}", True)

                        else:    
                            file_len = len(version_data['files'])
                            files = version_data['files']
                        # item_subtype conditions
                        sub_type = ''
                        if(version_data['has_linked_file']):
                            sub_type = 'linked'
                        elif(version_data['is_metadata_record']):
                            sub_type = 'metadata'
                        else:
                            sub_type = 'regular'
                        
                        version_md5 = ''
                        json_data = json.dumps(version_data).encode("utf-8")
                        version_md5 = hashlib.md5(json_data).hexdigest()

                        version_metadata = {'article_id': article_id, 
                        'metadata': {
                            'item_type': 'article', 'item_subtype': sub_type,'id': version_data['id'], 'version': version['version'], 'first_author': version_data['authors'][0], 'files': files, 
                            'total_num_files': file_len, 'file_size_sum': total_file_size, 'public_url': version_data['url_public_api'],'private_version_no': private_version_no, 'md5': version_md5
                            }
                        }
                        if(error): 
                            version_metadata['errors'] = []
                            version_metadata['errors'].append(error)

                        if(file_len > 0):
                            self.__download_files(files, version_metadata)
                        
                        self.logs.write_log_in_file("info", f"{version_metadata} ")

                        return version_metadata
                    else:
                        retries = self.retries_if_error(f"{article_id} API not reachable. Retry {retries}", get_response.status_code, retries)
                        if(retries > self.retries):
                            break
            except requests.exceptions.RequestException as e:
                retries = self.retries_if_error(f"{e}. Retry {retries}", get_response.status_code, retries)
                if(retries > self.retries):
                    break


    """
    This function will download files and place them in directory, with version_metadata.
    """
    def __download_files(self, files, version_metadata):
        if(len(files) > 0):
            for file in files:
                print(f"Start file downloading....{time.asctime()}")
                print(f"{file['download_url']}")
                print(f"End file downloading....{time.asctime()}")


    """
    Retries function. 
    :param msg 
    :param status_code 
    :param retries
    :return retries
    """
    def retries_if_error(self, msg, status_code, retries):
        self.logs.write_log_in_file("error", f"{msg} - Status code {status_code}", True)
        wait = self.retry_wait
        self.logs.write_log_in_file("error", 'Error! Waiting %s secs and re-trying...' % wait, True)
        sys.stdout.flush()
        time.sleep(wait)
        retries = int(retries) + 1
        return retries