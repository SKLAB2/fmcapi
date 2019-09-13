from .apiclasstemplate import APIClassTemplate
from .accesscontrolpolicy import AccessControlPolicy
from .device import Device
from .prefilterpolicies import PreFilterPolicy
import logging


class HitCount(APIClassTemplate):
    """
    The HitCount Object in the FMC.
    """

    PREFIX_URL = '/policy/accesspolicies'
    REQUIRED_FOR_PUT = ['acp_id']
    REQUIRED_FOR_DELETE = ['acp_id']
    REQUIRED_FOR_GET = ['acp_id']
    VALID_CHARACTERS_FOR_NAME = """[.\w\d_\- ]"""
    FIRST_SUPPORTED_FMC_VERSION = '6.4'

    @property
    def URL_SUFFIX(self):
        """
        Add the URL suffixes for filter.
        """
        filter_init = '?filter="'
        filter = filter_init

        self.URL = self.URL.split('?')[0]

        if self.device_id:
            filter += f'deviceId:{self.device_id};'
        if self.prefilter_ids:
             filter += f'ids:{self.prefilter_ids};'
        if self.fetchZeroHitCount:
            filter += f'fetchZeroHitCount:{self._fetchZeroHitCount};'

        if filter is filter_init:
            filter += '"'
        filter = f'{filter[:-1]}"&expanded=true'

        if 'limit' in self.__dict__:
            filter += f'&limit={self.limit}'
        return filter

    @property
    def fetchZeroHitCount(self):
        return self._fetchZeroHitCount

    @fetchZeroHitCount.setter
    def fetchZeroHitCount(self, value=False):
        self._fetchZeroHitCount = value
        # Rebuild the URL with possible new information
        self.URL = self.URL.split('?')[0]
        self.URL = f'{self.URL}{self.URL_SUFFIX}'

    def __init__(self, fmc, **kwargs):
        logging.debug("In __init__() for HitCount class.")
        self.device_id = None
        self.prefilter_ids = None
        self.fetchZeroHitCount = False
        super().__init__(fmc, **kwargs)
        self.parse_kwargs(**kwargs)
        self.type = 'HitCount'
        self.URL = f'{self.URL}{self.URL_SUFFIX}'

    def parse_kwargs(self, **kwargs):
        super().parse_kwargs(**kwargs)
        logging.debug("In parse_kwargs() for HitCount class.")
        if 'acp_id' in kwargs:
            self.acp(acp_id=kwargs['acp_id'])
        if 'acp_name' in kwargs:
            self.acp(name=kwargs['acp_name'])
        if 'device_id' in kwargs:
            self.device(id=kwargs['device_id'])
        if 'device_name' in kwargs:
            self.device(name=kwargs['device_name'])
        if 'fetchZeroHitCount' in kwargs:
            self.fetchZeroHitCount = kwargs['fetchZeroHitCount']
        if 'limit' in kwargs:
            self.limit = kwargs['limit']
        else:
            self.limit = self.fmc.limit

    def acp(self, name='', acp_id=''):
        # either name or id of the ACP should be given
        logging.debug("In acp() for HitCount class.")
        if acp_id != '':
            self.acp_id = acp_id
            self.URL = f'{self.fmc.configuration_url}{self.PREFIX_URL}/{self.acp_id}/operational/hitcounts'
            self.acp_added_to_url = True
        elif name != '':
            acp1 = AccessControlPolicy(fmc=self.fmc)
            acp1.get(name=name)
            if 'id' in acp1.__dict__:
                self.acp_id = acp1.id
                self.URL = f'{self.fmc.configuration_url}{self.PREFIX_URL}/{self.acp_id}/operational/hitcounts'
                self.acp_added_to_url = True
            else:
                logging.warning(f'Access Control Policy "{name}" not found.  Cannot configure acp for HitCount.')
        else:
            logging.error('No accessPolicy name or id was provided.')
        # Rebuild the URL with possible new information
        self.URL = self.URL.split('?')[0]
        self.URL = f'{self.URL}{self.URL_SUFFIX}'

    def device(self, name='', id=''):
        logging.debug("In device() for HitCount class")
        if id != '':
            self.device_id = id
        elif name != '':
            device1 = Device(fmc=self.fmc)
            device1.get(name=name)
            if 'id' in device1.__dict__:
                self.device_id = device1.id
            else:
                logging.warning(f'Device "{name}" not found.  Cannot configure device for HitCount.')
        else:
            logging.error('No device name or id was provided.')
        # Rebuild the URL with possible new information
        self.URL = self.URL.split('?')[0]
        self.URL = f'{self.URL}{self.URL_SUFFIX}'

    def prefilter_policies(self, action, name='', prefilter_id=''):
        logging.debug("In prefilter_policies_tags() for HitCount class.")
        if action == 'add':
            ppolicy = PreFilterPolicy(fmc=self.fmc)
            if prefilter_id:
                ppolicy.get(id=prefilter_id)
            elif name:
                ppolicy.get(name=name)
            if 'id' in ppolicy.__dict__:
                if self.prefilter_ids:
                    duplicate = False
                    for obj in self.prefilter_ids.split(','):
                        if obj is ppolicy.id:
                            duplicate = True
                            logging.warning(f'Id, {ppolicy.id}, already in prefilter_ids not duplicating.')
                            break
                    if not duplicate:
                        self.prefilter_ids += f',{ppolicy.id}'
                        logging.info(f'Adding "{ppolicy.id}" to prefilter_ids for this HitCount.')
                else:
                    self.prefilter_ids = f'{ppolicy.id}'
                    logging.info(f'Adding "{ppolicy.id}" to prefilter_ids for this HitCount.')
            else:
                if name:
                    logging.warning(f'Prefilter, "{name}", not found.  Cannot add to HitCount.')
                elif prefilter_id:
                    logging.warning(f'Prefilter, {prefilter_id}, not found.  Cannot add to HitCount.')
        elif action == 'remove':
            ppolicy = PreFilterPolicy(fmc=self.fmc)
            if prefilter_id:
                ppolicy.get(id=prefilter_id)
            elif name:
                ppolicy.get(name=name)
            if 'id' in ppolicy.__dict__:
                if self.prefilter_ids:
                    objects = []
                    for obj in self.prefilter_ids.split(','):
                        if obj is not ppolicy.id:
                            objects.append(obj)
                    self.prefilter_ids = ''.join(objects)
                    logging.info(f'Removed "{ppolicy.id}" from prefilter_ids for this HitCount.')
                else:
                    logging.info("prefilter_ids is empty for this HitCount.  Nothing to remove.")
            else:
                logging.warning(f'Prefilter Policy, {ppolicy.id}, not found.  Cannot remove from HitCount.')
        elif action == 'clear':
            if self.prefilter_ids:
                self.prefilter_ids = None
                logging.info('All prefilter_ids removed from this HitCount object.')

        # Rebuild the URL with possible new information
        self.URL = self.URL.split('?')[0]
        self.URL = f'{self.URL}{self.URL_SUFFIX}'

    def get(self, **kwargs):
        """
        Get HitCounts based on filter criteria
        :return:
        """
        logging.debug("In get() for HitCount class.")
        self.parse_kwargs(**kwargs)
        if self.fmc.serverVersion < self.FIRST_SUPPORTED_FMC_VERSION:
            logging.error(f'Your FMC version, {self.fmc.serverVersion} does not support GET of this feature.')
            return {'items': []}
        if self.valid_for_get() and (self.device_id or self.prefilter_ids):
            if self.dry_run:
                logging.info('Dry Run enabled.  Not actually sending to FMC.  Here is what would have been sent:')
                logging.info('\tMethod = GET')
                logging.info(f'\tURL = {self.URL}')
                return False
            response = self.fmc.send_to_api(method='get', url=self.URL)
            self.parse_kwargs(**response)
            if 'items' not in response:
                response['items'] = []
            return response
        else:
            logging.warning("get() method failed due to failure to pass valid_for_get() test.")
            return False

    def post(self):
        logging.info('API POST method for HitCount not supported.')
        pass