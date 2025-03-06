from .config import UrlConfig, Mobio, lru_redis_cache
import requests


@lru_redis_cache.add()
def get_parent_id_from_merchant(
        merchant_id
):
    from .license_sdk import MobioLicenseSDK
    api_version = MobioLicenseSDK().admin_version
    adm_url = str(UrlConfig.ADMIN_MERCHANT_PARENT).format(
        host=MobioLicenseSDK().admin_host,
        version=api_version,
        merchant_id=merchant_id,
    )
    request_header = {"Authorization": Mobio.MOBIO_TOKEN}
    if MobioLicenseSDK().request_header:
        request_header.update(MobioLicenseSDK().request_header)
    response = requests.get(
        adm_url,
        headers=request_header,
        timeout=MobioLicenseSDK.DEFAULT_REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    data_parent = response.json()
    if data_parent and data_parent.get("data") and len(data_parent.get("data")) > 0:
        root_merchant_id = data_parent.get("data")[0].get("root_merchant_id")
        if root_merchant_id:
            return root_merchant_id
    return merchant_id


@lru_redis_cache.add()
def get_license_attribute_merchant(merchant_id):
    from .license_sdk import MobioLicenseSDK
    api_version = MobioLicenseSDK().admin_version
    adm_url = str(UrlConfig.ADMIN_GET_LICENSE_ATTRIBUTE).format(
        host=MobioLicenseSDK().admin_host,
        version=api_version
    )
    request_header = {"Authorization": Mobio.MOBIO_TOKEN, "x-merchant-id": merchant_id}
    if MobioLicenseSDK().request_header:
        request_header.update(MobioLicenseSDK().request_header)
    response = requests.get(
        adm_url,
        headers=request_header,
        timeout=MobioLicenseSDK.DEFAULT_REQUEST_TIMEOUT_SECONDS,
    )
    json_response = response.json()
    if json_response and json_response.get("data"):
        return json_response.get("data")
    return {}


