from processing.module import AbsoluteSalinity, Module
from processing.utils import default_seabird_exe_path

mapper = {
    "abs_sal": AbsoluteSalinity,
}


def map_proc_name_to_class(module: str) -> type[Module]:
    """
    Sets and maps the known processing modules to their respective
    module classes.

    Parameters
    ----------
    module: str :
        Name of the module, that is being used inside the config.

    Returns
    -------

    """
    return mapper[module.lower()]


def get_list_of_installed_seabird_modules() -> list["str"]:
    seabird_path = default_seabird_exe_path()
    return [str(file.stem)[:-1] for file in seabird_path.glob("*W.exe")]


def get_list_of_available_processing_modules() -> list["str"]:
    proc_list = [*get_list_of_installed_seabird_modules(), *list(mapper.keys())]
    proc_list.sort()
    return proc_list
