import json
import os
import time

import requests

from django.conf import settings

from .agent import Issuer
# from .agent import convert_seed_to_did

from von_agent.codec import cred_attr_value
from von_agent.util import SchemaKey, cred_def_id
# from von_agent.util import encode
# from von_agent.schemakey import schema_key_for

from . import eventloop, dev, apps

import logging
logger = logging.getLogger(__name__)

# TODO: resolve url via DID -> endpoint
TOB_BASE_URL = os.getenv('THE_ORG_BOOK_API_URL')
TOB_INDY_SEED = os.getenv('TOB_INDY_SEED')


# def claim_value_pair(plain):
#     return [str(plain), encode(plain)]


class SchemaManager():

    # claim_def_json = None

    def __init__(self):
        schemas_path = os.path.abspath(settings.BASE_DIR + '/schemas.json')
        try:
            with open(schemas_path, 'r') as schemas_file:
                schemas_json = schemas_file.read()
        except FileNotFoundError as e:
            logger.error('Could not find schemas.json. Exiting.')
            raise
        self.schemas = json.loads(schemas_json)

        self.__log_json('Schema start', self.schemas)

        # if os.getenv('PYTHON_ENV') == 'development':
        #     for schema in self.schemas:
        #         schema['version'] = dev.get_unique_version()

    def __log_json(self, heading, data):
        logger.debug(
            "\n============================================================================\n" +
            "{0}\n".format(heading) +
            "----------------------------------------------------------------------------\n" +
            "{0}\n".format(json.dumps(data, indent=2)) +
            "============================================================================\n")
        return

    def __log(self, heading, data):
        logger.debug(
            "\n============================================================================\n" +
            "{0}\n".format(heading) +
            "----------------------------------------------------------------------------\n" +
            "{0}\n".format(data) +
            "============================================================================\n")
        return

    def publish_schema(self, schema):
        async def run(schema):
            async with Issuer() as issuer:
                claim_def_json = None

                self.__log('issuer', issuer)
                self.__log('schema', schema)

                # Check if schema exists on ledger
                schema_json = await issuer.get_schema(
                    SchemaKey(
                        origin_did=issuer.did,
                        name=schema['name'],
                        version=schema['version']
                    )
                )

                # If not, send the schema to the ledger, then get result
                if not json.loads(schema_json):
                    schema_json = await issuer.send_schema(json.dumps(schema))

                schema = json.loads(schema_json)

                self.__log_json('schema:', schema)

                # Check if claim definition has been published.
                # If not then publish.
                # claim_def_json = await issuer.get_claim_def(
                #     schema['seqNo'], issuer.did)
                # if not json.loads(claim_def_json):

                claim_def_json = await issuer.send_cred_def(schema_json)

                claim_def = json.loads(claim_def_json)
                self.__log_json('claim_def:', claim_def)

        return eventloop.do(run(schema))

    def submit_claim(self, schema, claim):
        async def run(schema, claim):
            logger.warn("schema_manager.submit_claim() >>> start")
            start_time = time.time()

            # we have a legal_entity_id at this point so we can put everything in a virtual wallet
            # this will stop the nonce from stepping on each other when multi-threading
            organizationId = claim["legal_entity_id"]

            async with Issuer(organizationId) as issuer:
                # claim_def_json = None

                # for key, value in claim.items():
                #     claim[key] = claim_value_pair(value) if value else \
                #         claim_value_pair("")

                self.__log_json('Claim:', claim)
                self.__log_json('Schema:', schema)

                # We need schema from ledger
                elapsed_time = time.time() - start_time
                start_time = time.time()
                logger.warn('Step elapsed time >>> {}'.format(
                    elapsed_time))  # 0.19
                logger.warn(
                    "schema_manager.submit_claim() >>> get schema from ledger")

                schema_json = await issuer.get_schema(
                    SchemaKey(
                        origin_did=issuer.did,
                        name=schema['name'],
                        version=schema['version']
                    )
                )
                schema = json.loads(schema_json)

                self.__log_json('Schema:', schema)

                elapsed_time = time.time() - start_time
                start_time = time.time()
                logger.warn('Step elapsed time >>> {}'.format(
                    elapsed_time))  # 1.00
                logger.warn(
                    "schema_manager.submit_claim() >>> get claim definition")
                claim_def_key = str(schema['seqNo']) + ":" + issuer.did

                claim_def_json = await issuer.get_cred_def(
                    cred_def_id(issuer.did, schema['seqNo']))

                claim_def = json.loads(claim_def_json)

                self.__log_json('Schema:', schema)

                # tob_did = await convert_seed_to_did(TOB_INDY_SEED)
                tob_did = apps.get_tob_did()
                self.__log('TheOrgBook DID:', tob_did)

                # We create a claim offer
                elapsed_time = time.time() - start_time
                start_time = time.time()
                logger.warn('Step elapsed time >>> {}'.format(
                    elapsed_time))  # 1.05
                logger.warn(
                    "schema_manager.submit_claim() >>> create a claim offer")

                claim_offer_json = await issuer.create_cred_offer(schema['seqNo'])
                claim_offer = json.loads(claim_offer_json)

                self.__log_json('Claim Offer:', claim_offer)

                self.__log_json('Requesting Claim Request:',
                                {
                                    'claim_offer': claim_offer,
                                    'claim_def': claim_def
                                })

                elapsed_time = time.time() - start_time
                start_time = time.time()
                logger.warn('Step elapsed time >>> {}'.format(
                    elapsed_time))  # 0.01
                logger.warn("schema_manager.submit_claim() >>> bcovrin generate claim request: " +
                            TOB_BASE_URL + '/bcovrin/generate-claim-request')
                response = requests.post(
                    TOB_BASE_URL + '/bcovrin/generate-claim-request',
                    json={
                        'claim_offer': claim_offer_json,
                        'claim_def': claim_def_json
                    }
                )

                # Build claim
                resp = response.json()

                credential_request = resp['credential_request']
                credential_request_metadata = resp['credential_request_metadata_json']

                claim_request_json = json.dumps(credential_request)
                self.__log_json('Claim Request Json:', credential_request)

                elapsed_time = time.time() - start_time
                start_time = time.time()
                logger.warn('Step elapsed time >>> {}'.format(
                    elapsed_time))  # 1.53
                logger.warn(
                    "schema_manager.submit_claim() >>> issuer create claim")

                (cred_json, _cred_revoc_id, _rev_reg_delta_json) = await issuer.create_cred(
                    claim_offer_json,
                    credential_request,
                    claim)

                self.__log_json('Claim Json:', json.loads(cred_json))

                # Send claim
                elapsed_time = time.time() - start_time
                start_time = time.time()
                logger.warn('Step elapsed time >>> {}'.format(
                    elapsed_time))  # 0.07
                logger.warn(
                    "schema_manager.submit_claim() >>> send claim to bcovrin")
                response = requests.post(
                    TOB_BASE_URL + '/bcovrin/store-claim',
                    json={
                        'claim_type': schema['name'],
                        'claim_data': json.loads(cred_json),
                        'issuer_did': issuer.did,
                        'cred_def': json.loads(claim_def_json),
                        'cred_req_metadata': credential_request_metadata
                    }
                )
                elapsed_time = time.time() - start_time
                start_time = time.time()
                logger.warn('Step elapsed time >>> {}'.format(
                    elapsed_time))  # 0.46
                logger.warn("schema_manager.submit_claim() >>> return")

                return response.json()

        return eventloop.do(run(schema, claim))
