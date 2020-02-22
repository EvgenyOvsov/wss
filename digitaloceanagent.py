# Evgeny Ovsov

'''
There is only one function: getting presigned personal temporary link for downloading some file from DigitalOcean Spaces
'''


import boto3
from botocore.client import Config

import config


class DigitalOceanAgent:
    '''
    Agent for getting link to files on DigitalOcean Spaces
    All calls must be made like DigitalOceanAgent.get().somefuction()
    '''

    _instance = None

    @staticmethod
    def get():
        '''
        Something kinda sigleton pattern.
        :return: DigitalOceanAgent()
        '''
        if DigitalOceanAgent._instance is None:
            DigitalOceanAgent._instance = DigitalOceanAgent()
        return DigitalOceanAgent._instance

    def __init__(self):
        self.__agent = boto3.session.Session().client('s3',
                                                      region_name='sfo2',
                                                      endpoint_url='https://sfo2.digitaloceanspaces.com',
                                                      aws_access_key_id=config.DIGITALOCEAN["key"],
                                                      aws_secret_access_key=config.DIGITALOCEAN["secret"],
                                                      config=Config(signature_version='s3'))

    def __str__(self):
        return str(config.DIGITALOCEAN)  # When print directly object of class - print info about connection

    def get_url(self, filename):
        '''
        Return the url to the file. Download will be available for a limited time (wtc cnfg)
        :param filename: *real* name of file on cloud-spaces
        :return: link or None if error
        '''
        try:
            url = self.__agent.generate_presigned_url(ClientMethod='get_object',
                                                      Params={'Bucket': config.DIGITALOCEAN["bucket"],
                                                              'Key': filename},
                                                      ExpiresIn=config.DIGITALOCEAN["link_lifespan"])
            return url
        except Exception:  # This is breaks PEP8, but we can get many different errors,
                            # like not connected, wrong file, wrong key etc
            return None


if __name__ != '__main__':  # when imported
    print(f"DIGITALOCEAN INIT: {DigitalOceanAgent.get()}")  # instantly init agent to detect errors as soon as possible
else:
    print("This module can't be used as independent executable.")
