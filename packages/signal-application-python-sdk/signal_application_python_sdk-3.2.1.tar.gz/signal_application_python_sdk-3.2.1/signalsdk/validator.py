import logging


def throw_if_parameter_not_found_in(value, param, location, customException=None):
    """validate parameter existence in location
    """
    if not value:
        error_message = f"signalsdk::Application SDK can not start " \
                        f"because {param} is not found in {location}"
        logging.info(error_message)
        if customException:
            raise customException
        raise Exception(error_message)
