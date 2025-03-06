from .call_api import get_license_attribute_merchant

class Utils:

    @staticmethod
    def get_attribute_license_by_key(merchant_id, attribute_key):
        try:
            data = get_license_attribute_merchant(merchant_id)
            if data and attribute_key in data:
                return data[attribute_key]
        except Exception as e:
            print("get_attribute_license_by_key ERR: {}".format(e))
        return None
