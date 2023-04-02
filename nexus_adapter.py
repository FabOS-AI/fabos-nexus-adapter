import os
from nexus_assets import *
from slm_client import *
from pathlib import Path
from typing import Dict


def isModelFile(asset: NexusAsset, filetype: str, contentType: str = 'application/x-tar'):
    return (filetype in asset.path) and (asset.contentType == contentType)


def replace_service_option_by_key(service_offering_version: Dict, option_key: str, option_value: any):

    found = False
    
    for optionCategory in service_offering_version['serviceOptionCategories']:
        for option in optionCategory['serviceOptions']:
            if option['key'] == option_key:
                option['valueOptions'] = option_value
                print(f"replaced option '{option['key']}' with '{str(option['valueOptions'])[:80] + '...'}'")
                option['valueType'] = 'ENUM'
                option['defaultValue'] =  option_value[0] if isinstance(option_value, list) else option_value
                print(f"option '{option['key']}' set defaultValue to '{option['defaultValue']}'")
                found = True

    if not found:
        print("WARNING: option could not be replaced...")
        return False

    return service_offering_version


def do_update():

    config = dict()

    config['NEXUS_URL'] = os.environ.get('NEXUS_URL')
    config['NEXUS_USER'] = os.environ.get('NEXUS_USER')
    config['NEXUS_PASSWORD'] = os.environ.get('NEXUS_PASSWORD')
    config['MODEL_FILETYPE'] = os.environ.get('MODEL_FILETYPE')
    config['SLM_HOST'] = os.environ.get('SLM_HOST', 'http://localhost')
    config['SLM_KEYCLOAK_HOST'] = os.environ.get("SLM_KEYCLOAK_HOST", f"{config['SLM_HOST']}:7080")
    config['SLM_SERVICE_REGISTRY_HOST'] = os.environ.get("SLM_SERVICE_REGISTRY_HOST", f"{config['SLM_HOST']}:9020")
    config['SLM_USER'] = os.environ.get('SLM_USER')
    config['SLM_PASSWORD'] = os.environ.get('SLM_PASSWORD')
    config['SLM_OFFERING_UUID'] = os.environ.get('SLM_OFFERING_UUID')
    config['SLM_OFFERING_VERSION_UUID'] = os.environ.get('SLM_OFFERING_VERSION_UUID')
    config['SLM_OFFERING_VERSION_OPTION_KEY'] = os.environ.get('SLM_OFFERING_VERSION_OPTION_KEY')

    print(f"loaded config: {config}")

    # catch assets
    assets = RemoteAssets(
        config={
        "download_url":"",
        "search_url": config['NEXUS_URL']
        },
        nexus_auth={
            "username": config['NEXUS_USER'],
            "password": config['NEXUS_PASSWORD']
        },
        include_metadata_files=False,
        update_on_init=True
    )

    # filter for models
    asset_paths_filtered = [Path(asset.path).stem for asset in assets if isModelFile(asset, filetype=config['MODEL_FILETYPE'])]
    print(f"found '{len(asset_paths_filtered)}' model options")


    slm = slmClient(
        host=config['SLM_HOST'],
        host_keycloak=config['SLM_KEYCLOAK_HOST'],
        host_resource_registry=config['SLM_HOST'],
        host_service_registry=config['SLM_SERVICE_REGISTRY_HOST'],
        slm_user=config['SLM_USER'],
        slm_password=config['SLM_PASSWORD']
    )

    service_offering_version = slm.get_service_offering_version(
        offering_id=config['SLM_OFFERING_UUID'], 
        offering_version_id=config['SLM_OFFERING_VERSION_UUID']
    )

    if replace_service_option_by_key(
        service_offering_version=service_offering_version,
        option_key=config['SLM_OFFERING_VERSION_OPTION_KEY'],
        option_value=asset_paths_filtered
    ):

        res = slm.update_service_offering_version(
            offering_version=service_offering_version
        )
    else:
        print("WARNING: offering was not updated ...")