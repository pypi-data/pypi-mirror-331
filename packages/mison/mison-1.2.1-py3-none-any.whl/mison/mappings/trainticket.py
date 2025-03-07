import os


def component_mapping(filename):
    if filename is None:
        return None
    service = str(filename).split(os.sep)[1]
    if service.startswith('ts-') and "service" in service:
        return service
    else:
        return None